from rest_framework import generics, permissions, status
import stripe
from django.conf import settings
from backend.apps.account.models import Account
from backend.apps.category.models import Category
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

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


stripe.api_key = settings.STRIPE["secret"]


class CreatePaymentSessionView(generics.GenericAPIView):
    def post(self, request):
        user = request.user
        plan = request.data.get('plan')
        count = request.data.get('count', 1)
        print(count)
        print(f"STRIPE_{plan.upper()}_PRICE_ID")
        
        # Проверяем, передан ли план, и существует ли соответствующее поле в settings
        if not plan or not hasattr(settings, f"STRIPE_{plan.upper()}_PRICE_ID"):
            return Response(
                {"error": "Invalid plan or plan not configured in settings."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Получаем ID цены для плана
            price_id = getattr(settings, f"STRIPE_{plan.upper()}_PRICE_ID")

            # Определяем режим Checkout Session
            mode = "subscription" if plan == "standard" else "payment"
            
            # Создаем Stripe Customer, если его еще нет
            existing_customers = stripe.Customer.list(email=user.email).data

            if 'business_lic' in user.roles:
                plan = "add_license"

            if existing_customers:
                # Если клиент найден, используем первого из списка
                customer = existing_customers[0]
                print(f"Existing customer found: {customer['id']}")
            else:
                # Если клиента нет, создаём нового
                customer = stripe.Customer.create(
                    email=user.email,
                    metadata={"user_id": user.id},
                )
                print(f"New customer created: {customer['id']}")


            # Создаем Checkout Session
            checkout_session = stripe.checkout.Session.create(
                customer=customer.id,
                payment_method_types=["card"],
                line_items=[{
                    "price": price_id,
                    "quantity": count,
                }],
                mode=mode,
                success_url=f"{settings.FRONTEND_URL}/shop/success",
                cancel_url=f"{settings.FRONTEND_URL}/cancel",
                locale="cs",
                metadata={
                    "description": plan,  # Передача значения переменной plan
                },
            )

            return Response({"session_id": checkout_session.id}, status=status.HTTP_200_OK)
        except Exception as e:
            print("error", str(e))
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class WebhookAPIView(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    
    VALID_ROLES = ["free", "business_plan", "business_lic", "sponsor", "employee"]

    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')
        webhook_secret = settings.STRIPE_WEBHOOK_SECRET

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        except ValueError as e:
            print("error", "Invalid payload")
            return Response({"error": "Invalid payload"}, status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError as e:
            print("error", "Invalid signature")
            return Response({"error": "Invalid signature"}, status=status.HTTP_400_BAD_REQUEST)

        print(event['type'])
        # Обработка события
        if event['type'] == 'checkout.session.completed':
            print("Payment successful.")

            # Получаем нужные переменные из события
            session = event['data']['object']
            user_email = session['customer_details']['email']
            mode = session.get('mode')
            stripe_user = session.get('customer')
            print("adfadf", mode, stripe_user)

            try:
                user = CustomUser.objects.get(email=user_email)
            except CustomUser.DoesNotExist:
                print("error", "User not found")
                return Response({"error": "User not found"}, status=status.HTTP_400_BAD_REQUEST)
            # Остальная логика создания Space, ролей и категорий
            # Ищем первую запись Space, где есть этот пользователь в members
            try:
                existing_space = Space.objects.filter(members=user).first()
                if not existing_space:
                    print("error", "No space found for this user")
                    return Response({"error": "No space found for this user"}, status=status.HTTP_400_BAD_REQUEST)
            except Space.DoesNotExist:
                print("error", "Space model not found")
                return Response({"error": "Space model not found"}, status=status.HTTP_400_BAD_REQUEST)

            # Получаем валюту из найденной записи
            currency = existing_space.currency

            # Создаем новый объект Space
            existing_spaces = Space.objects.filter(members=user)

            # Сохраняем подписку в модели Subscription
            print("session:", session)
            if mode == "subscription":
                # Обработка подписки
                subscription_id = session.get('subscription')
                slots = 10
                plan="business_plan"
                payment_category="subscription",
                print("Products purchased:", subscription_id, amount, slots, payment_category)
            elif mode == "payment":
                description = session.get('metadata', {}).get('description')
                if description == "premium":
                    # Обработка обычной покупки
                    plan="business_lic"
                    subscription_id = session.get('payment_intent')
                    amount = session.get('amount_total')
                    amount = amount / 100
                    slots = amount / 500
                    payment_category="license"
                    print("Products purchased:", subscription_id, amount, slots, payment_category)
                if description == "add_license":
                    # Обработка обычной покупки
                    plan="business_lic"
                    subscription_id = session.get('payment_intent')
                    amount = session.get('amount_total')
                    amount = amount / 100
                    slots = amount / 500
                    payment_category="license"
                    print("Products purchased:", subscription_id, amount, slots, payment_category)
            print(existing_spaces.count())
            if existing_spaces.count() == 1:
                print("one")
                # Создаём новый объект, так как существует только один такой объект
                space = Space.objects.create(
                    title=user.username,
                    currency=currency,
                    members_slots=Decimal(slots)
                )
                space.members.add(user)

                Category.objects.create(
                    title="Food",
                    limit=1000,
                    spent=0,
                    father_space=space,
                    color="#FF9800",
                    icon="Donut"
                )

                Category.objects.create(
                    title="Home",
                    spent=0,
                    father_space=space,
                    color="#FF5050",
                    icon="Home"
                )

                Account.objects.create(
                    title="Cash",
                    balance=0,
                    currency=currency,
                    father_space=space
                )

                TotalBalance.objects.create(balance=0, father_space=space)
            elif existing_spaces.count() > 1:
                print("more than one")
                # Если таких объектов больше одного, обновляем поле members_slots у второго
                space = existing_spaces[1]
                space.members_slots += Decimal(slots)
                space.save()                          

            Subscription.objects.create(
                user=user,
                stripe_user=stripe_user,
                stripe_subscription_id=subscription_id,
                plan=plan,
            )
            PaymentHistory.objects.create(
                father_space=space,
                amount=amount,
                payment_category=payment_category,
            )      

            # Безопасное обновление роли
            try:
                user.roles = [plan]
                user.save()
                print(f"User role set to {plan}")
            except Exception as e:
                print(f"Error updating user role: {str(e)}")
                # Продолжаем выполнение, так как обновление роли не критично
                pass

            print("message", "Space created successfully")
            return Response({"message": "Space created successfully"}, status=status.HTTP_201_CREATED)

        elif event['type'] == 'checkout.session.failed':
            print("Payment failed for subscription.")

        return Response(status=status.HTTP_200_OK)


class SubscribeCancel(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
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
                    if any(role in member.roles for role in ['business_member', 'business_lic', 'business_plan']):
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

