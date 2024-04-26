import requests
from celery import shared_task
from backend.apps.cryptocurrency.models import Cryptocurrency
import logging

logger = logging.getLogger(__name__)

@shared_task()
def update_crypto_prices():
    logger.info("Task started: update_crypto_prices")    
    cryptocurrencies = [
    {'name': 'Bitcoin', 'symbol': 'bitcoin', 'code': 'BTC'},
    {'name': 'Ethereum', 'symbol': 'ethereum', 'code': 'ETH'},
    {'name': 'Litecoin', 'symbol': 'litecoin', 'code': 'LTC'},
    {'name': 'Ripple', 'symbol': 'ripple', 'code': 'XRP'},
    {'name': 'Cardano', 'symbol': 'cardano', 'code': 'ADA'},
    {'name': 'Polkadot', 'symbol': 'polkadot', 'code': 'DOT'},
    {'name': 'Chainlink', 'symbol': 'chainlink', 'code': 'LINK'},
    {'name': 'Stellar', 'symbol': 'stellar', 'code': 'XLM'},
    {'name': 'Bitcoin Cash', 'symbol': 'bitcoin-cash', 'code': 'BCH'},
    {'name': 'Binance Coin', 'symbol': 'binancecoin', 'code': 'BNB'},
    {'name': 'USD Coin', 'symbol': 'usd-coin', 'code': 'USDC'},
    {'name': 'Wrapped Bitcoin', 'symbol': 'wrapped-bitcoin', 'code': 'WBTC'},
    {'name': 'Litecoin', 'symbol': 'litecoin', 'code': 'LTC'},
    {'name': 'Solana', 'symbol': 'solana', 'code': 'SOL'},
    {'name': 'Dogecoin', 'symbol': 'dogecoin', 'code': 'DOGE'},
    {'name': 'Avalanche', 'symbol': 'avalanche', 'code': 'AVAX'},
    {'name': 'Uniswap', 'symbol': 'uniswap', 'code': 'UNI'},
    {'name': 'Filecoin', 'symbol': 'filecoin', 'code': 'FIL'},
    {'name': 'Theta Network', 'symbol': 'theta-token', 'code': 'THETA'},
    {'name': 'Bitcoin SV', 'symbol': 'bitcoin-cash-sv', 'code': 'BSV'},
    {'name': 'Crypto.com Coin', 'symbol': 'crypto-com-coin', 'code': 'CRO'},
    {'name': 'TRON', 'symbol': 'tron', 'code': 'TRX'},
    {'name': 'Ethereum Classic', 'symbol': 'ethereum-classic', 'code': 'ETC'},
    {'name': 'Tezos', 'symbol': 'tezos', 'code': 'XTZ'},
    {'name': 'FTX Token', 'symbol': 'ftx-token', 'code': 'FTT'},
    {'name': 'NEO', 'symbol': 'neo', 'code': 'NEO'},
    {'name': 'Cosmos', 'symbol': 'cosmos', 'code': 'ATOM'},
    {'name': 'Monero', 'symbol': 'monero', 'code': 'XMR'},
    {'name': 'Algorand', 'symbol': 'algorand', 'code': 'ALGO'},
    {'name': 'Aave', 'symbol': 'aave', 'code': 'AAVE'},
    {'name': 'Compound', 'symbol': 'compound', 'code': 'COMP'},
    {'name': 'Dash', 'symbol': 'dash', 'code': 'DASH'}
]

    crypto_symbols = ','.join([crypto['symbol'] for crypto in cryptocurrencies])

    url = f'https://api.coingecko.com/api/v3/simple/price?ids={crypto_symbols}&vs_currencies=usd,eur'
    data = requests.get(url).json()

    for crypto in cryptocurrencies:
        symbol = crypto['symbol']
        if symbol in data:
            usd_price, eur_price = data.get(symbol, {}).get('usd', 0), data.get(symbol, {}).get('eur', 0)
            symbol = crypto['code']
            obj, created = Cryptocurrency.objects.get_or_create(symbol=symbol, defaults={'name': crypto['name'], 'price_usd': usd_price, 'price_eur': eur_price}
            )

            if not created:
                obj.price_usd = usd_price
                obj.price_eur = eur_price
                obj.symbol = symbol
                obj.save()
            print(f"{'Created' if created else 'Found'} {symbol} in database")
            print(f"Updated {symbol}: USD {obj.price_usd}, EUR {obj.price_eur}")

    return "Crypto prices updated"
