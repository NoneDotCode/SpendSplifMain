from django.db import models

from backend.apps.account.models import Account

from backend.apps.space.models import Space

from backend.apps.customuser.constants import Currency


class TotalBalance(models.Model):
    balance = models.DecimalField(max_digits=20, decimal_places=2)
    currency = models.CharField(max_length=4, choices=Currency.choices, default=Currency.UNITED_STATES_DOLLAR)
    father_space = models.OneToOneField(Space, verbose_name='father_space', on_delete=models.CASCADE)
