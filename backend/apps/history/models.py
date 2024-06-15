from datetime import datetime

from django.db import models

from backend.apps.space.models import Space

from backend.apps.account.models import Account
from backend.apps.category.models import Category
from backend.apps.goal.models import Goal
from backend.apps.customuser.constants import Currency

from backend.apps.category.constants import Icons


class HistoryExpense(models.Model):
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, choices=Currency.choices, default=Currency.UNITED_STATES_DOLLAR)
    amount_in_default_currency = models.DecimalField(max_digits=12, decimal_places=2)
    comment = models.CharField(max_length=300, null=True, blank=True)
    from_acc = models.ForeignKey(Account, verbose_name='from_acc', on_delete=models.DO_NOTHING)
    to_cat = models.ForeignKey(Category, verbose_name='to_cat', on_delete=models.DO_NOTHING)
    periodic_expense = models.BooleanField(default=False)
    new_balance = models.DecimalField(max_digits=12, decimal_places=2)
    father_space = models.ForeignKey(Space, verbose_name='father_space', on_delete=models.CASCADE)
    created = models.DateTimeField(default=datetime.now)


class HistoryIncome(models.Model):
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=4, choices=Currency.choices, default=Currency.UNITED_STATES_DOLLAR)
    amount_in_default_currency = models.DecimalField(max_digits=20, decimal_places=2)
    comment = models.CharField(max_length=300, blank=True)
    account = models.ForeignKey(Account, verbose_name='account', on_delete=models.DO_NOTHING)
    new_balance = models.DecimalField(max_digits=12, decimal_places=2)
    father_space = models.ForeignKey(Space, verbose_name='father_space', on_delete=models.CASCADE)
    created = models.DateTimeField(default=datetime.now)


class HistoryTransfer(models.Model):
    from_acc = models.ForeignKey(Account, related_name='transfers_from', verbose_name='from_acc',
                                 on_delete=models.DO_NOTHING)
    to_acc = models.ForeignKey(Account, related_name='transfers_to', verbose_name='to_acc', on_delete=models.DO_NOTHING)
    from_goal = models.ForeignKey(Goal, related_name='transfers_from_goal', verbose_name='from_goal',
                                  on_delete=models.DO_NOTHING)
    to_goal = models.ForeignKey(Goal, related_name='transfers_to_goal', verbose_name='to_goal',
                                on_delete=models.DO_NOTHING)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=4, choices=Currency.choices, default=Currency.UNITED_STATES_DOLLAR)
    amount_in_default_currency = models.DecimalField(max_digits=12, decimal_places=2)
    goal_is_done = models.BooleanField(null=True, default=False)
    goal_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    collected = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    father_space = models.ForeignKey(Space, verbose_name='father_space', on_delete=models.CASCADE)
    created = models.DateTimeField(default=datetime.now)
