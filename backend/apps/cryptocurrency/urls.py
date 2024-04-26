from django.urls import path
from backend.apps.cryptocurrency.views import CryptocurrencyPriceView, GenerateRandomCryptocurrencyDataView, StockAndCryptoAPIView

urlpatterns = [
    path('price/', CryptocurrencyPriceView.as_view(), name='cryptocurrency-price'),
    path('add_all_cryptocurrencies/', GenerateRandomCryptocurrencyDataView.as_view(), name='cryptocurrencies_add_all'),
    path('stock_and_crypto_price/', StockAndCryptoAPIView.as_view(), name="stock and crypto prices")
]
