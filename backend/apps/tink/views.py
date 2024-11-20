import decimal

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from backend.apps.space.models import Space
from backend.apps.tink.models import TinkUser, TinkAccount
from backend.apps.tink.serializers import TinkAccountSerializer

from django.conf import settings

import requests
import json

from backend.apps.account.permissions import IsSpaceMember


class AuthorizeAppView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    def get(self, request):
        client_id = settings.TINK["CLIENT_ID"]
        client_secret = settings.TINK["CLIENT_SECRET"]

        auth_data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials",
            "scope": "user:create"
        }

        response = requests.post("https://api.tink.com/api/v1/oauth/token", data=auth_data)

        if response.status_code == 200:
            access_token = response.json().get("access_token")
            return Response({"access_token": access_token}, status=status.HTTP_200_OK)
        else:
            return Response(response.json(), status=response.status_code)


class CreateUserView(generics.GenericAPIView):
    def post(self, request):
        access_token = request.data.get("access_token")
        external_user_id = request.data.get("external_user_id", request.user.id)
        market = request.data.get("market", "GB")
        locale = request.data.get("locale", "en_US")

        user_data = {
            'external_user_id': external_user_id,
            'market': market,
            'locale': locale
        }

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

        response = requests.post('https://api.tink.com/api/v1/user/create', headers=headers, json=user_data)

        if response.status_code == 200:
            TinkUser.objects.create(user=request.user,
                                    user_tink_id=response.json()["user_id"])
            created_user = response.json()
            return Response(created_user, status=status.HTTP_200_OK)
        else:
            return Response(response.json(), status=response.status_code)


class GenerateAuthorizationCodeView(generics.GenericAPIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        client_id = settings.TINK["CLIENT_ID"]
        client_secret = settings.TINK["CLIENT_SECRET"]

        auth_data = {
            'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': 'client_credentials',
            'scope': 'authorization:grant'
        }
        
        response = requests.post('https://api.tink.com/api/v1/oauth/token', data=auth_data)
        
        if response.status_code == 200:
            access_token = response.json().get('access_token')
            return Response({'access_token': access_token})
        else:
            return Response(response.json(), status=response.status_code)


class GrantUserAccessView(generics.GenericAPIView):
    def post(self, request):
        access_token = request.data.get('access_token')
        id_hint = request.data.get('id_hint', f"{request.user.username}{request.user.tag}")

        data = {
            'actor_client_id': 'df05e4b379934cd09963197cc855bfe9',
            'user_id': TinkUser.objects.get(user=request.user).user_tink_id,
            'id_hint': id_hint,
            'scope': 'authorization:read,authorization:grant,credentials:refresh,credentials:read,credentials:write,providers:read,user:read'
        }

        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        
        response = requests.post('https://api.tink.com/api/v1/oauth/authorization-grant/delegate', headers=headers, data=data)
        
        if response.status_code == 200:
            user_authorization_code = response.json().get('code')
            return Response({'user_authorization_code': user_authorization_code})
        else:
            return Response(response.json(), status=response.status_code)


class BuildTinkURLView(generics.GenericAPIView):
    def post(self, request):
        user_authorization_code = request.data.get('user_authorization_code')
        client_id = settings.TINK["CLIENT_ID"]
        market = request.data.get('market', 'GB')
        locale = request.data.get('locale', 'en_US')
        state = request.data.get('state')
        redirect_uri = request.build_absolute_uri("https://console.tink.com/callback")

        tink_url = (
            "https://link.tink.com/1.0/transactions/connect-accounts?"
            f"client_id={client_id}&"
            f"state={state}&"
            f"redirect_uri={redirect_uri}&"
            f"authorization_code={user_authorization_code}&"
            f"market={market}&"
            f"locale={locale}"
        )

        return Response({'tink_url': tink_url})


class GetAuthorizationCodeView(generics.GenericAPIView):
    def post(self, request):
        access_token = request.data.get('access_token')
        user_id = TinkUser.objects.get(user=request.user).user_tink_id
        external_user_id = request.data.get('external_user_id')
        scope = 'accounts:read,balances:read,transactions:read,provider-consents:read'

        headers = {
            'Authorization': f'Bearer {access_token}'
        }

        data = {
            'user_id': user_id,
            'external_user_id': external_user_id,
            'scope': scope
        }

        response = requests.post('https://api.tink.com/api/v1/oauth/authorization-grant', headers=headers, data=data)

        if response.status_code == 200:
            authorization_code = response.json().get('code')
            return Response({'authorization_code': authorization_code})
        else:
            return Response(response.json(), status=response.status_code)


class GetUserAccessTokenView(generics.GenericAPIView):
    def post(self, request):
        authorization_code = request.data.get('authorization_code')
        client_id = settings.TINK["CLIENT_ID"]
        client_secret = settings.TINK["CLIENT_SECRET"]

        data = {
            'code': authorization_code,
            'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': 'authorization_code'
        }

        response = requests.post('https://api.tink.com/api/v1/oauth/token', data=data)

        tink_user = TinkUser.objects.get(user=request.user)
        tink_user.access_token = response.json().get('access_token')


        if response.status_code == 200:
            return Response(response.json())
        else:
            return Response(response.json(), status=response.status_code)


class AddAccountsView(generics.GenericAPIView):
    permission_classes = (IsSpaceMember,)

    def post(self, request, space_pk):
        # Проверяем, что пространство принадлежит текущему пользователю
        try:
            space = Space.objects.get(pk=space_pk)
        except Space.DoesNotExist:
            return Response({"detail": "Space not found or access denied."}, status=status.HTTP_404_NOT_FOUND)

        # Получение токена пользователя
        user_access_token = request.data.get('user_access_token')
        if not user_access_token:
            return Response({"detail": "User access token is required."}, status=status.HTTP_400_BAD_REQUEST)

        headers = {
            'Authorization': f'Bearer {user_access_token}'
        }

        # Запрос данных аккаунтов из Tink
        response = requests.get('https://api.tink.com/data/v2/accounts', headers=headers)
        if response.status_code != 200:
            return Response(response.json(), status=response.status_code)

        accounts_data = response.json().get('accounts', [])
        created_accounts = []

        for account in accounts_data:
            account_id = account.get('id')
            account_name = account.get('name')
            account_type = account.get('type')
            balances = account.get('balances', {}).get('booked', {}).get('amount', {})
            unscaled_value = balances.get('value', {}).get('unscaledValue')
            scale = balances.get('value', {}).get('scale')
            currency = balances.get('currencyCode')

            # Проверяем валидность данных баланса
            if unscaled_value is not None and scale is not None:
                balance = decimal.Decimal(unscaled_value) * (decimal.Decimal(10) ** int(scale))
            else:
                balance = decimal.Decimal(0)

            # Проверяем, существует ли уже аккаунт
            if not TinkAccount.objects.filter(account_id=account_id).exists():
                # Создаём аккаунт, если его нет
                tink_account = TinkAccount.objects.create(
                    space=space,
                    account_id=account_id,
                    account_name=account_name,
                    account_type=account_type,
                    balance=balance,
                    currency=currency,
                )
                created_accounts.append({
                    "account_id": tink_account.account_id,
                    "account_name": tink_account.account_name,
                    "account_type": tink_account.account_type,
                    "balance": float(tink_account.balance),
                    "currency": tink_account.currency,
                })

        # Возвращаем информацию о созданных аккаунтах
        return Response({
            "detail": f"{len(created_accounts)} accounts added to space {space_pk}.",
            "created_accounts": created_accounts
        }, status=status.HTTP_201_CREATED)


class ListTinkAccountsView(generics.GenericAPIView):
    serializer_class = TinkAccountSerializer

    def get(self, request, space_pk):
        queryset = TinkAccount.objects.filter(space_id=space_pk)
        serializer = TinkAccountSerializer(queryset, many=True)
        return Response(serializer.data)


class ListTransactionsView(generics.GenericAPIView):
    def get(self, request):
        user_access_token = request.data.get('user_access_token')
        account_id = request.data.get('account_id')
        pending = request.data.get('pending')
        page_size = request.data.get('page_size')
        page_token = request.data.get('page_token')

        headers = {
            'Authorization': f'Bearer {user_access_token}'
        }

        params = {}
        if account_id:
            params['accountIdIn'] = account_id
        if pending:
            params['pending'] = pending
        if page_size:
            params['pageSize'] = page_size
        if page_token:
            params['pageToken'] = page_token

        response = requests.get('https://api.tink.com/data/v2/transactions', headers=headers, params=params)

        if response.status_code == 200:
            transactions = response.json()
            return Response(transactions)
        else:
            return Response(response.json(), status=response.status_code)


