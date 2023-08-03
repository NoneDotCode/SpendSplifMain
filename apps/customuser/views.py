from rest_framework import generics, permissions

from apps.customuser.models import CustomUser
from apps.customuser.serializers import CustomUserSerializer


class CustomUserRegistrationView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (permissions.AllowAny,)
