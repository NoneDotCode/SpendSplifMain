from rest_framework import serializers

from apps.account.models import Account

from apps.space.models import Space


class AccountSerializer(serializers.ModelSerializer):
    father_space = serializers.PrimaryKeyRelatedField(queryset=Space.objects.all(), required=False)

    class Meta:
        model = Account
        fields = ('title', 'balance', 'currency', 'included_in_total_balance', 'father_space')


class IncomeSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=20, decimal_places=2)

