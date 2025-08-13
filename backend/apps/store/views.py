from rest_framework import generics, permissions, status
import stripe
from django.conf import settings
from backend.apps.account.models import Account
from backend.apps.category.models import Category
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from datetime import datetime

from backend.apps.store.models import Subscription, PaymentHistory
from backend.apps.customuser.models import CustomUser
from backend.apps.space.models import Space
from backend.apps.total_balance.models import TotalBalance
from decimal import Decimal


class SubscribePricesView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        data = settings.SUBSCRIBES_DATA
        result = {}
        for subscribe in data:
            for sub_data in data[subscribe]:
                result[f"{subscribe.lower()}_{sub_data}"] = data[subscribe][sub_data]
        return Response(result, status=status.HTTP_200_OK)


class CreatePaymentSessionView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        print("Stripe key:", stripe.api_key)
        user = request.user
        plan = request.data.get('plan')  # business_plan или business_license
        period = request.data.get('period')  # monthly, quarterly, semiannually, yearly
        count = request.data.get('count', 1)
        
        # Проверяем, что план входит в допустимые значения
        valid_plans = ['business_plan', 'business_license']
        if plan not in valid_plans:
            return Response(
                {"error": f"Plan must be one of: {', '.join(valid_plans)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        # Проверяем, что передан и план, и период
        if not plan or not period:
            return Response(
                {"error": "Both plan and period are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Формируем ключ для получения price_id из настроек
        price_key = f"STRIPE_{plan.upper()}_{period.upper()}_PRICE_ID"
        
        # Проверяем, существует ли соответствующее поле в settings
        if not hasattr(settings, price_key):
            return Response(
                {"error": f"Price not configured for {plan} {period} in settings."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Получаем ID цены для плана и периода
            price_id = getattr(settings, price_key)

            # Создаем Stripe Customer, если его еще нет
            existing_customers = stripe.Customer.list(email=user.email).data

            if existing_customers:
                customer = existing_customers[0]
                print(f"Existing customer found: {customer['id']}")
            else:
                customer = stripe.Customer.create(
                    email=user.email,
                    metadata={"user_id": user.id},
                )
                print(f"New customer created: {customer['id']}")

            # Настройки для подписки с trial period
            subscription_data = {
                'trial_settings': {
                    'end_behavior': {
                        'missing_payment_method': 'cancel'
                    }
                },
                'trial_period_days': 14  # 14-day free trial
            }

            # Создаем Checkout Session
            checkout_session = stripe.checkout.Session.create(
                customer=customer.id,
                payment_method_types=["card"],
                line_items=[{
                    "price": price_id,
                    "quantity": count,
                }],
                mode="subscription",
                subscription_data=subscription_data,
                success_url=f"{settings.FRONTEND_URL}/shop/success",
                cancel_url=f"{settings.FRONTEND_URL}/cancel",
                locale="cs",
                metadata={
                    "plan": plan,
                    "period": period,
                    "user_id": str(user.id),
                },
            )
            print(checkout_session)

            return Response({"session_id": checkout_session.id}, status=status.HTTP_200_OK)
        except Exception as e:
            print("error", str(e))
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class WebhookAPIView(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')
        webhook_secret = settings.STRIPE_WEBHOOK_SECRET

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
            print(event)
        except ValueError as e:
            print("error", e)
            return Response({"error": "Invalid payload"}, status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError as e:
            print("error", e)
            return Response({"error": "Invalid signature"}, status=status.HTTP_400_BAD_REQUEST)

        # Обработка разных типов событий
        if event['type'] == 'checkout.session.completed':
            self.handle_checkout_session_completed(event)
        elif event['type'] == 'invoice.paid':
            self.handle_invoice_paid(event)
        elif event['type'] == 'invoice.payment_failed':
            self.handle_invoice_payment_failed(event)

        return Response(status=status.HTTP_200_OK)

    def handle_checkout_session_completed(self, event):
        """Обработка завершения checkout (начало подписки)"""
        session = event['data']['object']
        
        if session.mode != 'subscription':
            return

        try:
            # Получаем данные из metadata или customer_details
            user_id = session.get('metadata', {}).get('user_id')
            plan = session.get('metadata', {}).get('plan')
            period = session.get('metadata', {}).get('period')
            stripe_customer_id = session.get('customer')
            subscription_id = session.get('subscription')

            # Пытаемся найти пользователя по ID или email
            if user_id:
                user = CustomUser.objects.get(id=user_id)
            else:
                user_email = session['customer_details']['email']
                user = CustomUser.objects.get(email=user_email)

            # Создаем или обновляем подписку (убираем поля, которых нет в модели)
            subscription, created = Subscription.objects.update_or_create(
                user=user,
                stripe_user=stripe_customer_id,
                stripe_subscription_id=subscription_id,
                plan=plan,
                period=period,
            )

            # Обрабатываем Space для пользователя
            self.handle_user_space(user, plan)

            # Обновляем роль пользователя
            if hasattr(user, 'roles'):
                user.roles = [plan]
                user.save()
                
            print(f"Subscription {subscription_id} {'created' if created else 'updated'} for user {user.email}")

        except CustomUser.DoesNotExist:
            print(f"Error: User not found")
        except Exception as e:
            print(f"Error handling checkout.session.completed: {str(e)}")

    def handle_invoice_paid(self, event):
        """Обработка успешного платежа"""
        invoice = event['data']['object']
        
        # Исправленное получение subscription_id
        subscription_id = None
        if invoice.get('parent') and invoice['parent'].get('subscription_details'):
            subscription_id = invoice['parent']['subscription_details'].get('subscription')
        
        if not subscription_id:
            print("No subscription ID found in invoice")
            return
            
        amount = Decimal(invoice['amount_paid'] / 100) if invoice['amount_paid'] else 0
        
        try:
            subscription = Subscription.objects.get(stripe_subscription_id=subscription_id)
            subscription.is_active = True
            subscription.save()

            # Находим space пользователя для записи платежа
            user_spaces = Space.objects.filter(members=subscription.user)
            
            if user_spaces.exists():
                # Берем первый найденный space или space с members_slots
                space = user_spaces.filter(members_slots__isnull=False).first() or user_spaces.first()
                
                PaymentHistory.objects.create(
                    father_space=space,
                    amount=amount,
                    payment_category="subscription",
                )
                print(f"Payment recorded for subscription {subscription_id}, amount: {amount}")
            else:
                print(f"No space found for user {subscription.user.email}")

        except Subscription.DoesNotExist:
            print(f"Subscription {subscription_id} not found in database")
        except Exception as e:
            print(f"Error processing invoice.paid: {str(e)}")

    def handle_invoice_payment_failed(self, event):
        """Обработка неудачного платежа"""
        invoice = event['data']['object']
        
        # Исправленное получение subscription_id
        subscription_id = None
        if invoice.get('parent') and invoice['parent'].get('subscription_details'):
            subscription_id = invoice['parent']['subscription_details'].get('subscription')
        
        if not subscription_id:
            print("No subscription ID found in invoice")
            return

        try:
            # Получаем подписку из Stripe для проверки статуса
            stripe_sub = stripe.Subscription.retrieve(subscription_id)
            
            # Обновляем подписку в базе данных
            subscription = Subscription.objects.get(stripe_subscription_id=subscription_id)
            
            # Если подписка в Stripe отменена или unpaid, деактивируем
            if stripe_sub.status in ['canceled', 'unpaid', 'past_due']:
                subscription.is_active = False
                subscription.save()
                print(f"Subscription {subscription_id} deactivated due to payment failure")
            else:
                print(f"Payment failed for {subscription_id}, but subscription is still active")

        except Subscription.DoesNotExist:
            print(f"Subscription {subscription_id} not found in database")
        except Exception as e:
            print(f"Error processing invoice.payment_failed for {subscription_id}: {str(e)}")

    def handle_user_space(self, user, plan):
        """Создает или обновляет Space для пользователя"""
        try:
            existing_spaces = Space.objects.filter(members=user)
            
            if not existing_spaces.exists():
                print(f"No space found for user {user.email}")
                return

            slots = 10 

            # Получаем валюту из существующего space
            first_space = existing_spaces.first()
            currency = first_space.currency

            if existing_spaces.count() == 1:
                # Создаем новый space для бизнес-плана
                space = Space.objects.create(
                    title=f"{user.username} - {plan}",
                    currency=currency,
                    members_slots=Decimal(slots) 
                )
                space.members.add(user)

                # Создаем стандартные категории и аккаунт
                self.create_default_categories(space)
                self.create_default_account(space, currency)

            elif existing_spaces.count() > 1:
                # Обновляем существующий business space
                space = existing_spaces[1]
                if hasattr(space, 'members_slots'):
                    current_slots = space.members_slots or Decimal(0)
                    space.members_slots = current_slots + Decimal(slots)
                    space.save()

            PaymentHistory.objects.create(
                father_space=space,
                amount=Decimal(0),
                payment_category="service",
            )

        except Exception as e:
            print(f"Error handling user space: {str(e)}")

    def create_default_categories(self, space):
        """Создает стандартные категории для нового space"""
        try:
            Category.objects.create(
                title="Vývoj",
                limit=1000,
                spent=0,
                father_space=space,
                color="#FF9800",
                icon="Hand_Money"
            )
            Category.objects.create(
                title="Platy",
                spent=0,
                father_space=space,
                color="#FF5050",
                icon="Laptop"
            )
        except Exception as e:
            print(f"Error creating default categories: {str(e)}")

    def create_default_account(self, space, currency):
        """Создает стандартный аккаунт для нового space"""
        try:
            Account.objects.create(
                title="Hotovost",
                balance=0,
                currency=currency,
                father_space=space
            )
            TotalBalance.objects.create(balance=0, father_space=space)
        except Exception as e:
            print(f"Error creating default account: {str(e)}")


class SubscribeCancel(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        user = request.user

        # Проверка роли business_lic
        if 'business_lic' in user.roles:
            return Response(
                {"error": "Cannot cancel subscription for business_lic role."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Найти активную подписку пользователя
            subscription = Subscription.objects.filter(user=user, is_active=True).first()
            if not subscription:
                return Response({"error": "No active subscription found"}, status=status.HTTP_404_NOT_FOUND)

            # Немедленно отменить подписку в Stripe
            stripe.Subscription.delete(subscription.stripe_subscription_id)

            # Обновить статус подписки в базе данных
            subscription.is_active = False
            subscription.save()

            existing_project = Space.objects.filter(members=user, members_slots__isnull=False).first()
            if existing_project:
                # Меняем роль у всех членов существующего Space
                for member in existing_project.members.all():
                    if any(role in member.roles for role in ['business_member_plan', 'business_member_lic', 'business_lic', 'business_plan']):
                        member.roles = ['free']
                        member.save()

                # Устанавливаем members_slots в None
                existing_project.members_slots = None
                existing_project.save()

            return Response(
                {"message": "Subscription has been cancelled immediately."},
                status=status.HTTP_200_OK
            )
        except stripe.error.StripeError as e:
            print("error", str(e))
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print("error", "An error occurred: " + str(e))
            return Response({"error": "An error occurred: " + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class WebhookAPIView(generics.GenericAPIView):
#     permission_classes = (permissions.AllowAny,)

#     def post(self, request):
#         payload = request.body
#         sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')
#         webhook_secret = settings.STRIPE_WEBHOOK_SECRET

#         try:
#             event = stripe.Webhook.construct_event(
#                 payload, sig_header, webhook_secret
#             )
#         except ValueError as e:
#             print("error", "Invalid payload")
#             return Response({"error": "Invalid payload"}, status=status.HTTP_400_BAD_REQUEST)
#         except stripe.error.SignatureVerificationError as e:
#             print("error", "Invalid signature")
#             return Response({"error": "Invalid signature"}, status=status.HTTP_400_BAD_REQUEST)

#         # Обработка события
#         if event['type'] == 'checkout.session.completed':
#             print("Payment successful.")

#             # Получаем нужные переменные из события
#             session = event['data']['object']
#             user_email = session['customer_details']['email']
#             mode = session.get('mode')
#             description = session.get('metadata', {}).get('description')
#             print(description)
#             stripe_user = session.get('customer')
#             print("adfadf", mode, stripe_user)

#             try:
#                 user = CustomUser.objects.get(email=user_email)
#             except CustomUser.DoesNotExist:
#                 print("error", "User not found")
#                 return Response({"error": "User not found"}, status=status.HTTP_400_BAD_REQUEST)
#             # Остальная логика создания Space, ролей и категорий
#             # Ищем первую запись Space, где есть этот пользователь в members
#             try:
#                 existing_space = Space.objects.filter(members=user).first()
#                 if not existing_space:
#                     print("error", "No space found for this user")
#                     return Response({"error": "No space found for this user"}, status=status.HTTP_400_BAD_REQUEST)
#             except Space.DoesNotExist:
#                 print("error", "Space model not found")
#                 return Response({"error": "Space model not found"}, status=status.HTTP_400_BAD_REQUEST)

#             # Получаем валюту из найденной записи
#             currency = existing_space.currency

#             # Создаем новый объект Space
#             existing_spaces = Space.objects.filter(members=user)

#             # Сохраняем подписку в модели Subscription
#             if mode == "subscription":
#                 # Обработка подписки
#                 subscription_id = session.get('subscription')
#                 slots = 10
#                 plan="business_plan"
#                 amount = session.get('amount_total')
#                 amount = amount / 100
#                 payment_category="subscription"
#                 print("Products purchased:", subscription_id, amount, slots, payment_category)
#             elif mode == "payment":
#                 if description == "premium":
#                     # Обработка обычной покупки
#                     plan="business_lic"
#                     subscription_id = session.get('payment_intent')
#                     amount = session.get('amount_total')
#                     amount = amount / 100
#                     slots = amount / 500
#                     payment_category="license"
#                     print("Products purchased:", subscription_id, amount, slots, payment_category)
#                 elif description == "add_license":
#                     # Обработка обычной покупки
#                     plan="business_lic"
#                     subscription_id = session.get('payment_intent')
#                     amount = session.get('amount_total')
#                     amount = amount / 100
#                     slots = amount / 500
#                     payment_category="license"
#                     print("Products purchased:", subscription_id, amount, slots, payment_category)
#                 elif description == "service":
#                     # Обработка обычной покупки
#                     plan="business_lic"
#                     subscription_id = session.get('payment_intent')
#                     amount = session.get('amount_total')
#                     amount = amount / 100
#                     payment_category="service"
#                     print("Products purchased:", subscription_id, amount, payment_category)
#             print(existing_spaces.count())
#             if description != "service":
#                 if existing_spaces.count() == 1:
#                     print("one")
#                     # Создаём новый объект, так как существует только один такой объект
#                     space = Space.objects.create(
#                         title=user.username,
#                         currency=currency,
#                         members_slots=Decimal(slots)
#                     )
#                     space.members.add(user)

#                     Category.objects.create(
#                         title="Food",
#                         limit=1000,
#                         spent=0,
#                         father_space=space,
#                         color="#FF9800",
#                         icon="Donut"
#                     )

#                     Category.objects.create(
#                         title="Home",
#                         spent=0,
#                         father_space=space,
#                         color="#FF5050",
#                         icon="Home"
#                     )

#                     Account.objects.create(
#                         title="Cash",
#                         balance=0,
#                         currency=currency,
#                         father_space=space
#                     )

#                     TotalBalance.objects.create(balance=0, father_space=space)

#                     if description == "premium":
#                         print(description)
#                         PaymentHistory.objects.create(
#                             father_space=space,
#                             amount=0,
#                             payment_category="service",
#                         )   
#                 elif existing_spaces.count() > 1:
#                     print("more than one")
#                     # Если таких объектов больше одного, обновляем поле members_slots у второго
#                     space = existing_spaces[1]
#                     if description == "premium":
#                         print(description)
#                         PaymentHistory.objects.create(
#                             father_space=space,
#                             amount=0,
#                             payment_category="service",
#                         )   
#                     # Проверяем, что members_slots не None
#                     if space.members_slots is None:
#                         space.members_slots = Decimal('0')
#                     space.members_slots += Decimal(slots)
#                     space.save()
#             else:
#                 space = existing_spaces[1]

#             Subscription.objects.create(
#                 user=user,
#                 stripe_user=stripe_user,
#                 stripe_subscription_id=subscription_id,
#                 plan=plan,
#             )
#             PaymentHistory.objects.create(
#                 father_space=space,
#                 amount=amount,
#                 payment_category=payment_category,
#             )      

#             # Безопасное обновление роли
#             try:
#                 user.roles = [plan]
#                 user.save()
#                 print(f"User role set to {plan}")
#             except Exception as e:
#                 print(f"Error updating user role: {str(e)}")
#                 # Продолжаем выполнение, так как обновление роли не критично
#                 pass

#             print("message", "Space created successfully")
#             return Response({"message": "Space created successfully"}, status=status.HTTP_201_CREATED)

#         elif event['type'] == 'checkout.session.failed':
#             print("Payment failed for subscription.")

#         return Response(status=status.HTTP_200_OK)


# class CreatePaymentServiceView(generics.GenericAPIView):
#     def get(self, request, space_pk):
#         user = request.user

#         try:
#             # Получаем данные о стоимости из ProjectOverviewView
#             project_overview = ProjectOverviewView()
#             overview_response = project_overview.get(request, space_pk)
#             overview_data = overview_response.data
            
#             # Подсчитываем общую сумму
#             total_amount = sum(float(item['price']) for item in overview_data)
            
#             # Конвертируем в центы для Stripe (умножаем на 100)
#             amount_cents = int(total_amount * 100)

#             print(total_amount, amount_cents)

#             existing_customers = stripe.Customer.list(email=user.email).data

#             if existing_customers:
#                 # Если клиент найден, используем первого из списка
#                 customer = existing_customers[0]
#                 print(f"Existing customer found: {customer['id']}")
#             else:
#                 # Если клиента нет, создаём нового
#                 customer = stripe.Customer.create(
#                     email=user.email,
#                     metadata={"user_id": user.id},
#                 )
#                 print(f"New customer created: {customer['id']}")
            
#             # Создаем линейные элементы для детализации счета
#             line_items = [{
#                 'price_data': {
#                     'currency': 'eur',
#                     'unit_amount': int(float(item['price']) * 100),
#                     'product_data': {
#                         'name': item['assets'],
#                         'description': f'Usage: {item["data"]}'
#                     },
#                 },
#                 'quantity': 1,
#             } for item in overview_data]
            
#             # Создаем Checkout Session
#             checkout_session = stripe.checkout.Session.create(
#                 customer=customer.id,
#                 payment_method_types=['card'],
#                 line_items=line_items,
#                 locale="cs",
#                 metadata={
#                     "description": "service",
#                 },
#                 mode='payment',
#                 success_url=f"{settings.FRONTEND_URL}/shop/success",
#                 cancel_url=f"{settings.FRONTEND_URL}/cancel",
#             )
            
#             return Response({
#                 'session_id': checkout_session.id
#             }, status=status.HTTP_200_OK)
            
#         except stripe.error.StripeError as e:
#             return Response({
#                 'error': str(e)
#             }, status=status.HTTP_400_BAD_REQUEST)