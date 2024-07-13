from django.db import models
from backend.apps.customuser.models import CustomUser


class Notification(models.Model):
    notification_colors = (
        ("red", "Red"),
        ("yellow", "Yellow"),
        ("green", "Green")
    )
    who_can_view = models.ManyToManyField(CustomUser, related_name="who_can_view")
    message = models.TextField()
    color = models.CharField(max_length=25, choices=notification_colors)
    seen = models.ManyToManyField(CustomUser, related_name='viewed_notification')
    created_at = models.DateTimeField(auto_now_add=True)


class NotificationCompany(models.Model):
    notification_colors = (
        ("red", "Red"),
        ("yellow", "Yellow"),
        ("green", "Green")
    )
    message = models.TextField()
    color = models.CharField(max_length=25, choices=notification_colors)
    seen = models.ManyToManyField(CustomUser, related_name='viewed_notification_company')
    sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
