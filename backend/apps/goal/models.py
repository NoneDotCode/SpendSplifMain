from django.db import models

from backend.apps.space.models import Space


class Goal(models.Model):
    title = models.CharField(max_length=40)
    goal = models.DecimalField(max_digits=12, decimal_places=2)
    collected = models.DecimalField(max_digits=12, decimal_places=2)
    father_space = models.ForeignKey(Space, verbose_name='father_space', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
