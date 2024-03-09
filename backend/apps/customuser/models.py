import random

from django.contrib.auth.models import AbstractUser, Group, Permission, BaseUserManager
from django.core.validators import MaxValueValidator
from django.db import models
from rest_framework.exceptions import ValidationError

from django.core.mail import send_mail
from django.utils.crypto import get_random_string


from backend.apps.customuser.constants import Language, Currency


class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")

        existing_tags = set(CustomUser.objects.filter(username=username).values_list('tag', flat=True))
        available_tags = set(range(1, 10000)) - existing_tags
        if not available_tags:
            raise ValidationError("Too many people registered with this username, try another please.")

        tag = random.choice(list(available_tags))
        email = self.normalize_email(email)
        user = self.model(email=email, tag=tag, **extra_fields)

        user.set_password(password)
        user.save(using=self._db)

    def create_superuser(self, email, password=None, username=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        existing_tags = set(CustomUser.objects.filter(username=username).values_list('tag', flat=True))
        available_tags = set(range(1, 10000)) - existing_tags
        if not available_tags:
            raise ValidationError("Too many people registered with this username, try another please.")

        tag = random.choice(list(available_tags))

        return self.create_user(email, password, tag=tag, **extra_fields)


class CustomUser(AbstractUser):
    """
    Model class representing a custom user.
    """

    language = models.CharField(max_length=20, choices=Language.choices, default=Language.ENGLISH)
    tag = models.PositiveIntegerField(null=True, blank=True, validators=[MaxValueValidator(9999)])
    email = models.EmailField(unique=True, null=False, blank=False)
    username = models.CharField(max_length=150, unique=False, null=False, blank=False)
    currency = models.CharField(max_length=4, choices=Currency.choices, default=Currency.UNITED_STATES_DOLLAR)

    verify_code = models.CharField(max_length=12, blank=True, null=True)

    password_reset_code = models.PositiveIntegerField(blank=True, null=True)

    # The following fields are required when creating a user.
    groups = models.ManyToManyField(Group, related_name="custom_users")
    user_permissions = models.ManyToManyField(Permission, related_name="custom_users")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def save(self, *args, **kwargs):
        """
        Save the user to the database.
        """
        if not self.tag:
            existing_tags = set(CustomUser.objects.filter(username=self.username).values_list('tag', flat=True))
            available_tags = set(range(1, 10000)) - existing_tags

            if not available_tags:
                raise ValidationError("Too many people registered with this username, try another please.")

            self.tag = random.choice(list(available_tags))

        if not self.id:
            self.set_password(self.password)

        if self.verify_code is None:
            verify_code = get_random_string(length=8)
            self.verify_code = verify_code
            self.is_active = False

            subject = 'Email Verification'
            message = f'Your verification code: {verify_code}'
            from_email = 'spendsplif@gmail.com'
            to_email = self.email
            send_mail(subject, message, from_email, [to_email])

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} - {self.email}"
