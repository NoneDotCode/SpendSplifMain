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



class VerifyEmailSerializer(serializers.ModelSerializer):
    '''
    Mail verification
    '''
    code = serializers.IntegerField(required=True)


    class Meta:
        model = CustomUser
        fields = ("verify_code",)


    def validate(self, data: dict):
        '''
        Checking the validity of the entered code
        '''
        code: str = data["code"]

        if code != self.request.user.verify_code:
            raise serializers.ValidationError("Incorrect code")

        return data



class ResetPasswordSerializer(serializers.ModelSerializer):
    """
    password reset serializer
    """
    code = serializers.IntegerField(required=True)
    new_password = serializers.CharField(required=True)


    class Meta: 
        model = CustomUser
        fields = ("password_reset_code",)


    def validate(self, data: dict) -> dict:
        code: str = data["code"]
        new_password: str = data["new_password"]

        if code != self.request.user.password_reset_code:
            raise serializers.ValidationError("Incorrect code")

        self.request.user.set_password(new_password)
        self.request.user.save()

        return data