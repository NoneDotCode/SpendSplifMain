from rest_framework import generics, permissions
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.customuser.models import CustomUser
from apps.customuser.serializers import (
    CustomUserSerializer,
    EmailTokenObtainPairSerializer,
)


class CustomUserRegistrationView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (permissions.AllowAny,)


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Представление для получения JWT-токена через email.
    """

    serializer_class = EmailTokenObtainPairSerializer
