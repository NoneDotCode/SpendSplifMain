import os
import requests
from celery import shared_task
from .models import Stock
import environ

# Инициализация environ
env = environ.Env()
environ.Env.read_env()  # Чтение .env файла

@shared_task
def update_stock_prices():
    API_KEY = env('ALPHA_VANTAGE_API_KEY')
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'FB']

    for symbol in symbols:
        url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={API_KEY}'
        data = requests.get(url).json()

        if 'Global Quote' in data and '05. price' in data['Global Quote']:
            price = data['Global Quote']['05. price']
            stock, created = Stock.objects.get_or_create(
                symbol=symbol,
                defaults={'name': symbol, 'price': price}
            )
            if not created:
                stock.price = price
                stock.save()
            print(f"{'Created' if created else 'Updated'} {symbol}: {stock.price}")
        else:
            print(f"Price data not available for {symbol}")

    return "Stock prices updated"