from django.db import models

from apps.space.models import Space


class Category(models.Model):
    title = models.CharField(max_length=24)
    icon = models.FilePathField()
    minus = models.DecimalField(max_digits=20, decimal_places=2)
    limit = models.DecimalField(max_digits=20, decimal_places=2)
    father_space = models.ForeignKey(Space, verbose_name='father_space', on_delete=models.CASCADE)
    time_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
