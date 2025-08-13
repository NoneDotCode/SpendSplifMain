from django.db import models
from django.conf import settings
from backend.apps.customuser.models import CustomUser
from backend.apps.space.models import Space

class PaymentHistory(models.Model):
    father_space = models.ForeignKey(Space, verbose_name='father_space', on_delete=models.CASCADE)
    payment_category  = models.CharField(max_length=50,) # the value can only be subscription/service/license
    amount = models.DecimalField(max_digits=12, decimal_places=2,)
    date = models.DateTimeField(auto_now=True,)

    def str(self):
        return f"{self.space_id} - {self.assets}"


class Subscription(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    stripe_user = models.CharField(max_length=255)
    stripe_subscription_id = models.CharField(max_length=255, unique=True)
    plan = models.CharField(max_length=50)
    period = models.CharField(max_length=50, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)