from django.urls import path
from .views import *

urlpatterns = [
    path('api/price/', CryptocurrencyPriceView.as_view(), name='cryptocurrency-price'),
]