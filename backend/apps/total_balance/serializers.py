from rest_framework import serializers

from backend.apps.total_balance.models import TotalBalance


class TotalBalanceSerializer (serializers.ModelSerializer):
    balance = serializers.DecimalField(required=False, max_digits=20, decimal_places=2)
    currency = serializers.SerializerMethodField()

    class Meta:
        model = TotalBalance
        fields = ('balance', 'currency')

    @staticmethod
    def get_currency(obj):
        return obj.father_space.currency if obj.father_space else None
