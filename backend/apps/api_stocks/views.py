from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny 
import requests
from backend.apps.api_stocks.models import Stock
from rest_framework.permissions import AllowAny

from backend.apps.converter.utils import convert_currencies


class UpdateStocksAPIViewGroupFirst(APIView):
    permission_classes = AllowAny

    api_key = '296b89a58663457d9dcd754263b549bf'
    symbols_to_check = ['AAPL', 'MSFT', 'AMZN', 'GOOGL']

    def get_stock_name(self, symbol):
        symbol_info_url = f'https://api.twelvedata.com/quote?symbol={symbol}&apikey={self.api_key}'
        response = requests.get(symbol_info_url)
        data = response.json()
        if 'name' in data:
            return data['name']
        return 'N/A'

    def get(self, request, *args, **kwargs):
        response_data = {}
        for symbol in self.symbols_to_check:
            time_series_url = f'https://api.twelvedata.com/time_series?symbol={symbol}&interval=1min&apikey={self.api_key}'
            time_series_response = requests.get(time_series_url)

            try:
                data = time_series_response.json()
                if 'values' in data:
                    values = data['values']
                    if values:
                        latest_data = values[-1]
                        current_price = latest_data.get('close', 'N/A')
                        symbol_name = self.get_stock_name(symbol)

                        response_data[symbol] = {'symbol': symbol,
                                                 'price_usd': current_price,
                                                 'price_eur': convert_currencies(from_currency="USD", to_currency="EUR", amount=current_price),
                                                 'name': symbol_name}

                        stock, created = Stock.objects.get_or_create(symbol=symbol, defaults={'name': symbol_name, 'price': current_price})

                        if not created:
                            stock.price_usd = current_price
                            stock.price_eur = convert_currencies(from_currency="USD", to_currency="EUR", amount=current_price)
                            stock.name = symbol_name
                            stock.save()
                    else:
                        response_data[symbol] = "No data available"
                        
                else:
                    response_data[symbol] = "Error retrieving data: 'values'"
                    
            except Exception as e:
                response_data[symbol] = f"Error retrieving data: {e}"
                

        return Response(response_data, status=status.HTTP_200_OK)



class UpdateStocksAPIViewGroupFirstAdd(UpdateStocksAPIViewGroupFirst):
    symbols_to_check = ['ORCL', 'TSLA', 'BABA', 'JNJ']
class UpdateStocksAPIViewGroupSecond(UpdateStocksAPIViewGroupFirst):
    symbols_to_check = ['BAC', 'XOM', 'GE', 'KO']
class UpdateStocksAPIViewGroupSecondAdd(UpdateStocksAPIViewGroupFirst):
    symbols_to_check = ['PG', 'V', 'MA', 'JPM']
class UpdateStocksAPIViewGroupThird(UpdateStocksAPIViewGroupFirst):
    symbols_to_check = ['PFE', 'INTC', 'CSCO', 'DIS']
class UpdateStocksAPIViewGroupThirdAdd(UpdateStocksAPIViewGroupFirst):
    symbols_to_check = ['IBM', 'BA', 'NFLX', 'JCI']
class UpdateStocksAPIViewGroupFourth(UpdateStocksAPIViewGroupFirst):
    symbols_to_check = ['GM', 'CVX', 'PEP', 'GS']
class UpdateStocksAPIViewGroupFourthAdd(UpdateStocksAPIViewGroupFirst):
    symbols_to_check = ['GE', 'CSCO', 'ORCL','MMM']
class UpdateStocksAPIViewGroupFifth(UpdateStocksAPIViewGroupFirst):
    symbols_to_check = ['HON']



class StockAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        stocks = Stock.objects.all()

        stock_data = {}

        for stock in stocks:
            stock_data[stock.symbol] = {
                'name': stock.name,
                'symbol': stock.symbol,
                'price_usd': str(stock.price_usd),
                'price_eur': str(stock.price_eur)
            }
