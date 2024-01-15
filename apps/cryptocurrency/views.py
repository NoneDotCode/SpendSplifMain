from rest_framework import generics
from rest_framework.response import Response
from .models import Cryptocurrency

class CryptocurrencyPriceView(generics.RetrieveAPIView):
    def get(self, request, **kwargs):
        symbol = request.query_params.get('symbol')
        try:
            cryptocurrency = Cryptocurrency.objects.get(symbol=symbol.upper())
            return Response({
                'name': cryptocurrency.name,
                'symbol': cryptocurrency.symbol,
                'price_usd': cryptocurrency.price_usd,
                'price_eur': cryptocurrency.price_eur,
                'last_updated': cryptocurrency.last_updated
            })
        except Cryptocurrency.DoesNotExist:
            return Response({'error': 'Cryptocurrency not found'}, status=404)