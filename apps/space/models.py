from django.db import models

from apps.customuser.models import CustomUser


class Space(models.Model):
    """
    Model representing a space.
    """

    title = models.CharField(max_length=24)
    owner = models.ForeignKey(CustomUser, verbose_name="owner", on_delete=models.CASCADE)

    def __str__(self):
        return self.title
