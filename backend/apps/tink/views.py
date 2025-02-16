import decimal

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from backend.apps.history.models import HistoryExpense, HistoryIncome
from backend.apps.space.models import Space
from backend.apps.tink.models import TinkUser, TinkAccount
from backend.apps.tink.serializers import TinkAccountSerializer
from backend.apps.converter.utils import convert_currencies

from django.conf import settings

import requests
import json

from backend.apps.account.permissions import IsSpaceMember


class FullIntegrationView(generics.GenericAPIView):
    """
    Automates the entire Tink integration process:
    1. Authorizes app
    2. Creates a Tink user linked to a space
    3. Fetches accounts and adds them to the space
    4. Returns a Tink Link URL for user interaction
    """
    permission_classes = (IsSpaceMember,)

    def post(self, request, space_pk):

        # Authorize app
        market = request.data.get("market", "GB")
        locale = request.data.get("locale", "en_US")
        app_auth_data = {
            "client_id": settings.TINK["CLIENT_ID"],
            "client_secret": settings.TINK["CLIENT_SECRET"],
            "grant_type": "client_credentials",
            "scope": "user:create authorization:grant accounts:read"
        }
        app_response = requests.post("https://api.tink.com/api/v1/oauth/token", data=app_auth_data)
        if app_response.status_code != 200:
            return Response(app_response.json(), status=app_response.status_code)

        app_access_token = app_response.json().get("access_token")
        space = Space.objects.get(pk=space_pk)
        external_user_id = f"{space_pk}-{space.title}-{space.currency}-user"

        # Create Tink user
        if not TinkUser.objects.filter(space=space):
            user_data = {
                "external_user_id": external_user_id,
                "market": market,
                "locale": locale
            }
            headers = {"Authorization": f"Bearer {app_access_token}"}
            user_response = requests.post("https://api.tink.com/api/v1/user/create", json=user_data, headers=headers)
            if user_response.status_code != 200:
                return Response(user_response.json(), status=user_response.status_code)

            tink_user_id = user_response.json().get("user_id")
            tink_user, _ = TinkUser.objects.get_or_create(space=space, user_tink_id=tink_user_id)
        else:
            tink_user = TinkUser.objects.get(space=space)
            tink_user_id = tink_user.user_tink_id

        # Generate user authorization code
        id_hint = f"{request.user.username}{request.user.tag}"

        data = {
            'actor_client_id': 'df05e4b379934cd09963197cc855bfe9',
            'user_id': tink_user_id,
            'id_hint': id_hint,
            'scope': 'authorization:read,authorization:grant,credentials:refresh,credentials:read,credentials:write,'
                     'providers:read,user:read'
        }

        headers = {
            'Authorization': f'Bearer {app_access_token}'
        }

        response = requests.post('https://api.tink.com/api/v1/oauth/authorization-grant/delegate', headers=headers,
                                 data=data)

        authorization_code = response.json().get('code')
        state = request.data.get("state")
        redirect_uri = request.build_absolute_uri("https://console.tink.com/callback")

        # Build Tink Link URL
        tink_url = (
            "https://link.tink.com/1.0/transactions/connect-accounts?"
            f"client_id={settings.TINK['CLIENT_ID']}&"
            f"state={state}&"
            f"redirect_uri={redirect_uri}&"
            f"authorization_code={authorization_code}&"
            f"market={market}&"
            f"locale={locale}"
        )

        # Save user and link to space
        tink_user.space = space
        tink_user.save()

        return Response({"tink_url": tink_url}, status=status.HTTP_200_OK)


class UpdateAccountsAndTransactions(generics.GenericAPIView):

    def post(self, request, space_pk):

        app_auth_data = {
            "client_id": settings.TINK["CLIENT_ID"],
            "client_secret": settings.TINK["CLIENT_SECRET"],
            "grant_type": "client_credentials",
            "scope": "user:create authorization:grant accounts:read"
        }
        app_response = requests.post("https://api.tink.com/api/v1/oauth/token", data=app_auth_data)
        if app_response.status_code != 200:
            return Response(app_response.json(), status=app_response.status_code)

        app_access_token = app_response.json().get("access_token")
        space = Space.objects.get(pk=space_pk)
        tink_user = TinkUser.objects.get(space=space)
        tink_user_id = tink_user.user_tink_id
        data = {
            'user_id': tink_user_id,
            'scope': 'accounts:read,balances:read,transactions:read,provider-consents:read'
        }

        headers = {
            'Authorization': f'Bearer {app_access_token}'
        }

        response = requests.post('https://api.tink.com/api/v1/oauth/authorization-grant', headers=headers, data=data)

        authorization_code = response.json().get('code')

        client_id = settings.TINK["CLIENT_ID"]
        client_secret = settings.TINK["CLIENT_SECRET"]

        data = {
            'code': authorization_code,
            'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': 'authorization_code'
        }

        response = requests.post('https://api.tink.com/api/v1/oauth/token', data=data)

        tink_user = TinkUser.objects.get(space=space)
        user_access_token = response.json().get('access_token')
        tink_user.access_token = user_access_token

        headers = {
            'Authorization': f'Bearer {user_access_token}'
        }

        response = requests.get('https://api.tink.com/data/v2/accounts', headers=headers)
        if response.status_code != 200:
            return Response(response.json(), status=response.status_code)

        accounts_data = response.json().get('accounts', [])

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
                TinkAccount.objects.create(
                    user=tink_user,
                    account_id=account_id,
                    account_name=account_name,
                    account_type=account_type,
                    balance=balance,
                    currency=currency,
                )

            headers = {'Authorization': f'Bearer {user_access_token}'}
            params = {}
            pending = request.data.get('pending')
            page_size = request.data.get('page_size')
            page_token = request.data.get('page_token')
            if account_id:
                params['accountIdIn'] = account_id
            if pending:
                params['pending'] = pending
            if page_size:
                params['pageSize'] = page_size
            if page_token:
                params['pageToken'] = page_token

            response = requests.get('https://api.tink.com/data/v2/transactions', headers=headers, params=params)

            if response.status_code != 200:
                print("0")
                return Response(response.json(), status=response.status_code)

            transactions = response.json().get('transactions', [])
            for transaction in transactions:

                if HistoryExpense.objects.filter(tink_id=transaction.get('id')) or HistoryIncome.objects.filter(
                        tink_id=transaction.get('id')):
                    continue

                amount = transaction.get('amount', {}).get('value').get('unscaledValue')
                scale = transaction.get('amount', {}).get('value').get('scale')
                amount = decimal.Decimal(amount) * (decimal.Decimal(10) ** int(scale))
                description = transaction.get('descriptions').get('display')
                currency = transaction.get('amount')['currencyCode']
                account_id = transaction.get('accountId')
                transaction_date = transaction.get('dates', {}).get('booked')
                is_expense = amount < 0

                account = TinkAccount.objects.filter(account_id=account_id).first()
                if not account:
                    continue

                # Создание записи в истории
                if is_expense:
                    HistoryExpense.objects.create(
                        amount=abs(amount ** scale),
                        currency=currency,
                        amount_in_default_currency=convert_currencies(from_currency=currency,
                                                                      to_currency=space.currency,
                                                                      amount=amount),
                        comment=description,
                        to_cat=None,  # Можно настроить на основе анализа описания
                        tink_id=transaction.get('id'),
                        tink_account=account,
                        periodic_expense=False,
                        father_space=space,
                        created=transaction_date
                    )
                else:
                    HistoryIncome.objects.create(
                        amount=(amount ** scale),
                        currency=currency,
                        amount_in_default_currency=convert_currencies(from_currency=currency,
                                                                      to_currency=space.currency,
                                                                      amount=amount),
                        comment=description,
                        tink_id=transaction.get('id'),
                        tink_account=account,
                        father_space=space,
                        created=transaction_date
                    )

        return Response({"detail": "Accounts and transactions updated successfully."}, status=status.HTTP_200_OK)


class ListTinkAccountsView(generics.GenericAPIView):
    serializer_class = TinkAccountSerializer

    def get(self, request, space_pk):
        queryset = TinkAccount.objects.filter(space_id=space_pk)
        serializer = TinkAccountSerializer(queryset, many=True)
        return Response(serializer.data)
