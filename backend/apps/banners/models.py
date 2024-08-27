from django.db import models
from cloudinary.models import CloudinaryField
from backend.apps.customuser.models import CustomUser

class Banner(models.Model):
    image = CloudinaryField('image')
    views = models.PositiveIntegerField(default=0)
    clicks = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    goal_view = models.PositiveIntegerField(null=True, blank=True)
    goal_click = models.PositiveIntegerField(null=True, blank=True)
    link = models.URLField()
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='banners')

    def __str__(self):
        return f"Banner {self.id} - {self.link}"