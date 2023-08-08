from rest_framework import serializers

from .models import Account


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ('title', 'balance', 'currency', 'included_in_total_balance', 'father_space')
