from django.urls import path

from backend.apps.customuser.views import (CustomUserRegistrationView, ConfirmRegistrationView, CustomUserUpdateAPIView,
                                           ConfirmNewEmailView, UserProfileView, LogoutView, GoogleLoginRedirectApi,
                                           GoogleLoginApi, CheckAppVersion, GoogleLoginApiMobileView,
                                           ConfirmNewPasswordView, ForgotPasswordView, ConfirmValidationPasswordView)

app_name = 'customuser'

urlpatterns = [
    path("register/", CustomUserRegistrationView.as_view(), name="register"),
    path("verify_email/", ConfirmRegistrationView.as_view(), name="verifyCode"),
    path("me/profile/edit/", CustomUserUpdateAPIView.as_view(), name="edit_profile"),
    path("me/profile/edit/verify_new_email/", ConfirmNewEmailView.as_view(), name="new_email_verify"),
    path("me/logout/", LogoutView.as_view(), name="logout"),
    path("me/profile/", UserProfileView.as_view(), name="my_profile"),
    path('auth/google/login/', GoogleLoginRedirectApi.as_view(), name='google_login'),
    path('auth/google/callback/', GoogleLoginApi.as_view(), name='google_callback'),
    path('check_version/', CheckAppVersion.as_view(), name='check_app_version'),
    path('auth/google/mob/callback/', GoogleLoginApiMobileView.as_view(), name='google_mob_callback'),
    path('me/profile/edit/verify_new_password/', ConfirmNewPasswordView.as_view(), name='edit_new_password'),
    path('forgot_pass/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('forgot_pass/confirm/', ConfirmValidationPasswordView.as_view(), name='confirm_password')
]
