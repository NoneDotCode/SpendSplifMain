from django.urls import path
from backend.apps.cryptocurrency.views import CryptocurrencyPriceView

urlpatterns = [
    path('price/', CryptocurrencyPriceView.as_view(), name='cryptocurrency-price'),
]
