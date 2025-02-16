from datetime import datetime, date, time

from rest_framework import serializers

from backend.apps.account.models import Account

from backend.apps.space.models import Space

from backend.apps.history.models import HistoryIncome, HistoryExpense

from django.utils import timezone

from backend.apps.converter.utils import convert_currencies
from backend.apps.converter.utils import convert_number_to_letter


class AccountSerializer(serializers.ModelSerializer):
    father_space = serializers.PrimaryKeyRelatedField(queryset=Space.objects.all(), required=False)
    id = serializers.IntegerField(required=False)
    spend = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    income = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    formatted_spend = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    formatted_income = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    balance_converted = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = ('id', 'title', 'balance', 'balance_converted', 'currency', 'included_in_total_balance',
                  'spend', 'income', 'formatted_spend', 'formatted_income', 'father_space')

    @staticmethod
    def get_balance_converted(obj):
        if obj.balance is not None:
            return convert_number_to_letter(obj.balance)
        return None
    def to_representation(self, instance):
        data = super().to_representation(instance)

        today = date.today()
        today = timezone.make_aware(datetime.combine(today, time.max))
        first_day_of_month = timezone.make_aware(datetime.combine(today.replace(day=1), time.min))

        account_data = {
            'id': instance.id,
            'title': instance.title,
            'currency': instance.currency,
            'included_in_total_balance': instance.included_in_total_balance,
            'father_space': instance.father_space.id
        }

        # Получение расходов и доходов за текущий месяц
        expenses_obj = HistoryExpense.objects.filter(
            created__range=[first_day_of_month, today],
            from_acc__id=instance.id
        )

        income_obj = HistoryIncome.objects.filter(
            created__range=[first_day_of_month, today],
            account__id=instance.id
        )

        spend_amount = sum(
            [convert_currencies(amount=exp.amount, from_currency=exp.currency, to_currency=data['currency']) for exp in
             expenses_obj]
        )
        income_amount = sum(
            [convert_currencies(amount=inc.amount, from_currency=inc.currency, to_currency=data['currency']) for inc in
             income_obj]
        )

        # Добавление данных о расходах и доходах в представление
        data['spend'] = spend_amount
        data['income'] = income_amount
        data['formatted_spend'] = convert_number_to_letter(spend_amount)
        data['formatted_income'] = convert_number_to_letter(income_amount)
        # Преобразование баланса и добавление в представление
        data['balance_converted'] = self.get_balance_converted(instance)

        return data

    def to_representation_without_balance(self, instance):
        data = self.to_representation(instance)
        if 'balance' in data:
            del data['balance']
        return data

    def equals_without_balance(self, instance1, instance2):
        data1 = self.to_representation_without_balance(instance1)
        data2 = self.to_representation_without_balance(instance2)
        return data1 == data2


class IncomeSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=20, decimal_places=2)
