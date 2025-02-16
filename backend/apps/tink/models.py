from django.db import models

from backend.apps.customuser.models import CustomUser
from backend.apps.space.models import Space


class TinkUser(models.Model):
    space = models.OneToOneField(Space, on_delete=models.CASCADE)
    user_tink_id = models.CharField(unique=True)
    access_token = models.TextField(blank=True)
    refresh_token = models.TextField(blank=True)
    expires_at = models.DateTimeField(blank=True, null=True)


class TinkAccount(models.Model):
    user = models.ForeignKey(TinkUser, on_delete=models.CASCADE, related_name='tink_accounts')
    account_id = models.CharField(max_length=100, unique=True)
    account_name = models.CharField(max_length=100)
    account_type = models.CharField(max_length=50)
    balance = models.DecimalField(max_digits=20, decimal_places=2)
    currency = models.CharField(max_length=3)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
