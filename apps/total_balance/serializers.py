from rest_framework import serializers

from apps.total_balance.models import TotalBalance


class TotalBalanceSerializer (serializers.ModelSerializer):
    class Meta:
        model = TotalBalance
        fields = ('sum_of_balances', 'currency')
