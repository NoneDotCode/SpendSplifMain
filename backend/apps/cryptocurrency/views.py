from rest_framework import generics
from rest_framework.response import Response
from backend.apps.cryptocurrency.models import Cryptocurrency
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny 
import requests

class CryptocurrencyPriceView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    def get(self, request,*args, **kwargs):
        cryptocurrency = Cryptocurrency.objects.all()

        crypto_data = {}

        for crypto in cryptocurrency:
            crypto_data[crypto.symbol] = {
                'name': crypto.name,
                'symbol': crypto.symbol,
                'price_usd': str(crypto.price_usd),
                'price_eur': str(crypto.price_eur),
                'last_updated': crypto.last_updated,
            }

        return Response(crypto_data, status=status.HTTP_200_OK)
