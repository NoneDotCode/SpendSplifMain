from django.urls import path
from backend.apps.store.views import SubscribePricesView, CreatePaymentSessionView

urlpatterns = [
    path('subscribes_prices/', SubscribePricesView.as_view(), name='check-subscribes-prices'),
    path('create_checkout_session/', CreatePaymentSessionView.as_view(), name='create-checkout-session')
]
