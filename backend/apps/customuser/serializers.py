import re

from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from backend.apps.customuser.models import CustomUser


class GoogleAuthSerializer(serializers.Serializer):
    access_token = serializers.CharField()
    currency = serializers.CharField(max_length=3, required=False)


class CustomUserSerializer(serializers.ModelSerializer, ):
    class Meta:
        model = CustomUser
        fields = ("id", "username", "email", "password", "language", "tag", "roles")
        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, data):
        
        password = data.get("password")
        if password:
        
            if not 8 <= len(password) <= 24:
                raise serializers.ValidationError("the password should be at least 8 characters long")

            if password.isdecimal():
                raise serializers.ValidationError("the password cannot be all numeric")

            if len(re.findall(r'[a-zA-Z]', password)) < 4:
                raise serializers.ValidationError("the password should have more than four letters")

            if len(re.findall(r'\d', password)) < 3:
                raise serializers.ValidationError("the password should have more than 3 numbers")

            if len(re.findall(r'[!@#$%^&*()_+{}\[\]:;<>,.?/~`]', password)) < 1:
                raise serializers.ValidationError("the password must contain at least 1 special character")

        return data

    def update(self, instance, validated_data):
        if (instance.email != validated_data.get("email", instance.email) and
                validated_data.get("email") is not None):
            print("email:", validated_data.get("email"))
            instance.new_email = validated_data.get('email', instance.email)
        if (instance.username != validated_data.get("username", instance.username) and
                validated_data.get("username") is not None):
            instance.username = validated_data.get('username', instance.username)
        if validated_data.get('password') is not None:
            instance.set_password(validated_data.get('password', instance.password))
        instance.save()
        return instance


class CustomTokenRefreshSerializer(serializers.Serializer):
    access = serializers.CharField(read_only=True)


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializer for JWT authentication with email instead of username.
    """

    username_field = "email"
    username = None

    @staticmethod
    def get_username(user):
        return user.email

    def validate(self, attrs):
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


class VerifyEmailSerializer(serializers.ModelSerializer):
    """
    Mail verification
    """
    code = serializers.IntegerField(required=True, write_only=True)

    class Meta:
        model = CustomUser
        fields = ("verify_code", "code")

    def validate(self, data: dict):
        """
        Checking the validity of the entered code
        """
        code: str = data["code"]

        if code != self.request.user.verify_code:
            raise serializers.ValidationError("Incorrect code")

        self.request.user.verify_email = True
        self.request.user.save()

        return data


class ResetPasswordSerializer(serializers.ModelSerializer):
    """
    password reset serializer
    """
    code = serializers.IntegerField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = CustomUser
        fields = ("password_reset_code", "new_password", "code")

    def validate(self, data: dict) -> dict:
        code: str = data["code"]
        new_password: str = data["new_password"]

        if code != self.request.user.password_reset_code:
            raise serializers.ValidationError("Incorrect code")

        self.request.user.set_password(new_password)
        self.request.user.save()

        return data


class CheckAppVersionSerializer(serializers.Serializer):
    version = serializers.CharField()
