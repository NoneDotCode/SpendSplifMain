from django.urls import path
from backend.apps.store.views import (SubscribePricesView, CreatePaymentSessionView, CreatePaymentServiceView, WebhookAPIView, SubscribeCancel)

urlpatterns = [
    path('subscribes_prices/', SubscribePricesView.as_view(), name='check-subscribes-prices'),
    path('create_checkout_session/', CreatePaymentSessionView.as_view(), name='create-checkout-session'),
    path('my_spaces/<int:space_pk>/create_checkout_service_session/', CreatePaymentServiceView.as_view(), name='create-checkout-session'),
    path('stripe_webhook/', WebhookAPIView.as_view(), name='stripe-webhook'),
    path('subscribe_cancel/', SubscribeCancel.as_view(), name='subscribe-cancel'),
]
