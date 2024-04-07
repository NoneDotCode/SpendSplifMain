import requests
from celery import shared_task
from backend.apps.api_stocks.models import Stock
import environ
import time

env = environ.Env()
environ.Env.read_env()


def update_group_prices(api_key, symbols):
    for symbol in symbols:
        time_series_url = f'https://api.twelvedata.com/time_series?symbol={symbol}&interval=1min&apikey={api_key}'
        time_series_response = requests.get(time_series_url)

        data = time_series_response.json()
        if 'values' in data:
            values = data['values']
            if values:
                latest_data = values[-1]
                current_price = latest_data.get('close', 'N/A')

                stock, created = Stock.objects.update_or_create(symbol=symbol, defaults={'price': current_price})
                if not created:
                    stock.price = current_price
                    stock.save()
    print('Group Stocks prices updated')
    time.sleep(65)

@shared_task
def update_stock_prices_1():
    api_key = '296b89a58663457d9dcd754263b549bf'
    group_1_symbols = ['AAPL', 'MSFT', 'AMZN', 'GOOGL', 'ORCL', 'TSLA', 'BABA', 'JNJ']
    update_group_prices(api_key, group_1_symbols)
    

@shared_task
def update_stock_prices_2():
    api_key = '296b89a58663457d9dcd754263b549bf'
    group_2_symbols = ['BAC', 'XOM', 'GE', 'KO', 'PG', 'V', 'MA', 'JPM']
    update_group_prices(api_key, group_2_symbols)
    
@shared_task
def update_stock_prices_3():
    api_key = '296b89a58663457d9dcd754263b549bf'
    group_3_symbols = ['PFE', 'INTC', 'CSCO', 'DIS', 'IBM', 'BA', 'NFLX', 'JCI']
    update_group_prices(api_key, group_3_symbols)

@shared_task
def update_stock_prices_4():
    api_key = '296b89a58663457d9dcd754263b549bf'
    group_4_symbols = ['GM', 'CVX', 'PEP', 'GS','GE', 'CSCO', 'ORCL','MMM']
    update_group_prices(api_key, group_4_symbols)

@shared_task
def update_stock_prices_5():
    api_key = '296b89a58663457d9dcd754263b549bf'
    group_5_symbols = ['HON']
    update_group_prices(api_key, group_5_symbols)

