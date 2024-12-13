import random

from django.contrib.auth.models import AbstractUser, Group, Permission, BaseUserManager
from django.core.validators import MaxValueValidator
from django.db import models
from rest_framework.exceptions import ValidationError
from django.contrib.postgres.fields import ArrayField

from django.core.mail import send_mail
from django.utils.crypto import get_random_string

from backend.apps.customuser.utils import send_code_for_verify_email
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
    
    roles_choices = [
        ("free", "Free"),
        ("business_plan", "Business plan"),
        ("business_lic", "Business license"),
        ("sponsor", "Sponsor"),
        ("employee", "Employee"),
        ("premium/pre", "Premium/Pre"),
        ("standard/pre", "Standard/Pre")
    ]
    roles = ArrayField(
        models.CharField(max_length=15, choices=roles_choices), 
        default=["free"], 
        blank=True
        )

    new_email = models.EmailField(null=True, blank=True)
    new_password = models.CharField(max_length=24, null=True, blank=True)

    verify_code = models.CharField(max_length=12, blank=True, null=True)
    code_from_new_email = models.CharField(max_length=12, blank=True, null=True)

    password_reset_code = models.CharField(max_length=12, blank=True, null=True)

    # The following fields are required when creating a user.
    groups = models.ManyToManyField(Group, related_name="custom_users")
    user_permissions = models.ManyToManyField(Permission, related_name="custom_users")
    verify_new_password = models.CharField(max_length=12, blank=True,null=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def add_role(self, role, *args, **kwargs):
        if role not in [choice[0] for choice in self.roles_choices]:
            raise ValueError(f"Role {role} is not a valide one.")
        if role != self.roles[0]:
            self.roles[0] = role
            self.save()

    def send_password_reset_code(self):
        reset_code = get_random_string(length=8)
        self.password_reset_code = reset_code
        self.save()

        send_mail(
            'Password Reset Code',
            f'Your password reset code is: {reset_code}',
            'noreply@yourapp.com',
            [self.email],
            fail_silently=False,
        )

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
            send_code_for_verify_email(email=self.email, code=verify_code, flag="registration")

        if self.new_email:
            verify_code = get_random_string(length=8)
            code_from_new_email = get_random_string(length=8)
            self.verify_code = verify_code
            self.code_from_new_email = code_from_new_email

            send_code_for_verify_email(email=self.new_email, code=code_from_new_email, flag="change email")
            send_code_for_verify_email(email=self.email, code=verify_code, flag="change email")

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} - {self.email}"
