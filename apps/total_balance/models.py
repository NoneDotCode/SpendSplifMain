from django.db import models

from apps.account.models import Account

from apps.space.models import Space


class TotalBalance(models.Model):
    sum_of_balances = models.DecimalField(max_digits=20, decimal_places=2)
    currency = models.CharField(max_length=4)
    father_space = models.OneToOneField(Space, verbose_name='father_space', on_delete=models.CASCADE)
