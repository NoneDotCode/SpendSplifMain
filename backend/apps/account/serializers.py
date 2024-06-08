from rest_framework import serializers

from backend.apps.account.models import Account

from backend.apps.space.models import Space

from backend.apps.converter.utils import convert_number_to_letter


class AccountSerializer(serializers.ModelSerializer):
    father_space = serializers.PrimaryKeyRelatedField(queryset=Space.objects.all(), required=False)
    id = serializers.IntegerField(required=False)
    balance_converted = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = ('id', 'title', 'balance', 'currency', 'included_in_total_balance', 'father_space', 'balance_converted')

    @staticmethod
    def get_balance_converted(obj):
        if obj.balance is not None:
            return convert_number_to_letter(obj.balance)
        return None

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['balance_converted'] = self.get_balance_converted(instance)
        return representation



class IncomeSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=20, decimal_places=2)
