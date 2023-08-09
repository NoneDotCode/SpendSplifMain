from django.db import models

from apps.space.models import Space


class Account(models.Model):
    title = models.CharField(max_length=24)
    balance = models.DecimalField(max_digits=20, decimal_places=2)
    currency = models.CharField(max_length=4)
    included_in_total_balance = models.BooleanField(default=True)
    time_update = models.DateTimeField(auto_now=True)
    father_space = models.ForeignKey(Space, verbose_name='father_space', on_delete=models.CASCADE)

    def __str__(self):
        return self.title
