from rest_framework import generics, permissions, status
import stripe
from django.conf import settings
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

class SubscribePricesView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        data = settings.SUBSCRIBES_DATA
        result = {}
        for subscribe in data:
            for sub_data in data[subscribe]:
                result[f"{subscribe.lower()}_{sub_data}"] = data[subscribe][sub_data]
        return Response(result, status=status.HTTP_200_OK)


class CreateCheckoutSessionView(CreateAPIView):
    def create(self, request, *args, **kwargs):
        try:
            checkout_session = stripe.checkout.Session.create(
                line_items=[
                    {
                        'price': 'price_1PnZYwJ4gLcb8EJ9kjM5m9zD',
                        'quantity': 1,
                    },
                ],
                mode='payment',
                success_url=settings.STRIPE["payment_callback_url"] + '?success=true',
                cancel_url=settings.STRIPE["payment_callback_url"] + '?canceled=true',
            )
            return Response({'checkout_url': checkout_session.url}, status=status.HTTP_303_SEE_OTHER)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)