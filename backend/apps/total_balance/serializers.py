from rest_framework import serializers
from backend.apps.total_balance.models import TotalBalance
from backend.apps.converter.utils import convert_number_to_letter

class TotalBalanceSerializer(serializers.ModelSerializer):
    total_expenses_this_month = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total_income_this_month = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    currency = serializers.SerializerMethodField()
    formatted_balance = serializers.SerializerMethodField()

    class Meta:
        model = TotalBalance
        fields = ('balance', 'formatted_balance', 'currency', 'total_expenses_this_month', 'total_income_this_month')

    @staticmethod
    def get_currency(obj):
        return obj.father_space.currency if obj.father_space else None

    @staticmethod
    def get_formatted_balance(obj):
        return convert_number_to_letter(float(obj.balance))
