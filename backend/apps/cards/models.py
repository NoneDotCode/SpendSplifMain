from django.db import models
from django.conf import settings
from backend.apps.space.models import Space

class BankConnection(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    space = models.ForeignKey(Space, verbose_name='father_space', on_delete=models.CASCADE)
    bankConnectionName = models.CharField(max_length=255)
    currency = models.CharField(max_length=255, null=True, blank=True)
    balance = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    webFormId = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bank connection for {self.user.email}"


class UserSpace(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    space = models.ForeignKey(Space, verbose_name='father_space', on_delete=models.CASCADE)
    username = models.CharField(max_length=50, null=True, blank=True)
    password = models.CharField(max_length=50, null=True, blank=True)
    access_token = models.CharField(max_length=305, null=True, blank=True)
    refresh_token = models.CharField(max_length=305, null=True, blank=True)
    phone = models.CharField(max_length=255)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"User created for {self.phone}"


class ClientToken(models.Model):
    access_token = models.CharField(max_length=305, null=True, blank=True)
    refresh_token = models.CharField(max_length=305, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Tokens have updated {self.updated_at}"
