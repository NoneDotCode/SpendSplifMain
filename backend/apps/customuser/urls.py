from django.urls import path

from backend.apps.customuser.views import *
from backend.apps.customuser.views import *

urlpatterns = [
    path("register/", CustomUserRegistrationView.as_view(), name="register"),
    path("verify_email/", ConfirmRegistrationView.as_view(), name="verifyCode"),
    # path("me/password_reseе/send_code/", SendResetCodeView.as_view(), name="resetSendCode"),
    # path("me/password_reset/reset/", ResetPasswordView.as_view(), name="resetPassword"),
]