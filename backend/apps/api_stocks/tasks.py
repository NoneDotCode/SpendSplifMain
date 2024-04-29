import requests
from celery import shared_task
from backend.apps.api_stocks.models import Stock
import environ
import time
from backend.apps.converter.utils import convert_currencies
from backend.apps.api_stocks.constants import names_of_companies

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
                current_price = latest_data.get('close', None)
                print(current_price)
                current_price_eur = convert_currencies(from_currency="USD", to_currency="EUR", amount=float(current_price))

                stock, created = Stock.objects.update_or_create(name=names_of_companies[symbol],
                                                                symbol=symbol,
                                                                defaults={'price_usd': current_price,
                                                                          'price_eur': current_price_eur})
                if not created:
                    stock.price_usd = current_price
                    stock.price_eur = current_price_eur
                    stock.save()
    print('Group Stocks prices updated')
    return data

@shared_task
def update_stock_prices_1():
    api_key = '5a479d490af540dc99572bd655bbe7b4'
    group_1_symbols = ['AAPL', 'MSFT', 'AMZN', 'GOOGL', 'ORCL', 'TSLA', 'BABA', 'JNJ']
    update_group_prices(api_key, group_1_symbols)


@shared_task
def update_stock_prices_2():
    api_key = '5a479d490af540dc99572bd655bbe7b4'
    group_2_symbols = ['BAC', 'XOM', 'GE', 'KO', 'PG', 'V', 'MA', 'JPM']
    update_group_prices(api_key, group_2_symbols)
    
@shared_task
def update_stock_prices_3():
    api_key = '5a479d490af540dc99572bd655bbe7b4'
    group_3_symbols = ['PFE', 'INTC', 'CSCO', 'DIS', 'IBM', 'BA', 'NFLX', 'JCI']
    update_group_prices(api_key, group_3_symbols)

@shared_task
def update_stock_prices_4():
    api_key = '5a479d490af540dc99572bd655bbe7b4'
    group_4_symbols = ['GM', 'CVX', 'PEP', 'GS','MMM']
    update_group_prices(api_key, group_4_symbols)

@shared_task
def update_stock_prices_5():
    api_key = '5a479d490af540dc99572bd655bbe7b4'
    group_5_symbols = ['HON']
    update_group_prices(api_key, group_5_symbols)
