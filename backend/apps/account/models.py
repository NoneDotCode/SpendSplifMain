from django.db import models

from backend.apps.space.models import Space

from backend.apps.customuser.constants import Currency


class Account(models.Model):
    title = models.CharField(max_length=24)
    balance = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=4, choices=Currency.choices, default=Currency.UNITED_STATES_DOLLAR)
    included_in_total_balance = models.BooleanField(default=True)
    father_space = models.ForeignKey(Space, verbose_name='father_space', on_delete=models.CASCADE)

    def __str__(self):
        return self.title
