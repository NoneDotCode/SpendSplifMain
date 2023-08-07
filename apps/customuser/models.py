import random

from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.validators import MaxValueValidator
from django.db import models

from apps.customuser.constants import Language


class CustomUser(AbstractUser):
    """
    Model class representing a custom user.
    """

    language = models.CharField(max_length=20, choices=Language.choices, default=Language.ENGLISH)
    tag = models.PositiveIntegerField(null=True, blank=True, validators=[MaxValueValidator(9999)])
    email = models.EmailField(unique=True, null=False, blank=False)

    # The following fields are required when creating a user.
    groups = models.ManyToManyField(Group, related_name="custom_users")
    user_permissions = models.ManyToManyField(Permission, related_name="custom_users")

    def generate_random_tag(self):
        return random.randint(1, 9999)

    def save(self, *args, **kwargs):
        """
        Save the user to the database.
        """
        if not self.tag:
            self.tag = self.generate_random_tag()
        if not self.id:
            self.set_password(self.password)
        super().save(*args, **kwargs)
