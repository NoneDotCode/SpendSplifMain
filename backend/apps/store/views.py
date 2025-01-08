from rest_framework import generics, permissions, status
import stripe
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from backend.apps.store.models import Subscription
from backend.apps.customuser.models import CustomUser
from backend.apps.space.models import Space


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
        try:
            # Создаем Stripe Customer, если его еще нет
            customer = stripe.Customer.create(
                email=user.email,
                metadata={"user_id": user.id},
            )

            # Создаем Checkout Session
            checkout_session = stripe.checkout.Session.create(
                customer=customer.id,
                payment_method_types=["card"],  # Способы оплаты
                line_items=[
                    {
                        "price": settings.STRIPE_BUSINESS_PLAN_PRICE_ID,
                        "quantity": 1,
                    }
                ],
                mode="subscription",
                success_url=f"{settings.FRONTEND_URL}/success?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{settings.FRONTEND_URL}/cancel",
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
            return Response({"error": "Invalid payload"}, status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError as e:
            return Response({"error": "Invalid signature"}, status=status.HTTP_400_BAD_REQUEST)

        print(event['type'])
        # Обработка события
        if event['type'] == 'checkout.session.completed':
            print("Payment successful.")

            # Получаем мейл пользователя из события
            session = event['data']['object']
            user_email = session['customer_details']['email']

            try:
                print(user_email)
                user = CustomUser.objects.get(email=user_email)
            except CustomUser.DoesNotExist:
                print("error", "User not found")
                return Response({"error": "User not found"}, status=status.HTTP_400_BAD_REQUEST)

            # Ищем первую запись Space, где есть этот пользователь в members
            try:
                existing_space = Space.objects.filter(members=user).first()
                if not existing_space:
                    print("error", "No space found for this user")
                    return Response({"error": "No space found for this user"}, status=status.HTTP_400_BAD_REQUEST)
            except Space.DoesNotExist:
                return Response({"error": "Space model not found"}, status=status.HTTP_400_BAD_REQUEST)

            # Получаем валюту из найденной записи
            currency = existing_space.currency

            # Создаем новый объект Space
            space = Space.objects.create(
                title=user.username,
                currency=currency,
                members_slots=10
            )
            space.members.add(user)

            # Безопасное обновление роли
            try:
                if user.roles and len(user.roles) > 0:
                    if user.roles[0] == 'free':
                        user.roles = ['business_plan']  # ArrayField ожидает список
                        user.save()
                        print("User role updated from free to business_plan")
                else:
                    # Если roles пустой, устанавливаем business_plan
                    user.roles = ['business_plan']
                    user.save()
                    print("User role set to business_plan (was empty)")
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
    @staticmethod
    def post(request, *args, **kwargs):
        return Response({'status': 'Your subscribe will end when you will die.'},
                        status=status.HTTP_200_OK)
