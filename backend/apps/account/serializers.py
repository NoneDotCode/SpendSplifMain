import datetime

from rest_framework import serializers

from backend.apps.account.models import Account

from backend.apps.space.models import Space

from backend.apps.history.models import HistoryIncome, HistoryExpense

from django.utils import timezone

from backend.apps.converter.utils import convert_currencies

class AccountSerializer(serializers.ModelSerializer):
    father_space = serializers.PrimaryKeyRelatedField(queryset=Space.objects.all(), required=False)
    id = serializers.IntegerField(required=False)
    spend = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    income = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)

    class Meta:
        model = Account
        fields = ('id', 'title', 'balance', 'currency', 'included_in_total_balance', 'father_space', 'spend', 'income')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        today = datetime.date.today()
        
        today = timezone.make_aware(datetime.datetime.combine(today, datetime.time.max))
        first_day_of_month = timezone.make_aware(datetime.datetime.combine(today.replace(day=1), datetime.time.min))


        expenses_obj = HistoryExpense.objects.filter(created__range=[first_day_of_month, today]).filter(from_acc=data['id'])
        income_obj = HistoryIncome.objects.filter(created__range=[first_day_of_month, today]).filter(account=data['id'])
        
        spend_amount = sum([convert_currencies(amount=exp.amount, from_currency=exp.currency, to_currency=data['currency']) for exp in expenses_obj])
        income_amount = sum([convert_currencies(amount=inc.amount, from_currency=inc.currency, to_currency=data['currency']) for inc in income_obj])

        data['spend'] = spend_amount
        data['income'] = income_amount

        return data



class IncomeSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=20, decimal_places=2)
