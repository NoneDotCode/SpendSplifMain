from rest_framework import serializers
from .models import Cryptocurrency

class CryptocurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Cryptocurrency
        fields = ['name', 'symbol', 'price_usd', 'price_eur', 'last_updated']