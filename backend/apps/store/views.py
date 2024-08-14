from rest_framework import generics, permissions, status
import stripe
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView

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
