from django.db import models

from apps.space.models import Space


class History(models.Model):
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    currency = models.CharField(max_length=3)
    comment = models.CharField(max_length=300)
    from_acc = models.CharField(max_length=24)
    to_cat = models.CharField(max_length=24, null=True)
    father_space = models.ForeignKey(Space, verbose_name='father_space', on_delete=models.CASCADE)
    time_create = models.DateTimeField(auto_now_add=True)
