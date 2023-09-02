from rest_framework import serializers

from apps.account.models import Account


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ('title', 'balance', 'currency', 'included_in_total_balance', 'father_space')
        read_only_fields = ('father_space',)
