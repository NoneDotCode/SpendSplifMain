from django.urls import path

from apps.customuser.views import *

urlpatterns = [
    path("register/", CustomUserRegistrationView.as_view(), name="register"),
    path("me/send_code/", SendVerifCodeView.as_view(), name="sendVerifyCode"),
    path("me/verify_email/", VerifyEmailView.as_view(), name="veridyCode"),
    path("me/password_reser/send_code/", SendResetCodeView.as_view(), name="resetSendCode"),
    path("me/password_reset/reset/", ResetPasswordView.as_view(), name="resetPassword"),
]