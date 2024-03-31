from django.urls import path
from backend.apps.cryptocurrency.views import CryptocurrencyPriceView

urlpatterns = [
    path('api/price/', CryptocurrencyPriceView.as_view(), name='cryptocurrency-price'),
]
