from celery import shared_task
from rest_framework import status
from rest_framework.response import Response

from apps.account.models import Account
from apps.category.models import Category
from apps.converter.utils import convert_currencies
from apps.history.models import HistoryExpense
from apps.total_balance.models import TotalBalance


@shared_task(bind=True)
def clear_all_spent(self):
    all_categories = Category.objects.all()
    for category in all_categories:
        category.spent = 0
        category.save()
    return "All spent cleared"
