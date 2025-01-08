from django.db import models
from django.conf import settings
from backend.apps.customuser.models import CustomUser

class PaymentHistory(models.Model):
    space_id = models.IntegerField()
    payment_category  = models.CharField(max_length=50,) # the value can only be subscription/service/license
    amount = models.DecimalField(max_digits=12, decimal_places=2,)
    date = models.DateTimeField(auto_now=True,)

    def str(self):
        return f"{self.space_id} - {self.assets}"


class Subscription(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    stripe_subscription_id = models.CharField(max_length=255, unique=True)
    plan = models.CharField(max_length=50, choices=[
        ("business_plan", "Business Plan"),
        ("business_license", "Business License"),
    ])
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)