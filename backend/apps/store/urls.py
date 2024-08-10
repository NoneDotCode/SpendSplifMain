from django.urls import path
from backend.apps.store.views import SubscribePricesView

urlpatterns = [
    path('subscribes_prices/', SubscribePricesView.as_view(), name='check-subscribes-prices')
]