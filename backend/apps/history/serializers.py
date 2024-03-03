from rest_framework import serializers

from backend.apps.history.models import HistoryExpense, HistoryIncome
from datetime import datetime

class HistoryExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoryExpense
        fields = ("amount", "currency", "comment", "from_acc", "to_cat", "created")


class HistoryIncomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoryIncome
        fields = ("amount", "currency", "comment", "account", "created")


class DailyIncomeSerializer(serializers.Serializer):
    date = serializers.DateField()
    total_income = serializers.DecimalField(max_digits=20, decimal_places=2)


class HistoryIncomeAutoDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoryIncome
        fields = '__all__'


class HistoryExpenseAutoDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoryExpense
        fields = '__all__'
