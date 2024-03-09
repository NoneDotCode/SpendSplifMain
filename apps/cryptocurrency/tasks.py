import requests
from celery import shared_task
from .models import Cryptocurrency
import logging

logger = logging.getLogger(__name__)

@shared_task()
def update_crypto_prices():
    logger.info("Task started: update_crypto_prices")
    url = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd,eur'
    data = requests.get(url).json()

    cryptocurrencies = [
        {'name': 'Bitcoin', 'symbol': 'bitcoin'},
        {'name': 'Ethereum', 'symbol': 'ethereum'}
    ]

    for crypto in cryptocurrencies:
        symbol = crypto['symbol']
        name = crypto['name']
        
        if symbol in data and data[symbol]['usd'] is not None:
            price_usd = data[symbol]['usd']
            price_eur = data[symbol]['eur']
            obj, created = Cryptocurrency.objects.update_or_create(
                symbol=symbol,
                defaults={'name': name, 'price_usd': price_usd, 'price_eur': price_eur}
            )
            logger.info(f"{'Created' if created else 'Updated'} {symbol} in database with USD {price_usd} and EUR {price_eur}")
        else:
            logger.warning(f"No price data available for {symbol}")

    print('Crypto Prices updated')