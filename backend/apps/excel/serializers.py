from rest_framework import serializers
from backend.apps.history.models import HistoryExpense, HistoryIncome, HistoryTransfer


class HistoryExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoryExpense
        fields = ['amount', 'comment', 'created', 'from_acc', 'to_cat']


class HistoryIncomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoryIncome
        fields = ['amount', 'comment', 'created', 'account']
