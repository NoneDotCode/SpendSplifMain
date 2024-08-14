from rest_framework import generics, permissions, status
import stripe
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView

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
        plan = request.data.get('plan')

        # Здесь вы должны определить цену в зависимости от плана
        if plan == 'standard':
            price = int(settings.SUBSCRIBES_DATA['Standard']['price'].replace("€", "")) * 100
        elif plan == 'premium':
            price = int(settings.SUBSCRIBES_DATA['Premium']['price'].replace("€", "")) * 100
        else:
            return Response({'error': 'Invalid plan'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Создаем или получаем существующего клиента Stripe
            customer = stripe.Customer.create(email=request.user.email)

            # Создаем Ephemeral Key
            ephemeral_key = stripe.EphemeralKey.create(
                customer=customer.id,
                stripe_version=stripe.api_version,
            )

            # Создаем PaymentIntent
            payment_intent = stripe.PaymentIntent.create(
                amount=price,
                currency='eur',
                customer=customer.id,
                automatic_payment_methods={
                    'enabled': True,
                },
            )

            return Response({
                'paymentIntent': payment_intent.client_secret,
                'ephemeralKey': ephemeral_key.secret,
                'customer': customer.id,
                'publishableKey': settings.STRIPE["publishableKey"]
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class StripeWebhookView(generics.GenericAPIView):
    def post(self, request, *args, **kwargs):
        payload = request.body
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

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
                user.roles = ["standard/pre"]
            elif payment_intent['amount'] == price_premium:
                user.roles.remove("premium")
                user.roles = ["premium/pre"]
            user.save()
        elif event['type'] == 'payment_intent.payment_failed':
            return Response({'error': 'Payment was not successful'}, status=status.HTTP_402_PAYMENT_REQUIRED)

        return Response({'status': 'success'}, status=status.HTTP_200_OK)
