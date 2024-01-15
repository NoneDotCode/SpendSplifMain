import requests
from celery import shared_task
from .models import Cryptocurrency
import logging

logger = logging.getLogger(__name__)

@shared_task()
def update_crypto_prices():
    print("Task started: update_crypto_prices")
    logger.info("Task started: update_crypto_prices")
    url = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd,eur'
    data = requests.get(url).json()
    print(f"Data from API: {data}")

    # Список криптовалют, которые нужно обновить или создать
    cryptocurrencies = [
        {'name': 'Bitcoin', 'symbol': 'bitcoin'},
        {'name': 'Ethereum', 'symbol': 'ethereum'}
    ]

    for crypto in cryptocurrencies:
        symbol = crypto['symbol']
        # Получение или создание объекта криптовалюты
        obj, created = Cryptocurrency.objects.get_or_create(
            symbol=symbol,
            defaults={'name': crypto['name']}
        )
        print(f"{'Created' if created else 'Found'} {symbol} in database")

        if symbol in data:
            obj.price_usd = data[symbol]['usd']
            obj.price_eur = data[symbol]['eur']
            obj.save()
            print(f"Updated {symbol}: USD {obj.price_usd}, EUR {obj.price_eur}")

    return "Crypto prices updated"