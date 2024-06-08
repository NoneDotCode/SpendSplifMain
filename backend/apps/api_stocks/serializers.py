from rest_framework import serializers
from .models import Stock

class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ['name', 'symbol', 'price_usd', 'price_eur', 'last_updated']
