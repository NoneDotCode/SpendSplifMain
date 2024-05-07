from django.urls import path

from backend.apps.customuser.views import (CustomUserRegistrationView, ConfirmRegistrationView, CustomUserUpdateAPIView,
                                           ConfirmNewEmailView, UserProfileView)

urlpatterns = [
    path("register/", CustomUserRegistrationView.as_view(), name="register"),
    path("verify_email/", ConfirmRegistrationView.as_view(), name="verifyCode"),
    path("me/profile/edit/", CustomUserUpdateAPIView.as_view(), name="edit_profile"),
    path("me/profile/edit/verify_new_email/", ConfirmNewEmailView.as_view(), name="new_email_verify"),
    path("me/profile/", UserProfileView.as_view(), name="my_profile")
]
