from rest_framework import serializers

from apps.total_balance.models import TotalBalance


class TotalBalanceSerializer (serializers.ModelSerializer):
    balance = serializers.DecimalField(required=False, max_digits=20, decimal_places=2)

    class Meta:
        model = TotalBalance
        fields = ('balance', 'currency')
