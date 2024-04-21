from django.urls import path
from backend.apps.cryptocurrency.views import CryptocurrencyPriceView, GenerateRandomCryptocurrencyDataView

urlpatterns = [
    path('price/', CryptocurrencyPriceView.as_view(), name='cryptocurrency-price'),
    path('add_all_cryptocurrencies/', GenerateRandomCryptocurrencyDataView.as_view(), name='cryptocurrencies_add_all'),
]
