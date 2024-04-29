from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny 
import requests
from backend.apps.api_stocks.models import Stock
from rest_framework import generics
from .serializers import StockSerializer
from backend.apps.converter.utils import convert_currencies
from datetime import datetime

class UpdateStocksAPIViewGroupFirst(APIView):
    permission_classes = AllowAny

    api_key = '5a479d490af540dc99572bd655bbe7b4'
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

class GenerateRandomStockDataView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = StockSerializer

    def get(self, request, *args, **kwargs):
        stock_data = [
            {'name': 'Oracle Corporation', 'symbol': 'ORCL', 'price_usd': 343,
            'price_eur': 233, 'last_updated': datetime.now()},
            {'name': 'TSLA', 'symbol': 'STK2', 'price_usd': 232,
            'price_eur': 190, 'last_updated': datetime.now()},
            {'name': 'Alibaba Group Holding Limited', 'symbol': 'BABA', 'price_usd': 450,
            'price_eur': 320, 'last_updated': datetime.now()},
            {'name': 'Johnson & Johnson', 'symbol': 'JNJ', 'price_usd': 275,
            'price_eur': 200, 'last_updated': datetime.now()},
            {'name': 'Bank of America Corporation', 'symbol': 'BAC', 'price_usd': 150,
            'price_eur': 120, 'last_updated': datetime.now()},
            {'name': 'Exxon Mobil Corporation', 'symbol': 'XOM', 'price_usd': 60,
            'price_eur': 50, 'last_updated': datetime.now()},
            {'name': 'General Electric Company', 'symbol': 'GE', 'price_usd': 80,
            'price_eur': 70, 'last_updated': datetime.now()},
            {'name': 'The Coca-Cola Company', 'symbol': 'KO', 'price_usd': 55,
            'price_eur': 45, 'last_updated': datetime.now()},
            {'name': 'Procter & Gamble Company', 'symbol': 'PG', 'price_usd': 130,
            'price_eur': 110, 'last_updated': datetime.now()},
            {'name': 'Visa Inc.', 'symbol': 'V', 'price_usd': 240,
            'price_eur': 200, 'last_updated': datetime.now()},
            {'name': 'Mastercard Incorporated', 'symbol': 'MA', 'price_usd': 350,
            'price_eur': 280, 'last_updated': datetime.now()},
            {'name': 'JPMorgan Chase & Co.', 'symbol': 'JPM', 'price_usd': 180,
            'price_eur': 150, 'last_updated': datetime.now()},
            {'name': 'Pfizer Inc.', 'symbol': 'PFE', 'price_usd': 45,
            'price_eur': 40, 'last_updated': datetime.now()},
            {'name': 'Intel Corporation', 'symbol': 'INTC', 'price_usd': 65,
            'price_eur': 55, 'last_updated': datetime.now()},
            {'name': 'Cisco Systems, Inc.', 'symbol': 'CSCO', 'price_usd': 50,
            'price_eur': 45, 'last_updated': datetime.now()},
            {'name': 'The Walt Disney Company', 'symbol': 'DIS', 'price_usd': 180,
            'price_eur': 150, 'last_updated': datetime.now()},
            {'name': 'International Business Machines Corporation', 'symbol': 'IBM', 'price_usd': 120,
            'price_eur': 100, 'last_updated': datetime.now()},
            {'name': 'The Boeing Company', 'symbol': 'BA', 'price_usd': 230,
            'price_eur': 200, 'last_updated': datetime.now()},
            {'name': 'Netflix, Inc.', 'symbol': 'NFLX', 'price_usd': 400,
            'price_eur': 350, 'last_updated': datetime.now()},
            {'name': 'Johnson Controls International plc', 'symbol': 'JCI', 'price_usd': 55,
            'price_eur': 45, 'last_updated': datetime.now()},
            {'name': 'General Motors Company', 'symbol': 'GM', 'price_usd': 65,
            'price_eur': 55, 'last_updated': datetime.now()},
            {'name': 'Chevron Corporation', 'symbol': 'CVX', 'price_usd': 110,
            'price_eur': 90, 'last_updated': datetime.now()},
            {'name': 'PepsiCo, Inc.', 'symbol': 'PEP', 'price_usd': 160,
            'price_eur': 140, 'last_updated': datetime.now()},
            {'name': 'The Goldman Sachs Group, Inc.', 'symbol': 'GS', 'price_usd': 400,
            'price_eur': 350, 'last_updated': datetime.now()},
            {'name': '3M Company', 'symbol': 'MMM', 'price_usd': 200,
            'price_eur': 180, 'last_updated': datetime.now()},
            {'name': 'Honeywell International Inc.', 'symbol': 'HON', 'price_usd': 590,
            'price_eur': 300, 'last_updated': datetime.now()},
        ]

        for data in stock_data:
            serializer = StockSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response("Random stock data generated successfully", status=status.HTTP_201_CREATED)

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
        return Response(stock_data, status=status.HTTP_200_OK)
