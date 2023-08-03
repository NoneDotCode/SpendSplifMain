from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator
from django.db import models

from apps.customuser.constants import Language


class CustomUser(AbstractUser):
    """
    Model class representing a custom user.
    """

    language = models.CharField(max_length=20, choices=Language.choices, default=Language.ENGLISH)
    tag = models.PositiveIntegerField(null=True, blank=True, validators=[MaxValueValidator(9999)])
