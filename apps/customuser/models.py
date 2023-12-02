import random

from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.validators import MaxValueValidator
from django.db import models

from apps.customuser.constants import Language, Currency


class CustomUser(AbstractUser):
    """
    Model class representing a custom user.
    """

    language = models.CharField(max_length=20, choices=Language.choices, default=Language.ENGLISH)
    tag = models.PositiveIntegerField(null=True, blank=True, validators=[MaxValueValidator(9999)])
    email = models.EmailField(unique=True, null=False, blank=False)
    username = models.CharField(max_length=150, unique=False, null=False, blank=False)
    currency = models.CharField(max_length=4, choices=Currency.choices, default=Currency.UNITED_STATES_DOLLAR)

    verify_code = models.PositiveIntegerField(null=True, blank=True)
    verify_email = models.BooleanField(default=False)

    password_reset_code = models.PositiveIntegerField(blank=True, null=True)

    # The following fields are required when creating a user.
    groups = models.ManyToManyField(Group, related_name="custom_users")
    user_permissions = models.ManyToManyField(Permission, related_name="custom_users")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]


    @staticmethod
    def generate_random_tag():
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


    def __str__(self):
        return f"{self.username} - {self.email}"