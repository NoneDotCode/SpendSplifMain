from django.contrib import admin
from .models import Cryptocurrency

@admin.register(Cryptocurrency)
class CryptocurrencyAdmin(admin.ModelAdmin):
    list_display = ['name', 'symbol', 'price_usd', 'price_eur', 'last_updated']