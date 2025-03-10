from django.db import models
from django.conf import settings
from backend.apps.space.models import Space
from backend.apps.customuser.models import CustomUser

class BankConnection(models.Model):
    user = models.ForeignKey(CustomUser, verbose_name='user', on_delete=models.CASCADE)
    space = models.ForeignKey(Space, verbose_name='father_space', on_delete=models.CASCADE)
    bankConnectionName = models.CharField(max_length=255)
    webFormId = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bank connected"


class ConnectedAccounts(models.Model):
    bankConnection = models.ForeignKey(BankConnection, verbose_name='bank_connection', null=True, blank=True, on_delete=models.CASCADE)
    accountIban = models.CharField(max_length=255, null=True, blank=True)
    currency = models.CharField(max_length=255, null=True, blank=True)
    balance = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    accountId = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    bankConnectionId = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bank connected"


class UserSpace(models.Model):
    user = models.ForeignKey(CustomUser, verbose_name='user', on_delete=models.CASCADE)
    email = models.EmailField(unique=True, null=True, blank=True)
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
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Tokens have updated {self.updated_at}"
