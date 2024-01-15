from django.urls import path
from .views import CryptocurrencyPriceView

urlpatterns = [
    path('api/price/', CryptocurrencyPriceView.as_view(), name='cryptocurrency-price')
]