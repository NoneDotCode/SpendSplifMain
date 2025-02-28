import json
import random
import string
from datetime import timedelta

import requests
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.apps.account.permissions import IsSpaceMember
from backend.apps.cards.models import UserSpace, ClientToken, BankConnection, ConnectedAccounts
from backend.apps.space.models import Space
from .serializers import (
    UserCreateSerializer,
    UserSpaceSerializer,
    BankConnectionSerializer
)


def generate_secure_password(length=12):
    """Генерирует случайный безопасный пароль"""
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))


class FinAPIClient:
    BASE_URL_API = "https://sandbox.finapi.io"
    BASE_URL_WEB = "https://webform-sandbox.finapi.io"

    def __init__(self):
        self.token = self.get_finapi_token()

    @staticmethod
    def get_finapi_token():
        """Получает последний FinAPI токен КЛИЕНТА из базы данных"""
        token_obj = ClientToken.objects.first()
        return token_obj.access_token if token_obj else None

    def refresh_or_authenticate_user(self, user_space):
        """Обновляет или получает новый токен доступа для пользователя."""
        user_response = self.refresh_token(user_space.refresh_token, grant_type="refresh_token")
        if 'error' in user_response:
            user_response = self.auth_token(user_space.password, user_space.username, grant_type="password")
        access_token = user_response.get("access_token")
        user_space.access_token = access_token
        user_space.refresh_token = user_response.get("refresh_token")
        user_space.updated_at = timezone.now()
        user_space.save()
        return access_token

    def _request(self, method, endpoint, content_type, BASE_URL, data=None, params=None, access_token=None):
        """Базовый метод для выполнения HTTP-запросов к FinAPI"""
        headers = {
            'Content-Type': content_type,
        }

        token = access_token or self.token
        if not token:
            return None
        # Добавляем токен авторизации, если он есть
        if token and endpoint != "/api/v2/oauth/token":
            headers['Authorization'] = f'Bearer {token}'
        
        url = f"{BASE_URL}{endpoint}"
        try:
            print(method, url, data, params, headers)
            if content_type == 'application/x-www-form-urlencoded':
                response = requests.request(method, url, data=data, params=params, headers=headers)
            else:
                response = requests.request(method, url, json=data, params=params, headers=headers)
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Request error: {str(e)}")
            print(f"Details: {e.response.text if e.response else 'No response body available'}")
            return {'error': str(e)}

    def create_user(self, member_email, generated_password, phone):
        """Создаёт пользователя в FinAPI"""
        payload = {
            'email': member_email,
            'password': generated_password,
            'phone': phone,
            'isAutoUpdateEnabled': True
        }
        return self._request("POST", "/api/v2/users", data=payload, content_type='application/json', BASE_URL=self.BASE_URL_API,)
    
    def refresh_token(self, refresh_token, grant_type):
        """Обновить токен в FinAPI"""
        payload = {
            'grant_type': grant_type,
            'client_id': settings.FINAPI_CLIENT_ID,
            'client_secret': settings.FINAPI_CLIENT_SECRET,
            'refresh_token': refresh_token,
        }
        return self._request("POST", "/api/v2/oauth/token", data=payload, content_type='application/x-www-form-urlencoded', BASE_URL=self.BASE_URL_API)

    def auth_token(self, password, username, grant_type):
        """Обновить токен в FinAPI"""
        payload = {
            'grant_type': grant_type,
            'client_id': settings.FINAPI_CLIENT_ID,
            'client_secret': settings.FINAPI_CLIENT_SECRET,
            'username': username,
            'password': password,
        }
        return self._request("POST", "/api/v2/oauth/token", data=payload, content_type='application/x-www-form-urlencoded', BASE_URL=self.BASE_URL_API)

    def get_accounts(self, access_token):
        """Получение списка счетов"""
        return self._request("GET", "/api/v2/accounts", access_token=access_token, content_type='application/json', BASE_URL=self.BASE_URL_API)

    def get_account(self, access_token, id):
        """Получение списка счетов"""
        return self._request("GET", f"/api/v2/accounts/{id}", access_token=access_token, content_type='application/json', BASE_URL=self.BASE_URL_API)

    def bank_connection_import(self, access_token, bank_id, bank_connection_name, space_pk):
        """Импорт банковского подключения"""
        # потом добавить'redirectUrl': "https://spendsplif.com/bank/success/",
        payload = {
            "bank": {
                "id": bank_id
            },
            "callbacks": {
                "finalised": f"https://api.spendsplif.com/api/v1/my_spaces/{space_pk}/webhook/bank/connection/"
                # "finalised": f"https://5ef0-46-175-177-104.ngrok-free.app/api/v1/my_spaces/{space_pk}/webhook/bank/connection/"
            },
            "bankConnectionName": bank_connection_name,
            "maxDaysForDownload": 60
        }
        return self._request("POST", "/api/webForms/bankConnectionImport", access_token=access_token, data=payload, content_type='application/json', BASE_URL=self.BASE_URL_WEB)

    def get_transactions(self, access_token, account_ids, start_date, end_date):
        """Получение транзакций"""
        payload = {
            'accountIds': account_ids,
            'minBookingDate': start_date,
            'maxBookingDate': end_date,
            'includeChildCategories': True,
            'orderBy': 'bookingDate,desc'
        }
        return self._request("POST", "/api/v2/transactions", data=payload, access_token=access_token, content_type='application/json', BASE_URL=self.BASE_URL_API)

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
        return self._request("POST", "/api/v2/notificationRules", data=payload, access_token=access_token, content_type='application/json', BASE_URL=self.BASE_URL_API)

    def make_webhook_transactions(self, access_token, account_ids, space_pk):
        """Получение транзакций"""
        payload = {
            "triggerEvent": "NEW_TRANSACTIONS",
            "params": {
                'accountIds': account_ids,
                "waitForCategorization": True,
                "maxTransactionsCount": 100,
            },
            "callbackHandle": str(space_pk),
            "includeDetails": True,
        }
        return self._request("POST", "/api/v2/notificationRules", data=payload, access_token=access_token, content_type='application/json', BASE_URL=self.BASE_URL_API)

class UserAuthView(APIView):
    """Представление для аутентификации пользователя и создания токенов доступа."""
    permission_classes = [IsAuthenticated]

    @staticmethod
    def post(request, space_pk):
        """Обрабатывает POST-запрос для создания пользователя и получения токенов."""
        serializer = UserCreateSerializer(data=request.data, context={'space_pk': space_pk, 'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        user = request.user 
        space = serializer.validated_data['space']
        member_email = serializer.validated_data['user_email']

        finapi_client = FinAPIClient()
        user_space = UserSpace.objects.filter(space=space, user=user).first()

        if not user_space:
            return Response("error", status=status.HTTP_400_BAD_REQUEST)

        if user_space.access_token and user_space.updated_at > timezone.now() - timedelta(hours=1):
            return Response(UserSpaceSerializer(user_space).data, status=status.HTTP_200_OK)

        if user_space.refresh_token:
            access_token = finapi_client.refresh_or_authenticate_user(user_space)
            return Response({'access_token': access_token}, status=status.HTTP_200_OK)

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
            return Response({'detail': f"{e}"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        username = user_response.get('id')
        password = user_response.get('password')
        user_response = finapi_client.auth_token(password, username, grant_type="password")
        access_token = user_response.get('access_token')
        refresh_token = user_response.get('refresh_token')

        try:
            user_space.access_token = access_token
            user_space.refresh_token = refresh_token
            user_space.password = generated_password
            user_space.username = username
            user_space.save(update_fields=['access_token', 'refresh_token', 'password', 'username'])

            return Response(UserSpaceSerializer(user_space).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class BankConnectionView(APIView):
    """Представление для импорта банковских подключений."""
    permission_classes = [IsAuthenticated, IsSpaceMember]

    @staticmethod
    def _is_valid_bank_name(bank_name):
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
        access_token = self._get_access_token(request, space_pk)
        if isinstance(access_token, Response):
            return access_token

        # Импорт банковского подключения
        finapi_client = FinAPIClient()
        response = finapi_client.bank_connection_import(access_token, bank_id, bank_connection_name, space_pk)

        if 'error' in response:
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        # Получение значений из словаря response
        webform_id = response.get('id')
        redirect_url = response.get('url')

        if not webform_id or not redirect_url:
            return Response({'error': 'Invalid response from FinAPI'}, status=status.HTTP_400_BAD_REQUEST)

        BankConnection.objects.create(
            user=request.user,
            space=space,  # Важно добавить space в модель
            bankConnectionName=bank_connection_name,
            status="WAITING",
            webFormId=webform_id,
        )

        return Response({"url": redirect_url}, status=status.HTTP_200_OK)

    @staticmethod
    def _get_access_token(request, space_pk):
        """Obtains the access token for FinAPI."""
        auth_response = UserAuthView.post(request, space_pk)
        if auth_response.status_code not in [status.HTTP_200_OK, status.HTTP_201_CREATED]:
            return auth_response

        if isinstance(auth_response.data, dict):
            return auth_response.data.get('access_token')
        return auth_response.data


class BankConnectionWebhook(APIView):
    """Представление на которое будут приходить запросы о статусе банковских подключений."""
    permission_classes = [AllowAny]

    @staticmethod
    def post(request):
        """Обрабатывает POST-запрос и обновляет статус банковского подключения"""
        print(request, request.data)
        webFormId = request.data.get('webFormId')
        connection_status = request.data.get('status')
        bank_connection = BankConnection.objects.filter(webFormId=webFormId).first()

        space = bank_connection.space
        if not space:
            return Response({'message': 'No transactions available'}, status=status.HTTP_200_OK)

        space_pk = space.pk

        finapi_client = FinAPIClient()
        user_space = UserSpace.objects.filter(space=space, user=bank_connection.user, access_token__isnull=False).first()
        user_response = UserAuthView._get_or_refresh_token(user_space, finapi_client)
        access_token = user_response.get("access_token")
        UserAuthView._update_user_space(user_space, user_response)

        bank_connection.status = connection_status
        bank_connection.save()

        if connection_status in ['CANCELLED', 'EXPIRED']:
            bank_connection.delete()

        if connection_status == 'COMPLETED':
            # Получаем список счетов
            accounts_response = finapi_client.get_accounts(access_token)
            print(accounts_response)

            new_accounts = []
            for account in accounts_response.get('accounts', []):
                existing_account = ConnectedAccounts.objects.filter(
                    bankConnection=bank_connection,
                    accountIban=account['iban']
                ).first()

                if not existing_account:
                    new_accounts.append(str(account['id']))
                    ConnectedAccounts.objects.create(
                        bankConnection=bank_connection,
                        accountIban=account['iban'],
                        currency=account['accountCurrency'],
                        balance=account.get('balance', 0),
                        bankConnectionId=account['bankConnectionId'],
                        accountId=account['id'],
                        created_at=timezone.now()
                    )

            if new_accounts:  # Вызываем вебхуки только если есть новые счета
                account_ids_str = ",".join(new_accounts)

                response_balance_webhook = finapi_client.make_webhook_balance(access_token, account_ids_str, space_pk)
                if 'error' in response_balance_webhook:
                    print(response_balance_webhook)
                    return Response({"error": response_balance_webhook}, status=status.HTTP_400_BAD_REQUEST)

                response_transactions_webhook = finapi_client.make_webhook_transactions(access_token, account_ids_str, space_pk)
                if 'error' in response_transactions_webhook:
                    print(response_transactions_webhook)
                    return Response({"error": response_transactions_webhook}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"Success"}, status=status.HTTP_200_OK)


class BankTransactionsAndBalanceWebhook(APIView):
    """Webhook view to receive transactions and balance updates."""

    @staticmethod
    def post(request):
        """Handles POST request to update balance or add a transaction."""
        print(request.data)
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
                            transaction_type = "income" if amount >= 0 else "expense"

                            print("------------------------------------------------")
                            print(f"Type: {transaction_type}")
                            print(f"Amount: {abs(amount)}")
                            print(f"Bank: {bank_connection_name}")
                            print(f"Account: {account_name}")
                            print(f"Category: {detail.get('categoryName', 'Not specified')}")
                            print(f"Purpose: {detail.get('purpose', 'Not specified')}")
                            if transaction_type == "expense":
                                print(f"Store: {detail.get('counterpartName', 'Not specified')}")

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
    @staticmethod
    def get(request, space_pk):
        # Получаем пространство по pk или возвращаем 404
        space = get_object_or_404(Space, pk=space_pk)

        # Получаем все банковские подключения для данного пространства
        bank_connections = BankConnection.objects.filter(space=space, user=request.user)

        # Получаем все связанные счета
        connections = ConnectedAccounts.objects.filter(bankConnection__in=bank_connections)

        # Сериализуем данные
        serializer = BankConnectionSerializer(connections, many=True)

        return Response(serializer.data)


class BanksView(APIView):
    """Представление для получения списка банков из FinAPI."""

    @staticmethod
    def get_finapi_token():
        """Получает последний FinAPI токен КЛИЕНТА из базы данных"""
        token_obj = ClientToken.objects.first()
        return token_obj.access_token if token_obj else None

    def get(self, request):
        """Получение списка чешских банков из FinAPI."""
        finapi_url = "https://sandbox.finapi.io/api/v2/banks"
        token = self.get_finapi_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        }
        params = {
            "location": "CZ",
            "perPage": 100
        }

        response = requests.get(finapi_url, headers=headers, params=params)

        if response.status_code == 200:
            banks_data = response.json().get("banks", [])
            result = [{"id": bank["id"], "name": bank["name"]} for bank in banks_data if bank.get("location") == "CZ"]
            return Response(result, status=status.HTTP_200_OK)

        return Response({"error": "Failed to retrieve data from FinAPI"}, status=response.status_code)


class UserSpaceView(APIView):
    @staticmethod
    def get(request, space_pk):
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

    @staticmethod
    def _is_valid_phone(phone):
        """Проверяет валидность номера телефона."""
        return phone and phone.startswith('+') and 2 <= len(phone) <= 50


class DeleteBankAccountView(APIView):
    """View to delete a bank account and unlink it from FinAPI."""
    permission_classes = [IsAuthenticated, IsSpaceMember]

    @staticmethod
    def delete(request, space_pk):
        """Обрабатывает DELETE-запрос для удаления счета."""
        print(request.data)
        account_id = request.data.get('accountId')
        if not account_id:
            return Response({'error': 'accountId is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Находим счет по accountId и проверяем, что он принадлежит текущему пользователю и пространству
        account = get_object_or_404(
            ConnectedAccounts,
            accountId=account_id,
            bankConnection__space__pk=space_pk,
            bankConnection__user=request.user
        )

        # Получаем access_token для FinAPI
        access_token = BankConnectionView._get_access_token(request, space_pk)
        if isinstance(access_token, Response):
            return access_token

        # Удаляем счет из FinAPI
        finapi_client = FinAPIClient()
        delete_response = finapi_client._request(
            method="DELETE",
            endpoint=f"/api/v2/accounts/{account_id}",
            content_type='application/json',
            BASE_URL=finapi_client.BASE_URL_API,
            access_token=access_token
        )

        print(delete_response)

        # Удаляем счет из базы данных
        account.delete()

        return Response({'message': 'Bank account successfully deleted and unlinked from FinAPI'}, status=status.HTTP_200_OK)


# class TransactionsFetchView(APIView):
#     """Представление для получения транзакций за последние 10 дней. Нужно переделать под скрипт, на случаи ЧП"""
#     permission_classes = [IsAuthenticated, IsSpaceMember]

#     def get(self, request, space_pk):
#         """Обрабатывает GET-запрос для получения транзакций."""
#         space = Space.objects.filter(pk=space_pk).first()
#         if not space:
#             return Response({'message': 'No transactions available'}, status=status.HTTP_200_OK)

#         try:
#             user_space = UserSpace.objects.get(space_id=space_pk)
#         except UserSpace.DoesNotExist:
#             return Response({'message': 'No transactions available'}, status=status.HTTP_200_OK)

#         finapi_client = FinAPIClient()
#         access_token = user_space.access_token

#         end_date = timezone.now().date()
#         start_date = end_date - timedelta(days=10)

#         # Получаем список счетов
#         accounts_response = finapi_client.get_accounts(access_token)
#         if not accounts_response.ok:
#             return Response({'error': 'Failed to fetch accounts'}, status=status.HTTP_400_BAD_REQUEST)

#         accounts_data = accounts_response.json()
#         account_ids = [account['id'] for account in accounts_data.get('accounts', [])]

#         if not account_ids:
#             return Response({'message': 'No accounts found'}, status=status.HTTP_200_OK)

#         # Получаем транзакции
#         transactions_response = finapi_client.get_transactions(access_token, account_ids, start_date, end_date)
#         if not transactions_response.ok:
#             return Response({'error': 'Failed to fetch transactions'}, status=status.HTTP_400_BAD_REQUEST)

#         return Response(transactions_response.json(), status=status.HTTP_200_OK)