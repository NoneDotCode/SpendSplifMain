import datetime
from rest_framework import generics
from rest_framework.response import Response
from backend.apps.cryptocurrency.models import Cryptocurrency
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny 
import requests
from .serializers import CryptocurrencySerializer
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

class GenerateRandomCryptocurrencyDataView(generics.ListAPIView):
    serializer_class = CryptocurrencySerializer
    permission_classes = (AllowAny)

    def get(self, request, *args, **kwargs):
        cryptocurrencies = [
            {'name': 'Bitcoin', 'symbol': 'bitcoin', 'code': 'BTC', 'price_usd': 590, 'price_eur': 300},
            {'name': 'Ethereum', 'symbol': 'ethereum', 'code': 'ETH', 'price_usd': 4000, 'price_eur': 3500},
            {'name': 'Litecoin', 'symbol': 'litecoin', 'code': 'LTC', 'price_usd': 200, 'price_eur': 180},
            {'name': 'Ripple', 'symbol': 'ripple', 'code': 'XRP', 'price_usd': 1.2, 'price_eur': 1},
            {'name': 'Cardano', 'symbol': 'cardano', 'code': 'ADA', 'price_usd': 2, 'price_eur': 1.8},
            {'name': 'Polkadot', 'symbol': 'polkadot', 'code': 'DOT', 'price_usd': 40, 'price_eur': 35},
            {'name': 'Chainlink', 'symbol': 'chainlink', 'code': 'LINK', 'price_usd': 30, 'price_eur': 25},
            {'name': 'Stellar', 'symbol': 'stellar', 'code': 'XLM', 'price_usd': 0.5, 'price_eur': 0.45},
            {'name': 'Bitcoin Cash', 'symbol': 'bitcoin-cash', 'code': 'BCH', 'price_usd': 700, 'price_eur': 600},
            {'name': 'Binance Coin', 'symbol': 'binancecoin', 'code': 'BNB', 'price_usd': 500, 'price_eur': 450},
            {'name': 'USD Coin', 'symbol': 'usd-coin', 'code': 'USDC', 'price_usd': 1, 'price_eur': 0.9},
            {'name': 'Wrapped Bitcoin', 'symbol': 'wrapped-bitcoin', 'code': 'WBTC', 'price_usd': 60000, 'price_eur': 55000},
            {'name': 'Litecoin', 'symbol': 'litecoin', 'code': 'LTC', 'price_usd': 200, 'price_eur': 180},
            {'name': 'Solana', 'symbol': 'solana', 'code': 'SOL', 'price_usd': 200, 'price_eur': 180},
            {'name': 'Dogecoin', 'symbol': 'dogecoin', 'code': 'DOGE', 'price_usd': 0.3, 'price_eur': 0.25},
            {'name': 'Avalanche', 'symbol': 'avalanche', 'code': 'AVAX', 'price_usd': 100, 'price_eur': 90},
            {'name': 'Uniswap', 'symbol': 'uniswap', 'code': 'UNI', 'price_usd': 30, 'price_eur': 25},
            {'name': 'Filecoin', 'symbol': 'filecoin', 'code': 'FIL', 'price_usd': 150, 'price_eur': 130},
            {'name': 'Theta Network', 'symbol': 'theta-token', 'code': 'THETA', 'price_usd': 10, 'price_eur': 9},
            {'name': 'Bitcoin SV', 'symbol': 'bitcoin-cash-sv', 'code': 'BSV', 'price_usd': 300, 'price_eur': 250},
            {'name': 'Crypto.com Coin', 'symbol': 'crypto-com-coin', 'code': 'CRO', 'price_usd': 0.1, 'price_eur': 0.09},
            {'name': 'TRON', 'symbol': 'tron', 'code': 'TRX', 'price_usd': 0.05, 'price_eur': 0.045},
            {'name': 'Ethereum Classic', 'symbol': 'ethereum-classic', 'code': 'ETC', 'price_usd': 50, 'price_eur': 45},
            {'name': 'Tezos', 'symbol': 'tezos', 'code': 'XTZ', 'price_usd': 5, 'price_eur': 4.5},
            {'name': 'FTX Token', 'symbol': 'ftx-token', 'code': 'FTT', 'price_usd': 50, 'price_eur': 45},
            {'name': 'NEO', 'symbol': 'neo', 'code': 'NEO', 'price_usd': 40, 'price_eur': 35},
            {'name': 'Cosmos', 'symbol': 'cosmos', 'code': 'ATOM', 'price_usd': 25, 'price_eur': 22.5},
            {'name': 'Monero', 'symbol': 'monero', 'code': 'XMR', 'price_usd': 300, 'price_eur': 250},
            {'name': 'Algorand', 'symbol': 'algorand', 'code': 'ALGO', 'price_usd': 1, 'price_eur': 0.9},
            {'name': 'Aave', 'symbol': 'aave', 'code': 'AAVE', 'price_usd': 500, 'price_eur': 450},
            {'name': 'Compound', 'symbol': 'compound', 'code': 'COMP', 'price_usd': 300, 'price_eur': 250},
            {'name': 'Dash', 'symbol': 'dash', 'code': 'DASH', 'price_usd': 150, 'price_eur': 130}
        ]

        for data in cryptocurrencies:
            serializer = CryptocurrencySerializer(data=data)
            if serializer.is_valid():
                serializer.save(last_updated=datetime.now())
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response("Random cryptocurrency data generated successfully", status=status.HTTP_201_CREATED)