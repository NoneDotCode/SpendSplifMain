from rest_framework import serializers

from backend.apps.history.models import HistoryExpense, HistoryIncome


class HistoryExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoryExpense
        fields = ("amount", "currency", "comment", "from_acc", "to_cat", "created")


class HistoryIncomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoryIncome
        fields = ("amount", "currency", "comment", "account", "created")
