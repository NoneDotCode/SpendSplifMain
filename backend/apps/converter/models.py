from django.db import models

from backend.apps.customuser.constants import Currency as CurrencyConstants


class Currency(models.Model):
    currency = models.CharField(max_length=30)
    iso_code = models.CharField(max_length=4, choices=CurrencyConstants.choices,
                                default=CurrencyConstants.UNITED_STATES_DOLLAR)
    euro = models.DecimalField(max_digits=10, decimal_places=2)
    time_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"1EUR = {self.euro}{self.iso_code}"
