from django.db import models
from colorfield.fields import ColorField

from backend.apps.category.constants import Icons

from backend.apps.space.models import Space


class Category(models.Model):
    title = models.CharField(max_length=24)
    spent = models.DecimalField(max_digits=12, decimal_places=2)
    limit = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    color = ColorField(format="hex")
    icon = models.CharField(choices=Icons.choices)
    father_space = models.ForeignKey(Space, verbose_name='father_space', on_delete=models.CASCADE)
    created = models.DateField(auto_now=True)

    def __str__(self):
        return self.title
