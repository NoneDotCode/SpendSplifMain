from rest_framework import serializers

from backend.apps.history.models import HistoryExpense, HistoryIncome, HistoryTransfer
from datetime import datetime


class CombinedHistorySerializer(serializers.Serializer):
    type = serializers.CharField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    currency = serializers.CharField(max_length=4)
    comment = serializers.CharField(max_length=300, allow_blank=True)
    account = serializers.CharField()
    created_date = serializers.DateField()
    created_time = serializers.TimeField()
    from_acc = serializers.CharField(required=False)
    to_cat_title = serializers.CharField(required=False)
    to_cat_icon = serializers.CharField(required=False)
    periodic_expense = serializers.BooleanField(required=False)
    new_balance = serializers.DecimalField(max_digits=12, decimal_places=2)


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
    Week = serializers.DictField()
    Week_Percent = serializers.DictField()
    Analyze_Week = serializers.CharField()
    Month = serializers.DictField()
    Month_Percent = serializers.DictField()
    Analyze_Month = serializers.CharField()
    Three_month = serializers.DictField()
    Three_month_Percent = serializers.DictField()
    Analyze_Three_month = serializers.CharField()
    Year = serializers.DictField()
    Year_Percent = serializers.DictField()
    Analyze_Year = serializers.CharField()


class GoalTransferStatisticSerializer(serializers.Serializer):
    Week = serializers.DictField()
    Week_Percent = serializers.DictField()
    Analyze_Week = serializers.CharField()
    Month = serializers.DictField()
    Month_Percent = serializers.DictField()
    Analyze_Month = serializers.CharField()
    Three_month = serializers.DictField()
    Three_month_Percent = serializers.DictField()
    Analyze_Three_month = serializers.CharField()
    Year = serializers.DictField()
    Year_Percent = serializers.DictField()
    Analyze_Year = serializers.CharField()


class RecurringPaymentsStatisticSerializer(serializers.Serializer):
    week = serializers.DictField(child=serializers.DictField(), allow_empty=True)
    month = serializers.DictField(child=serializers.DictField(), allow_empty=True)
    three_month = serializers.DictField(child=serializers.DictField(), allow_empty=True)
    year = serializers.DictField(child=serializers.DictField(), allow_empty=True)


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
                  "from_acc", "to_cat", "periodic_expense", "new_balance", "father_space", "created")


class HistoryTransferAutoDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoryTransfer
        fields = '__all__'


class ExpenseSummarySerializer(serializers.Serializer):
    categories = serializers.DictField()
    total_amount = serializers.DecimalField(max_digits=20, decimal_places=2)

class CombinedStatisticSerializer(serializers.Serializer):
    Expenses = serializers.DictField()
    Balance = serializers.DictField()
    Incomes = serializers.DictField()
    Goals = serializers.DictField()
    Recurring_Payments = serializers.DictField()
    Categories = serializers.DictField()
