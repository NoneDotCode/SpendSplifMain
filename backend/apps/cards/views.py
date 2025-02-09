from rest_framework import serializers, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta
from rest_framework.request import Request

from backend.apps.space.models import Space
from backend.apps.account.permissions import IsSpaceMember
from backend.apps.cards.models import UserSpace, ClientToken
from .serializers import (
    FinAPICreateTokenSerializer,
    UserCreateSerializer,
    FinAPIRefreshTokenSerializer,
    UserSpaceSerializer,
    TransactionsRequestSerializer,
)

import string
import random
import uuid
import requests


def generate_secure_password(length=12):
    """Генерирует случайный безопасный пароль"""
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))


class FinAPIClient:
    BASE_URL = "https://sandbox.finapi.io"

    def __init__(self):
        self.token = self.get_finapi_token()

    @staticmethod
    def get_finapi_token():
        """Получает последний FinAPI токен КЛИЕНТА из базы данных"""
        token_obj = ClientToken.objects.first()
        return token_obj.access_token if token_obj else None

    def _request(self, method, endpoint, data=None, params=None, access_token=None):
        """Базовый метод для выполнения HTTP-запросов к FinAPI"""
        token = access_token or self.token
        if not token:
            return None

        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'X-Request-Id': str(uuid.uuid4())
        }

        url = f"{self.BASE_URL}{endpoint}"
        try:
            response = requests.request(method, url, json=data, params=params, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}

    def create_user(self, user_id, email, password, phone):
        """Создаёт пользователя в FinAPI"""
        payload = {
            'id': user_id,
            'email': email,
            'password': password,
            'phone': phone,
            'isAutoUpdateEnabled': False
        }
        return self._request("POST", "/api/v2/users", data=payload)

    def get_accounts(self, access_token):
        """Получение списка счетов"""
        return self._request("GET", "/api/v2/accounts", access_token=access_token)

    def get_transactions(self, access_token, account_ids, start_date, end_date):
        """Получение транзакций"""
        payload = {
            'accountIds': account_ids,
            'minBookingDate': start_date,
            'maxBookingDate': end_date,
            'includeChildCategories': True,
            'orderBy': 'bookingDate,desc'
        }
        return self._request("POST", "/api/v2/transactions/search", data=payload, access_token=access_token)


class UserAuthView(APIView):
    """Представление для аутентификации пользователя и создания токенов доступа."""
    permission_classes = [IsAuthenticated]

    def post(self, request, space_pk):
        """Обрабатывает POST-запрос для создания пользователя и получения токенов."""
        serializer = UserCreateSerializer(data=request.data, context={'space_pk': space_pk})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        space = serializer.validated_data['space']
        member_email = serializer.validated_data['member_email']
        phone = serializer.validated_data['phone']

        finapi_client = FinAPIClient()
        user_space, created = UserSpace.objects.get_or_create(space=space)

        # Если токен был обновлен менее часа назад, возвращаем существующие токены
        if not created and user_space.updated_at > timezone.now() - timedelta(hours=1):
            return Response(UserSpaceSerializer(user_space).data, status=status.HTTP_200_OK)

        generated_password = generate_secure_password()
        user_id = f"{space.id},{space.title}"

        # Создаем пользователя в FinAPI
        user_response = finapi_client.create_user(user_id, member_email, generated_password, phone)
        if 'error' in user_response:
            return Response(user_response, status=status.HTTP_400_BAD_REQUEST)

        # Получаем токены от FinAPI
        token_data = {
            'grant_type': "password",
            'client_id': settings.FINAPI_CLIENT_ID,
            'client_secret': settings.FINAPI_CLIENT_SECRET,
            'username': user_id,
            'password': generated_password
        }
        token_serializer = FinAPICreateTokenSerializer(data=token_data)
        if not token_serializer.is_valid():
            return Response(token_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            tokens = token_serializer.save()
            user_space.access_token = tokens['access_token']
            user_space.refresh_token = tokens['refresh_token']
            user_space.password = generated_password
            user_space.phone = phone
            user_space.save(update_fields=['access_token', 'refresh_token', 'password', 'phone'])

            return Response(UserSpaceSerializer(user_space).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class BankConnectionImportView(APIView):
    """Представление для импорта банковских подключений."""
    permission_classes = [IsAuthenticated, IsSpaceMember]

    def _is_valid_phone(self, phone):
        """Проверяет валидность номера телефона."""
        return phone and phone.startswith('+')

    def _is_valid_bank_name(self, bank_name):
        """Проверяет валидность имени банковского подключения."""
        return bank_name and len(bank_name) > 2

    def post(self, request, space_pk):
        """Обрабатывает POST-запрос для импорта банковского подключения."""
        space = get_object_or_404(Space, pk=space_pk)

        phone = request.data.get('phone')
        if not self._is_valid_phone(phone):
            return Response({'error': 'Invalid or missing phone number'}, status=status.HTTP_400_BAD_REQUEST)

        bank_connection_name = request.data.get('bankConnectionName')
        if not self._is_valid_bank_name(bank_connection_name):
            return Response({'error': 'Invalid or missing bank connection name'}, status=status.HTTP_400_BAD_REQUEST)

        # Аутентификация пользователя
        auth_request = Request(request, data={'space': space, 'phone': phone}, method='POST')
        auth_response = UserAuthView.as_view()(auth_request, space_pk=space.pk)

        if auth_response.status_code != status.HTTP_201_CREATED:
            return auth_response

        access_token = auth_response.data.get('access_token')
        if not access_token:
            return Response({'error': 'Failed to retrieve user token'}, status=status.HTTP_400_BAD_REQUEST)

        # Импорт банковского подключения
        finapi_client = FinAPIClient()
        response = finapi_client.bank_connection_import(access_token, bank_connection_name)

        if 'error' in response:
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        return Response(response, status=status.HTTP_200_OK)


class TransactionsFetchView(APIView):
    """Представление для получения транзакций за последние 10 дней."""
    permission_classes = [IsAuthenticated, IsSpaceMember]

    def get(self, request, space_pk):
        """Обрабатывает GET-запрос для получения транзакций."""
        space = Space.objects.filter(pk=space_pk).first()
        if not space:
            return Response({'message': 'No transactions available'}, status=status.HTTP_200_OK)

        try:
            user_space = UserSpace.objects.get(space_id=space_pk)
        except UserSpace.DoesNotExist:
            return Response({'message': 'No transactions available'}, status=status.HTTP_200_OK)

        finapi_client = FinAPIClient()
        access_token = user_space.access_token

        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=10)

        # Получаем список счетов
        accounts_response = finapi_client.get_accounts(access_token)
        if not accounts_response.ok:
            return Response({'error': 'Failed to fetch accounts'}, status=status.HTTP_400_BAD_REQUEST)

        accounts_data = accounts_response.json()
        account_ids = [account['id'] for account in accounts_data.get('accounts', [])]

        if not account_ids:
            return Response({'message': 'No accounts found'}, status=status.HTTP_200_OK)

        # Получаем транзакции
        transactions_response = finapi_client.get_transactions(access_token, account_ids, start_date, end_date)
        if not transactions_response.ok:
            return Response({'error': 'Failed to fetch transactions'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(transactions_response.json(), status=status.HTTP_200_OK)