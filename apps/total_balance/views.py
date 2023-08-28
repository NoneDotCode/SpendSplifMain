from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import render
from rest_framework import generics

from apps.account.models import Account
from apps.total_balance.models import TotalBalance
from apps.total_balance.serializers import TotalBalanceSerializer


def CurrencyTotalBalance():



@receiver(post_save, sender=Account)
def update_total_balance(sender, instance, **kwargs):
    accounts = Account.objects.filter(father_space_id=instance.father_space_id)
    currency = accounts.first().currency
    father_space_id = accounts.first().father_space_id
    if all(account.currency == currency for account in accounts):
        sum_of_balances = sum(account.balance for account in accounts)
        total_balance = TotalBalance.objects.filter(
            currency=currency, father_space_id=father_space_id
        ).first()
        total_balance = TotalBalance.objects.filter(father_space_id=father_space_id).first()
        if total_balance:
            if total_balance.currency != currency:
                total_balance.currency = currency
            if total_balance.sum_of_balances != sum_of_balances:
                total_balance.sum_of_balances = sum_of_balances
            total_balance.save()
        else:
            total_balance = TotalBalance.objects.create(currency=currency, sum_of_balances=sum_of_balances,
                                                        father_space_id=father_space_id)
        return total_balance


class TotalBalanceView(generics.ListAPIView):
    serializer_class = TotalBalanceSerializer

    def get_queryset(self):
        return TotalBalance.objects.filter(father_space_id=self.request.data.get('father_space_id'))
