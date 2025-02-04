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
#     password = models.CharField(max_length=50)
#     refresh_token = models.CharField(max_length=305)
#     phone = models.CharField(max_length=255)

#     def __str__(self):
#         return f"User created for {self.phone}"
