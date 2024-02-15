from backend.apps.history.models import HistoryExpense, HistoryIncome

from django.contrib import admin

admin.site.register(HistoryExpense)
admin.site.register(HistoryIncome)
