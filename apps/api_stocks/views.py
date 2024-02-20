from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
from apps.api_stocks.models import Stock




class UpdateStocksAPIView_group1(APIView):
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

                        response_data[symbol] = {'symbol': symbol, 'price': current_price, 'name': symbol_name}

                        stock, created = Stock.objects.get_or_create(symbol=symbol, defaults={'name': symbol_name, 'price': current_price})

                        if not created:
                            stock.price = current_price
                            stock.name = symbol_name
                            stock.save()
                    else:
                        response_data[symbol] = "No data available"
                        print(f"No data available for {symbol}")
                else:
                    response_data[symbol] = "Error retrieving data: 'values'"
                    print(f"Error retrieving data for {symbol}: 'values' key not found")
            except Exception as e:
                response_data[symbol] = f"Error retrieving data: {e}"
                print(f"Error retrieving data for {symbol}: {e}")

        return Response(response_data, status=status.HTTP_200_OK)



class Update_Stocks_APIView_group1_add(UpdateStocksAPIView_group1):
    symbols_to_check = ['ORCL', 'TSLA', 'BABA', 'JNJ']
class UpdateStocksAPIView_group2(UpdateStocksAPIView_group1):
    symbols_to_check = ['BAC', 'XOM', 'GE', 'KO']
class UpdateStocksAPIView_group2_add(UpdateStocksAPIView_group2):
    symbols_to_check = ['PG', 'V', 'MA', 'JPM']
class UpdateStocksAPIView_group3(UpdateStocksAPIView_group2):
    symbols_to_check = ['PFE', 'INTC', 'CSCO', 'DIS']
class UpdateStocksAPIView_group3_add(UpdateStocksAPIView_group3):
    symbols_to_check = ['IBM', 'BA', 'NFLX', 'JCI']

class UpdateStocksAPIView_group4(UpdateStocksAPIView_group3):
    symbols_to_check = ['GM', 'CVX', 'PEP', 'GS']

class UpdateStocksAPIView_group4_add(UpdateStocksAPIView_group4):
    symbols_to_check = ['GE', 'CSCO', 'ORCL','MMM']

class UpdateStocksAPIView_group5(UpdateStocksAPIView_group4):
    symbols_to_check = ['HON']

class StockAPIView(APIView):
    def get(self, request, *args, **kwargs):
        stocks = Stock.objects.all()

        stock_data = {}

        for stock in stocks:
            stock_data[stock.symbol] = str(stock.price)

        return Response(stock_data, status=status.HTTP_200_OK)

