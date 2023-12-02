from django.db import models

from apps.customuser.models import CustomUser


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
