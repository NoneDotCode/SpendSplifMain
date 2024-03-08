from datetime import datetime

from django.db import models

from backend.apps.space.models import Space

from backend.apps.customuser.constants import Currency


class HistoryExpense(models.Model):
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    currency = models.CharField(max_length=3, choices=Currency.choices, default=Currency.UNITED_STATES_DOLLAR)
    comment = models.CharField(max_length=300, null=True, blank=True)
    from_acc = models.CharField(max_length=24)
    to_cat = models.CharField(max_length=24, null=True)
    periodic = models.BooleanField(default=False)
    father_space = models.ForeignKey(Space, verbose_name='father_space', on_delete=models.CASCADE)
    created = models.DateTimeField(default=datetime.now)


class HistoryIncome(models.Model):
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    currency = models.CharField(max_length=4, choices=Currency.choices, default=Currency.UNITED_STATES_DOLLAR)
    comment = models.CharField(max_length=300, null=True, blank=True)
    account = models.CharField(max_length=24)
    father_space = models.ForeignKey(Space, verbose_name='father_space', on_delete=models.CASCADE)
    created = models.DateTimeField(default=datetime.now)


class HistoryTransfer(models.Model):
    from_acc = models.CharField(blank=True)
    to_acc = models.CharField(blank=True)
    to_goal = models.CharField(blank=True)
    from_goal = models.CharField(blank=True)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    currency = models.CharField(max_length=4, choices=Currency.choices, default=Currency.UNITED_STATES_DOLLAR)
    father_space = models.ForeignKey(Space, verbose_name='father_space', on_delete=models.CASCADE)
    created = models.DateTimeField(default=datetime.now)
