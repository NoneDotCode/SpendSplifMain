from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
from apps.api_stocks.models import Stock


class UpdateStocksAPIView(APIView):
    api_key = '296b89a58663457d9dcd754263b549bf'
    symbols_to_check = ['AAPL', 'MSFT', 'AMZN', 'GOOGL', 'ORCL', 'TSLA', 'BABA', 'JNJ']

    def get(self, request, *args, **kwargs):
        for symbol in self.symbols_to_check:
            time_series_url = f'https://api.twelvedata.com/time_series?symbol={symbol}&interval=1min&apikey={self.api_key}'
            time_series_response = requests.get(time_series_url)

            try:
                data = time_series_response.json()['values']
                if data:
                    current_price = data[-1]['close']
                    stock, created = Stock.objects.get_or_create(symbol=symbol, defaults={'price': current_price})

                    if not created:
                        stock.price = current_price
                        stock.save()
                else:
                    print(f"No data available for {symbol}")
            except KeyError as e:
                print(f"Error retrieving data for {symbol}: {e}")

        return Response({'message': 'Stocks updated successfully'}, status=status.HTTP_200_OK)
