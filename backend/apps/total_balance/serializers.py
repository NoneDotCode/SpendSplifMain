from rest_framework import serializers

from backend.apps.total_balance.models import TotalBalance
from backend.apps.converter.utils import convert_number_to_letter


class TotalBalanceSerializer (serializers.ModelSerializer):
    currency = serializers.SerializerMethodField()
    formatted_balance = serializers.SerializerMethodField()

    class Meta:
        model = TotalBalance
        fields = ('balance', 'formatted_balance', 'currency')

    @staticmethod
    def get_currency(obj):
        return obj.father_space.currency if obj.father_space else None

    @staticmethod
    def get_formatted_balance(obj):
        return convert_number_to_letter(float(obj.balance))
