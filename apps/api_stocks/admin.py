from django.contrib import admin
from .models import Stock

# @admin.register(Stock)
# class StocksAdmin(admin.ModelAdmin):
#     list_display = ['name', 'symbol', 'price', 'last_updated']