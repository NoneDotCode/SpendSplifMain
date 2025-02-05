# from django.db import models
# from django.conf import settings
# from backend.apps.space.models import Space

# class BankConnection(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     access_token = models.CharField(max_length=255)
#     refresh_token = models.CharField(max_length=255)
#     expires_at = models.DateTimeField()

#     def __str__(self):
#         return f"Bank connection for {self.user.email}"


# class UserSpace(models.Model):
#     space = models.ForeignKey(Space, verbose_name='father_space', on_delete=models.CASCADE)
#     username = models.CharField(max_length=50)
#     password = models.CharField(max_length=50)
#     access_token = models.CharField(max_length=305, null=True, blank=True)
#     refresh_token = models.CharField(max_length=305, null=True, blank=True)
#     phone = models.CharField(max_length=255)
#     updated_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"User created for {self.phone}"


# class ClientToken(models.Model):
#     access_token = models.CharField(max_length=305, null=True, blank=True)
#     refresh_token = models.CharField(max_length=305, null=True, blank=True)
#     updated_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Tokens have updated {self.updated_at}"
