from rest_framework import serializers
from django.conf import settings
from backend.apps.space.models import Space, MemberPermissions
from .models import BankConnection, UserSpace, ClientToken
from django.shortcuts import get_object_or_404
import string
import random


# Функция для генерации безопасного пароля
def generate_secure_password(length=12):
    """Генерирует случайный безопасный пароль"""
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))


# Сериализатор для модели BankConnection
class BankConnectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankConnection
        fields = ['user', 'access_token', 'refresh_token', 'expires_at']
        read_only_fields = ['user'] 

    def validate(self, data):
        if not data.get('access_token') or not data.get('refresh_token'):
            raise serializers.ValidationError("Access token and refresh token are required.")
        return data


# Сериализатор для модели UserSpace
class UserSpaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSpace
        fields = ['space', 'access_token', 'refresh_token', 'phone', 'updated_at']
        read_only_fields = ['updated_at'] 

    def validate_phone(self, value):
        # Пример валидации номера телефона
        if not value.startswith('+'):
            raise serializers.ValidationError("Phone number must start with '+'.")
        return value


# Сериализатор для модели ClientToken
class ClientTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientToken
        fields = ['access_token', 'refresh_token', 'updated_at']
        read_only_fields = ['updated_at']

    def validate(self, data):
        if not data.get('access_token') or not data.get('refresh_token'):
            raise serializers.ValidationError("Access token and refresh token are required.")
        return data


# Сериализатор для создания токена в FinAPI
class FinAPICreateTokenSerializer(serializers.Serializer):
    grant_type = serializers.CharField()
    client_id = serializers.CharField()
    client_secret = serializers.CharField()
    username = serializers.CharField()
    password = serializers.CharField()

    def validate_grant_type(self, value):
        if value != "password":
            raise serializers.ValidationError("Grant type must be 'password'.")
        return value


# Сериализатор для обновления токена в FinAPI
class FinAPIRefreshTokenSerializer(serializers.Serializer):
    grant_type = serializers.CharField()
    client_id = serializers.CharField()
    client_secret = serializers.CharField()
    refresh_token = serializers.CharField()

    def validate_grant_type(self, value):
        if value != "refresh_token":
            raise serializers.ValidationError("Grant type must be 'refresh_token'.")
        return value


# Сериализатор для создания пользователя
class UserCreateSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=255)

    def validate_phone(self, value):
        if not value.startswith('+'):
            raise serializers.ValidationError("Phone number must start with '+'.")
        return value

    def validate(self, data):
        space_pk = self.context.get('space_pk')
        if not space_pk:
            raise serializers.ValidationError("space_pk is required")

        # Get the requesting user from context
        request = self.context.get('request')
        if not request or not request.user:
            raise serializers.ValidationError("Authentication required")

        space = get_object_or_404(Space, pk=space_pk)

        data['space'] = space
        data['user_email'] = request.user.email
        return data


# Сериализатор для запроса транзакций
class TransactionsRequestSerializer(serializers.Serializer):
    account_ids = serializers.ListField(child=serializers.CharField())
    start_date = serializers.DateField()
    end_date = serializers.DateField()

    def validate(self, data):
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError("Start date must be before end date.")
        return data