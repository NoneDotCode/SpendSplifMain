from django.db import models
from backend.apps.customuser.models import CustomUser
from backend.apps.space.models import Space

class Advice(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    advice = models.TextField()
    created = models.DateField(auto_now_add=True)
    space = models.ForeignKey(Space, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user}:{self.advice}"