from django.urls import path

from apps.customuser.views import CustomUserRegistrationView

urlpatterns = [
    path("register/", CustomUserRegistrationView.as_view(), name="register"),
]
