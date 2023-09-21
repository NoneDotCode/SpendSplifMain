from django.db import models

from apps.space.models import Space


class Category(models.Model):
    title = models.CharField(max_length=24)
    icon = models.FilePathField()
    spent = models.DecimalField(max_digits=20, decimal_places=2)
    limit = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    father_space = models.ForeignKey(Space, verbose_name='father_space', on_delete=models.CASCADE)

    def __str__(self):
        return self.title
