from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.total_balance.utils import convert_currency

from apps.account.models import Account
from apps.total_balance.models import TotalBalance


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
    else:
        t_balance = TotalBalance.objects.get(father_space_id=instance.father_space_id)
        currency = t_balance.currency
        converted_balance = 0
        for i in accounts:
            converted_balance += convert_currency(i.currency, currency, int(i.balance))
        t_balance.sum_of_balances = converted_balance
        t_balance.save()
        return t_balance