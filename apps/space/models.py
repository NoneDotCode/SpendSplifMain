from django.db import models

from apps.customuser.models import CustomUser
# Create your models here.


class Space(models.Model):
    title = models.CharField(max_length=24)
    owner = models.ForeignKey(CustomUser, verbose_name='owner', on_delete=models.CASCADE)

    def __str__(self):
        return self.title
