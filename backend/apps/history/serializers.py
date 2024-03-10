from rest_framework import serializers

from backend.apps.history.models import HistoryExpense, HistoryIncome, HistoryTransfer
from datetime import datetime


class HistoryExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoryExpense
        fields = '__all__'


class StatisticViewSerializer(serializers.Serializer):
    week_summary = serializers.DictField(child=serializers.DecimalField(max_digits=20, decimal_places=2))

    def to_representation(self, instance):
        return instance


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


class HistoryTransferAutoDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoryTransfer
        fields = '__all__'


class ExpenseSummarySerializer(serializers.Serializer):
    categories = serializers.DictField()
    total_amount = serializers.DecimalField(max_digits=20, decimal_places=2)
