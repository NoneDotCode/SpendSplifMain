from django.contrib import admin
from backend.apps.cryptocurrency.models import Cryptocurrency

@admin.register(Cryptocurrency)
class CryptocurrencyAdmin(admin.ModelAdmin):
    list_display = ['name', 'symbol', 'price_usd', 'price_eur', 'last_updated']
