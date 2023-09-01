from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.customuser.models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("id", "username", "email", "password", "language", "currency")
        extra_kwargs = {"password": {"write_only": True}}


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializer for JWT authentication with email instead of username.
    """

    username_field = "email"
    username = None

    def validate(self, attrs):
        """
        credentials = {
            'email': attrs.get('email'),
            'password': attrs.get('password')
        }
        """
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:
            user = authenticate(email=email, password=password)
            if user:
                if not user.is_active:
                    raise AuthenticationFailed("Account is not active")
                data = super().validate(attrs)
                data["user_id"] = user.id
                return data
            else:
                raise AuthenticationFailed("Not found user with given credentials..")
        else:
            raise AuthenticationFailed('Must include "email" and "password"')
