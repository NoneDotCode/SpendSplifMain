from rest_framework import serializers

from backend.apps.account.models import Account

from backend.apps.space.models import Space


class AccountSerializer(serializers.ModelSerializer):
    father_space = serializers.PrimaryKeyRelatedField(queryset=Space.objects.all(), required=False)
    id = serializers.IntegerField(required=False)

    class Meta:
        model = Account
        fields = ('id', 'title', 'balance', 'currency', 'included_in_total_balance', 'father_space')


class IncomeSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=20, decimal_places=2)
