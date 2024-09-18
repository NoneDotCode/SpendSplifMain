from rest_framework import serializers
from django.utils import timezone
from django.db.models import Sum

from backend.apps.history.models import HistoryExpense, HistoryIncome
from backend.apps.total_balance.models import TotalBalance
from backend.apps.converter.utils import convert_number_to_letter


class TotalBalanceSerializer(serializers.ModelSerializer):
    currency = serializers.SerializerMethodField()
    formatted_balance = serializers.SerializerMethodField()
    total_income_this_month = serializers.SerializerMethodField()
    total_expenses_this_month = serializers.SerializerMethodField()

    class Meta:
        model = TotalBalance
        fields = ('balance', 'formatted_balance', 'currency', 'total_expenses_this_month', 'total_income_this_month')

    @staticmethod
    def get_currency(obj):
        return obj.father_space.currency if obj.father_space else None

    @staticmethod
    def get_formatted_balance(obj):
        return convert_number_to_letter(float(obj.balance))

    @staticmethod
    def get_total_expenses_this_month(obj):
        today = timezone.now()
        start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        total_expenses = HistoryExpense.objects.filter(
            father_space_id=obj.father_space.id,
            created__gte=start_of_month
        ).aggregate(total=Sum('amount_in_default_currency'))['total'] or 0

        return total_expenses

    @staticmethod
    def get_total_income_this_month(obj):
        today = timezone.now()
        start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        total_income = HistoryIncome.objects.filter(
            father_space_id=obj.father_space.id,
            created__gte=start_of_month
        ).aggregate(total=Sum('amount_in_default_currency'))['total'] or 0

        return total_income
