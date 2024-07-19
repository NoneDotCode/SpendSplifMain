from django.db import models
from backend.apps.customuser.models import CustomUser


class Notification(models.Model):
    notification_importance = (
        ("important", "Important"),
        ("medium", "Medium"),
        ("standard", "Standard")
    )
    who_can_view = models.ManyToManyField(CustomUser, related_name="who_can_view")
    message = models.TextField()
    importance = models.CharField(max_length=25, choices=notification_importance)
    seen = models.ManyToManyField(CustomUser, related_name='viewed_notification')
    created_at = models.DateTimeField(auto_now_add=True)


class NotificationCompany(models.Model):
    notification_importance = (
        ("important", "Important"),
        ("medium", "Medium"),
        ("standard", "Standard")
    )
    message = models.TextField()
    importance = models.CharField(max_length=25, choices=notification_importance)
    seen = models.ManyToManyField(CustomUser, related_name='viewed_notification_company')
    sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
