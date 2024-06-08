from django.db import models

from backend.apps.account.models import Account

from backend.apps.space.models import Space


class TotalBalance(models.Model):
    balance = models.DecimalField(max_digits=12, decimal_places=2)
    father_space = models.OneToOneField(Space, verbose_name='father_space', on_delete=models.CASCADE)
