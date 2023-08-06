from rest_framework import serializers

from apps.customuser.models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("id", "username", "email", "password", "language")
        extra_kwargs = {"password": {"write_only": True}}
