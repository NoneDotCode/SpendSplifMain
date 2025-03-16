from datetime import datetime

from django.db import models

from backend.apps.space.models import Space

from backend.apps.account.models import Account
from backend.apps.category.models import Category
from backend.apps.goal.models import Goal
from backend.apps.customuser.constants import Currency
from backend.apps.tink.models import TinkAccount
from backend.apps.cards.models import ConnectedAccounts
from backend.apps.category.constants import Icons
from django.utils import timezone


class HistoryExpense(models.Model):
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, choices=Currency.choices, default=Currency.UNITED_STATES_DOLLAR)
    amount_in_default_currency = models.DecimalField(max_digits=12, decimal_places=2)
    comment = models.CharField(max_length=300, null=True, blank=True)
    from_acc = models.JSONField(verbose_name='account', null=True, blank=True)
    to_cat = models.JSONField(verbose_name='to_cat', null=True)
    periodic_expense = models.BooleanField(default=False)
    new_balance = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    transaction_id = models.DecimalField(max_digits=12, decimal_places=0, null=True, blank=True)
    father_space = models.ForeignKey(Space, verbose_name='father_space', on_delete=models.CASCADE)
    bank_account = models.DecimalField(max_digits=12, decimal_places=0, null=True, blank=True)
    created = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # Если значение created не передано, устанавливаем текущую дату и время
        if not self.created:
            self.created = timezone.now()
        super().save(*args, **kwargs)


class HistoryIncome(models.Model):
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=4, choices=Currency.choices, default=Currency.UNITED_STATES_DOLLAR)
    amount_in_default_currency = models.DecimalField(max_digits=20, decimal_places=2)
    comment = models.CharField(max_length=300, blank=True)
    account = models.JSONField(verbose_name='account', null=True, blank=True)
    new_balance = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    transaction_id = models.DecimalField(max_digits=12, decimal_places=0, null=True, blank=True)
    father_space = models.ForeignKey(Space, verbose_name='father_space', on_delete=models.CASCADE)
    bank_account = models.DecimalField(max_digits=12, decimal_places=0, null=True, blank=True)
    created = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # Если значение created не передано, устанавливаем текущую дату и время
        if not self.created:
            self.created = timezone.now()
        super().save(*args, **kwargs)


class HistoryTransfer(models.Model):
    from_acc = models.JSONField(verbose_name="from_acc", null=True)
    to_acc = models.JSONField(verbose_name="to_acc", null=True)
    from_goal = models.JSONField(verbose_name='from_goal', null=True)
    to_goal = models.JSONField(verbose_name='to_goal', null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=4, choices=Currency.choices, default=Currency.UNITED_STATES_DOLLAR)
    amount_in_default_currency = models.DecimalField(max_digits=12, decimal_places=2)
    goal_is_done = models.BooleanField(null=True, default=False)
    goal_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    collected = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    father_space = models.ForeignKey(Space, verbose_name='father_space', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_created=True)
