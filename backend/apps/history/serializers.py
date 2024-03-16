from rest_framework import serializers

from backend.apps.history.models import HistoryExpense, HistoryIncome, HistoryTransfer
from datetime import datetime


class HistoryExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoryExpense
        fields = '__all__'


class StatisticViewSerializer(serializers.Serializer):
    Statistics = serializers.DictField()


class CategoryViewSerializer(serializers.Serializer):
    week_summary = serializers.DictField(child=serializers.DecimalField(max_digits=20, decimal_places=2))

    def to_representation(self, instance):
        return instance


class ExpensesViewSerializer(serializers.Serializer):
    week = serializers.DictField()
    week_percent = serializers.DictField()
    analyze_week = serializers.CharField()
    month = serializers.DictField()
    month_percent = serializers.DictField()
    analyze_month = serializers.CharField()
    three_month = serializers.DictField()
    three_month_percent = serializers.DictField()
    analyze_three_month = serializers.CharField()
    year = serializers.DictField()
    year_percent = serializers.DictField()
    analyze_year = serializers.CharField()


class GoalTransferStatisticSerializer(serializers.Serializer):
    week = serializers.DictField(child=serializers.CharField())
    week_percent = serializers.DictField(child=serializers.CharField())
    month = serializers.DictField(child=serializers.CharField())
    month_percent = serializers.DictField(child=serializers.CharField())
    three_month = serializers.DictField(child=serializers.CharField(), required=False)
    three_month_percent = serializers.DictField(child=serializers.CharField(), required=False)
    year = serializers.DictField(child=serializers.CharField(), required=False)
    year_percent = serializers.DictField(child=serializers.CharField(), required=False)


class IncomeStatisticViewSerializer(serializers.Serializer):
    Period = serializers.DictField(child=serializers.DictField())

    def to_representation(self, instance):
        return instance


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
        fields = ("amount", "currency", "amount_in_default_currency", "comment",
                  "from_acc", "to_cat", "periodic", "father_space", "created")


class HistoryTransferAutoDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoryTransfer
        fields = '__all__'


class ExpenseSummarySerializer(serializers.Serializer):
    categories = serializers.DictField()
    total_amount = serializers.DecimalField(max_digits=20, decimal_places=2)
