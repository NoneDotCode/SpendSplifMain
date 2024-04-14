from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from backend.apps.tink.models import TinkUser

from django.conf import settings

import requests
import json

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
        external_user_id = request.data.get("external_user_id", request.user.pk)
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
        user_id = request.data.get('user_id')
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

        if response.status_code == 200:
            return Response(response.json())
        else:
            return Response(response.json(), status=response.status_code)


class ListTransactionsView(generics.GenericAPIView):
    def get(self, request):
        user_access_token = request.GET.get('user_access_token')
        account_id = request.GET.get('account_id')
        pending = request.GET.get('pending')
        page_size = request.GET.get('page_size')
        page_token = request.GET.get('page_token')

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
