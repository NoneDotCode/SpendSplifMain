from rest_framework import generics, permissions, status
import stripe
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from backend.apps.store.models import Subscription
from backend.apps.customuser.models import CustomUser


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

            print(checkout_session.id)
            return Response({"session_id": checkout_session.id}, status=status.HTTP_200_OK)
        except Exception as e:
            print("error", str(e))
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class WebhookAPIView(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)

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

        # Обработка события
        if event['type'] == 'invoice.payment_succeeded':
            subscription = event['data']['object']
            # Логика подтверждения оплаты подписки
            print(f"Subscription {subscription['id']} was paid successfully.")
        elif event['type'] == 'invoice.payment_failed':
            print("Payment failed for subscription.")

        return Response(status=status.HTTP_200_OK)


class StripeWebhookView(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)

    @staticmethod
    def post(request, *args, **kwargs):
        payload = request.body
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']
        endpoint_secret = settings.STRIPE["webhook_secret_key"]

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError as e:
            return Response({'error': 'Invalid payload'}, status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError as e:
            return Response({'error': 'Invalid signature'}, status=status.HTTP_400_BAD_REQUEST)

        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            # Access the customer ID from the event object
            customer_id = payment_intent['customer']

            # Retrieve the customer object based on the customer ID
            customer = stripe.Customer.retrieve(customer_id)

            user = CustomUser.objects.get(email=customer["email"])
            price_premium = int(settings.SUBSCRIBES_DATA['Premium']['price'].replace("€", "")) * 100
            price_standard = int(settings.SUBSCRIBES_DATA['Standard']['price'].replace("€", "")) * 100
            if payment_intent['amount'] == price_standard:
                if "free" in user.roles:
                    user.roles.remove("free")
                elif "premium" in user.roles:
                    user.roles.remove("premium")
                user.roles = ["standard/pre"]
            elif payment_intent['amount'] == price_premium:
                if "premium" in user.roles:
                    user.roles.remove("premium")
                elif "standard/pre" in user.roles:
                    user.roles.remove("standard/pre")
                user.roles = ["premium/pre"]
            user.save()
        elif event['type'] == 'payment_intent.payment_failed':
            return Response({'error': 'Payment was not successful'}, status=status.HTTP_402_PAYMENT_REQUIRED)

        return Response({'status': 'success'}, status=status.HTTP_200_OK)


class SubscribeCancel(generics.GenericAPIView):
    @staticmethod
    def post(request, *args, **kwargs):
        return Response({'status': 'Your subscribe will end when you will die.'},
                        status=status.HTTP_200_OK)
