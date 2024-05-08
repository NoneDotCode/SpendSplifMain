from django.db import models

from apps.customuser.models import CustomUser
from apps.space.models import Space


class DmChat(models.Model):
    owner_1 = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="owner1_chats")
    owner_2 = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="owner2_chats")

    def str(self):
        return f"Chat between {self.owner_1.username} and {self.owner_2.username}"


class DmMessage(models.Model):
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    text = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    father_chat = models.ForeignKey(DmChat, on_delete=models.CASCADE)

    def __str__(self):
        return self.text


class SpaceGroup(models.Model):
    father_space = models.OneToOneField(Space, on_delete=models.CASCADE)


class MessageGroup(models.Model):
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    father_group = models.ForeignKey(SpaceGroup, on_delete=models.CASCADE)

class MessengerSettings(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    can_text = models.CharField(max_length=20, choices=[('nobody','Nobody'),('people_in_space', 'People in space'),('everybody','Everybody')], default='everybody')
    notification_enabled = models.BooleanField(default=True)

    def __str__(self):
        return f'Messenger settings for {self.user.username} applied'
    