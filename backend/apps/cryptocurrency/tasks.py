import requests
from celery import shared_task
from .models import Cryptocurrency
import logging

logger = logging.getLogger(__name__)

@shared_task()
def update_crypto_prices():
    logger.info("Task started: update_crypto_prices")    
    cryptocurrencies = [
        {'name': 'Bitcoin', 'symbol': 'bitcoin'},
        {'name': 'Ethereum', 'symbol': 'ethereum'},
        {'name': 'Litecoin', 'symbol': 'litecoin'},
        {'name': 'Ripple', 'symbol': 'ripple'},
        {'name': 'Cardano', 'symbol': 'cardano'},
        {'name': 'Polkadot', 'symbol': 'polkadot'},
        {'name': 'Chainlink', 'symbol': 'chainlink'},
        {'name': 'Stellar', 'symbol': 'stellar'},
        {'name': 'Bitcoin Cash', 'symbol': 'bitcoin-cash'},
        {'name': 'Binance Coin', 'symbol': 'binancecoin'},
        {'name': 'USD Coin', 'symbol': 'usd-coin'},
        {'name': 'Wrapped Bitcoin', 'symbol': 'wrapped-bitcoin'},
        {'name': 'Litecoin', 'symbol': 'litecoin'},
        {'name': 'Solana', 'symbol': 'solana'},
        {'name': 'Dogecoin', 'symbol': 'dogecoin'},
        {'name': 'Avalanche', 'symbol': 'avalanche'},
        {'name': 'Uniswap', 'symbol': 'uniswap'},
        {'name': 'Filecoin', 'symbol': 'filecoin'},
        {'name': 'Theta Network', 'symbol': 'theta-token'},
        {'name': 'Bitcoin SV', 'symbol': 'bitcoin-cash-sv'},
        {'name': 'Crypto.com Coin', 'symbol': 'crypto-com-coin'},
        {'name': 'TRON', 'symbol': 'tron'},
        {'name': 'Ethereum Classic', 'symbol': 'ethereum-classic'},
        {'name': 'Tezos', 'symbol': 'tezos'},
        {'name': 'FTX Token', 'symbol': 'ftx-token'},
        {'name': 'NEO', 'symbol': 'neo'},
        {'name': 'Cosmos', 'symbol': 'cosmos'},
        {'name': 'Monero', 'symbol': 'monero'},
        {'name': 'Algorand', 'symbol': 'algorand'},
        {'name': 'Aave', 'symbol': 'aave'},
        {'name': 'Compound', 'symbol': 'compound'},
        {'name': 'Dash', 'symbol': 'dash'}
    ]

    crypto_symbols = ','.join([crypto['symbol'] for crypto in cryptocurrencies])

    url = f'https://api.coingecko.com/api/v3/simple/price?ids={crypto_symbols}&vs_currencies=usd,eur'
    data = requests.get(url).json()

    for crypto in cryptocurrencies:
        symbol = crypto['symbol']
        if symbol in data:
            usd_price, eur_price = data.get(symbol, {}).get('usd', 0), data.get(symbol, {}).get('eur', 0)
            obj, created = Cryptocurrency.objects.get_or_create(
                symbol=symbol,
                defaults={'name': crypto['name'], 'price_usd': usd_price, 'price_eur': eur_price}
            )

            if not created:
                obj.price_usd = usd_price
                obj.price_eur = eur_price
                obj.save()
            print(f"{'Created' if created else 'Found'} {symbol} in database")
            print(f"Updated {symbol}: USD {obj.price_usd}, EUR {obj.price_eur}")

    return "Crypto prices updated"