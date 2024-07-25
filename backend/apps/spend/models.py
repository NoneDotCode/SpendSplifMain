from django.db import models
from backend.apps.customuser.models import CustomUser
from backend.apps.space.models import Space

class PeriodicSpendCounter(models.Model):
    title = models.CharField(max_length=100)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    father_space = models.ForeignKey(Space, on_delete=models.CASCADE)