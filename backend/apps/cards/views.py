from rest_framework import serializers, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta
from rest_framework.request import Request
import json

from backend.apps.space.models import Space
from backend.apps.account.permissions import IsSpaceMember
from backend.apps.cards.models import UserSpace, ClientToken, BankConnection
from .serializers import (
    FinAPICreateTokenSerializer,
    UserCreateSerializer,
    FinAPIRefreshTokenSerializer,
    UserSpaceSerializer,
    TransactionsRequestSerializer,
    BankConnectionSerializer
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
        }

        url = f"{self.BASE_URL}{endpoint}"
        try:
            response = requests.request(method, url, json=data, params=params, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}

    def create_user(self, member_email, generated_password, phone):
        """Создаёт пользователя в FinAPI"""
        payload = {
            'email': member_email,
            'password': generated_password,
            'phone': phone,
            'isAutoUpdateEnabled': False
        }
        return self._request("POST", "/api/v2/users", data=payload)

    def get_accounts(self, access_token):
        """Получение списка счетов"""
        return self._request("GET", "/api/v2/accounts", access_token=access_token)

    def bank_connection_import(self, access_token, bank_id, bank_connection_name, space_pk):
        """Импорт банковского подключения"""
        payload = {
            'bankingInterface': 'XS2A',
            'bank': {'id': bank_id},
            'callbacks': f'https://api.spendsplif.com/api/v1/my_spaces/${space_pk}/webhook/bank/connection/',
            'bankConnectionName': bank_connection_name,
            'maxDaysForDownload': 60,
            "redirectUrl": "https://spendsplif.com/bank/success/",
        }
        return self._request("POST", "/api/webForms/bankConnectionImport", data=payload, access_token=access_token)

    def get_transactions(self, access_token, account_ids, start_date, end_date):
        """Получение транзакций"""
        payload = {
            'accountIds': account_ids,
            'minBookingDate': start_date,
            'maxBookingDate': end_date,
            'includeChildCategories': True,
            'orderBy': 'bookingDate,desc'
        }
        return self._request("POST", "/api/v2/transactions", data=payload, access_token=access_token)

    def make_webhook_balance(self, access_token, account_ids, space_pk):
        """Получение изменения баланса"""
        payload = {
            "triggerEvent": "NEW_ACCOUNT_BALANCE",
            "params": {
                'accountIds': account_ids,
            },
            "callbackHandle": str(space_pk),
            "includeDetails": True,
        }
        return self._request("POST", "/api/v2/notificationRules", data=payload, access_token=access_token)

    def make_webhook_transactions(self, access_token, account_ids, space_pk):
        """Получение транзакций"""
        payload = {
            "triggerEvent": "NEW_TRANSACTIONS",
            "params": {
                'accountIds': account_ids,
                "waitForCategorization": True,
                "maxTransactionsCount": 100,
            },
            "callbackHandle": space_pk,
            "includeDetails": True,
        }
        return self._request("POST", "/api/v2/notificationRules", data=payload, access_token=access_token)


class UserAuthView(APIView):
    """Представление для аутентификации пользователя и создания токенов доступа."""
    permission_classes = [IsAuthenticated]

    def post(self, request, space_pk):
        """Обрабатывает POST-запрос для создания пользователя и получения токенов."""
        serializer = UserCreateSerializer(data=request.data, context={'space_pk': space_pk, 'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        user = request.user 
        space = serializer.validated_data['space']
        member_email = serializer.validated_data['user_email']

        finapi_client = FinAPIClient()
        user_space = UserSpace.objects.filter(space=space, email=member_email, access_token__isnull=False, user=user).first()

        # Если токен был обновлен менее часа назад, возвращаем существующие токены
        if user_space.updated_at > timezone.now() - timedelta(hours=1):
            return Response(UserSpaceSerializer(user_space).data, status=status.HTTP_200_OK)

        generated_password = generate_secure_password()
        phone = user_space.phone

        # Создаем пользователя в FinAPI
        try:
            user_response = finapi_client.create_user(member_email, generated_password, phone)
            if 'error' in user_response:
                return Response(
                    {'detail': 'Failed to create FinAPI user'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        except Exception as e:
            return Response(
                {'detail': 'Service temporarily unavailable'}, 
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        finapi_user_id = user_response.get('id')

        # Получаем токены от FinAPI
        token_data = {
            'grant_type': "password",
            'client_id': settings.FINAPI_CLIENT_ID,
            'client_secret': settings.FINAPI_CLIENT_SECRET,
            'username': finapi_user_id,
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
            user_space.username = finapi_user_id
            user_space.save(update_fields=['access_token', 'refresh_token', 'password', 'username'])

            return Response(UserSpaceSerializer(user_space).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class BankConnectionView(APIView):
    """Представление для импорта банковских подключений."""
    permission_classes = [IsAuthenticated, IsSpaceMember]

    def _is_valid_bank_name(self, bank_name):
        """Проверяет валидность имени банковского подключения."""
        return bank_name and 2 <= len(bank_name) <= 50

    def post(self, request, space_pk):
        """Обрабатывает POST-запрос для импорта банковского подключения. В ответе будет юрл, на который перенаправит фронт"""
        space = get_object_or_404(Space, pk=space_pk)

        bank_connection_name = request.data.get('bankConnectionName')
        if not self._is_valid_bank_name(bank_connection_name):
            return Response({'error': 'Invalid or missing bank connection name'}, status=status.HTTP_400_BAD_REQUEST)

        bank_id = request.data.get('bank_id')

        # Аутентификация пользователя
        auth_request = Request(request, data={'space': space}, method='POST')
        auth_response = UserAuthView.as_view()(auth_request, space_pk=space.pk)

        if auth_response.status_code != status.HTTP_201_CREATED:
            return auth_response

        access_token = auth_response.data.get('access_token')
        if not access_token:
            return Response({'error': 'Failed to retrieve user token'}, status=status.HTTP_400_BAD_REQUEST)

        # Импорт банковского подключения
        finapi_client = FinAPIClient()
        response = finapi_client.bank_connection_import(access_token, bank_id, bank_connection_name, space_pk)

        if 'error' in response:
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        bank_connection = BankConnection.objects.create(
            user=request.user,
            bankConnectionName=bank_connection_name,
            status="WAITING",
            webFormId=response.id,
        )
        
        return Response(response.url, status=status.HTTP_200_OK)


class BankConnectionWebhook(APIView):
    """Представление на которое будут приходить запросы о статусе банковских подключений."""

    def post(self, request, space_pk):
        """Обрабатывает POST-запрос и обновляет статус банковского подключения"""
        space = Space.objects.filter(pk=space_pk).first()
        if not space:
            return Response({'message': 'No transactions available'}, status=status.HTTP_200_OK)

        try:
            user_space = UserSpace.objects.get(space_id=space_pk)
        except UserSpace.DoesNotExist:
            return Response({'message': 'No transactions available'}, status=status.HTTP_200_OK)

        finapi_client = FinAPIClient()
        access_token = user_space.access_token
        webFormId = request.data.get('webFormId')
        status = request.data.get('status')
        bank_connection_name = request.data.get('bankConnectionName')

        bank_connection = BankConnection.objects.filter(
            bankConnectionName=bank_connection_name,
            webFormId=webFormId,
            space=space
        ).first()

        bank_connection.status = status
        bank_connection.save()

        if status == 'CANCELLED':
            bank_connection.delete()

        if status == 'COMPLETED':
            # Получаем список счетов
            accounts_response = finapi_client.get_accounts(access_token)
            if not accounts_response.ok:
                return Response({'error': 'Failed to fetch accounts'}, status=status.HTTP_400_BAD_REQUEST)

            accounts_data = accounts_response.json()
            account_ids = [account['id'] for account in accounts_data.get('accounts', [])]

            if not account_ids:
                return Response({'message': 'No accounts found'}, status=status.HTTP_200_OK)
            
            response_balance_webhook = finapi_client.make_webhook_balance(access_token, space_pk, account_ids)

            if 'error' in response_balance_webhook:
                print(response_balance_webhook)
                return Response(response_balance_webhook, status=status.HTTP_400_BAD_REQUEST)
        
            response_transactions_webhook = finapi_client.make_webhook_transactions(access_token, space_pk, account_ids)

            if 'error' in response_transactions_webhook:
                print(response_transactions_webhook)
                return Response(response_transactions_webhook, status=status.HTTP_400_BAD_REQUEST)

        return Response("Success", status=status.HTTP_200_OK)


class BankTransactionsAndBalanceWebhook(APIView):
    """Представление на которое будут приходить транзакции и обновление баланса банковского счета."""
    def post(self, request, space_pk):
        """Обрабатывает POST-запрос и обновляет баланс или добавляет транзакцию"""
        triggerEvent = request.data.get('triggerEvent')
        callbackHandle = request.data.get('callbackHandle')
       
        space_pk = callbackHandle
        space = Space.objects.filter(pk=space_pk).first()
        if not space:
            return Response("Space not found", status=status.HTTP_404_NOT_FOUND)
        
        if triggerEvent == "NEW_TRANSACTIONS":
            print("Trigger NEW_TRANSACTIONS")
            new_transactions = request.data.get('newTransactions', [])
            
            for transaction in new_transactions:
                account_name = transaction.get('accountName')
                bank_connection_name = transaction.get('bankConnectionName')
                details = transaction.get('details')
                
                if details:
                    try:
                        details_data = json.loads(details)
                        transactions_details = details_data.get('transactionDetails', [])
                        
                        for detail in transactions_details:
                            amount = detail.get('amount', 0)
                            transaction_type = "доход" if amount >= 0 else "трата"
                            
                            print("------------------------------------------------")
                            print(f"Тип: {transaction_type}")
                            print(f"Сумма: {abs(amount)}")
                            print(f"Банк: {bank_connection_name}")
                            print(f"Счёт: {account_name}")
                            print(f"Категория: {detail.get('categoryName', 'Не указана')}")
                            print(f"Назначение: {detail.get('purpose', 'Не указано')}")
                            if transaction_type == "трата":
                                print(f"Магазин: {detail.get('counterpartName', 'Не указан')}")
                            
                    except Exception as e:
                        print(f"Error parsing transaction details: {e}")
                        continue
                        
        elif triggerEvent == "NEW_ACCOUNT_BALANCE":
            balance_changes = request.data.get('balanceChanges', [])
           
            for change in balance_changes:
                bank_connection_name = change.get('bankConnectionName')
                details = change.get('details')
                if details:
                    try:
                        details_data = json.loads(details)
                        new_balance = details_data.get('newBalance')
                    except Exception as e:
                        print(f"Error parsing details: {e}")
                        continue
                    bank_connection = BankConnection.objects.filter(
                        bankConnectionName=bank_connection_name,
                        space=space
                    ).first()
                    if bank_connection:
                        bank_connection.balance = new_balance
                        bank_connection.save()
                        print(f"Updated balance for {bank_connection_name} to {new_balance}")
                    else:
                        print(f"BankConnection not found for {bank_connection_name}")
        return Response("Success", status=status.HTTP_200_OK)


class SpaceBankConnectionsView(APIView):
    def get(self, request, space_pk):
        # Получаем пространство по pk или возвращаем 404
        space = get_object_or_404(Space, pk=space_pk)
        
        # Получаем все банковские подключения для данного пространства
        connections = BankConnection.objects.filter(space=space)
        
        # Сериализуем данные
        serializer = BankConnectionSerializer(connections, many=True)
        
        return Response(serializer.data)


class BanksView(APIView):
    """Представление для получения списка банков."""

    def get(self, request):
        """Позже привяжем к FinAPI."""
        
        czech_banks = [
            {"id": 3001, "name": "Česká spořitelna"},
            {"id": 3002, "name": "ČSOB"},
            {"id": 3003, "name": "Komerční banka"},
            {"id": 3004, "name": "Air Bank"},
            {"id": 3005, "name": "Moneta Money Bank"},
            {"id": 3006, "name": "Fio banka"},
            {"id": 3007, "name": "Raiffeisenbank"},
            {"id": 3008, "name": "UniCredit Bank"},
            {"id": 3009, "name": "mBank"},
            {"id": 3010, "name": "Equa bank"},
            {"id": 3011, "name": "CREDITAS"}
        ]

        return Response(czech_banks, status=status.HTTP_200_OK)


class UserSpaceView(APIView):
    def get(self, request, space_pk):
        user = request.user
        
        if not space_pk:
            return Response({"message": "space_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        space = get_object_or_404(Space, id=space_pk)
        user_space = UserSpace.objects.filter(user=user, space=space).first()
        
        if user_space:
            return Response({"phone": user_space.phone}, status=status.HTTP_200_OK)
        return Response({"message": "No record found"}, status=status.HTTP_400_BAD_REQUEST)
    
    def post(self, request, space_pk):
        user = request.user
        phone = request.data.get('phone')
        
        if not space_pk or not phone:
            return Response({"message": "space_pk and phone are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        space = get_object_or_404(Space, id=space_pk)
        
        # Проверка валидности номера телефона
        if not self._is_valid_phone(phone):
            return Response({"message": "Invalid phone number"}, status=status.HTTP_400_BAD_REQUEST)
        
        user_space, created = UserSpace.objects.update_or_create(
            user=user,
            space=space,
            defaults={"phone": phone, "username": user.username}
        )
        
        return Response({
            "message": "Record updated" if not created else "Record created",
            "phone": user_space.phone
        }, status=status.HTTP_200_OK if not created else status.HTTP_201_CREATED)
    
    def _is_valid_phone(self, phone):
        """Проверяет валидность номера телефона."""
        return phone and phone.startswith('+') and 2 <= len(phone) <= 50


class TransactionsFetchView(APIView):
    """Представление для получения транзакций за последние 10 дней. Нужно переделать под скрипт, на случаи ЧП"""
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