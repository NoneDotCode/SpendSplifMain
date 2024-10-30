from typing import Dict

import jwt
from rest_framework import generics, permissions
from rest_framework.generics import GenericAPIView


from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.views import TokenObtainPairView
from random import SystemRandom
from urllib.parse import urlencode

from django.shortcuts import redirect
from rest_framework.views import APIView

from backend.apps.account.models import Account
from backend.apps.category.models import Category
from backend.apps.customuser.models import CustomUser
from backend.apps.customuser.serializers import (
    CustomUserSerializer,
    CustomTokenRefreshSerializer, CheckAppVersionSerializer,
)
from backend.apps.customuser.utils import cookie_response_payload_handler
from rest_framework.exceptions import APIException

from backend.apps.notifications.models import Notification
from backend.apps.space.models import Space, MemberPermissions
from rest_framework import serializers, status
from django.urls import reverse_lazy


from datetime import datetime

from backend.apps.total_balance.models import TotalBalance
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from google.auth.transport import requests
from attr import define
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from google.oauth2 import id_token
from oauthlib.common import UNICODE_ASCII_CHARACTER_SET
import requests as requestss


class CustomUserRegistrationView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (permissions.AllowAny,)


class UserProfileView(generics.RetrieveAPIView):
    serializer_class = CustomUserSerializer

    def get_object(self):
        return self.request.user


class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            raise e

        user = serializer.user
        token = serializer.validated_data['access']
        response_data = cookie_response_payload_handler(token, user, request)

        response = Response(response_data)
        refresh_cookie_payload = response_data.pop('refresh_cookie_payload', None)
        if refresh_cookie_payload:
            response.set_cookie(
                key=settings.SIMPLE_JWT['REFRESH_TOKEN_COOKIE_NAME'],
                value=refresh_cookie_payload['refresh'],
                expires=refresh_cookie_payload['exp'],
                httponly=settings.SIMPLE_JWT['REFRESH_TOKEN_COOKIE_OPTIONS'].get('httponly', True),
                samesite=settings.SIMPLE_JWT['REFRESH_TOKEN_COOKIE_OPTIONS'].get('samesite', 'Lax'),
                secure=settings.SIMPLE_JWT['REFRESH_TOKEN_COOKIE_OPTIONS'].get('secure', True),
            )
        return response


class LogoutView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        response = Response()
        response.delete_cookie(
            key=settings.SIMPLE_JWT['REFRESH_TOKEN_COOKIE_NAME'],
            path=settings.SIMPLE_JWT['REFRESH_TOKEN_COOKIE_OPTIONS'].get('path', '/'),
            samesite=settings.SIMPLE_JWT['REFRESH_TOKEN_COOKIE_OPTIONS'].get('samesite', 'Lax'),
        )
        response.data = {"message": "Logout successful."}
        return response


class CustomTokenRefreshView(GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = CustomTokenRefreshSerializer
    def get(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get(settings.SIMPLE_JWT['REFRESH_TOKEN_COOKIE_NAME'])

        if refresh_token is None:
            return Response({'error': 'Refresh token not found.'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            payload = RefreshToken(refresh_token)
            user = CustomUser.objects.get(id=payload.payload['user_id'])
            if user.is_active:
                access_token = payload.access_token
                new_refresh_token = payload.token
                response_data = {
                    'access': str(access_token),
                }
                response = Response(response_data)

                refresh_token_expiration = datetime.utcnow() + settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME']

                response.set_cookie(
                    key=settings.SIMPLE_JWT['REFRESH_TOKEN_COOKIE_NAME'],
                    value=str(new_refresh_token),
                    expires=refresh_token_expiration,
                    httponly=settings.SIMPLE_JWT['REFRESH_TOKEN_COOKIE_OPTIONS'].get('httponly', True),
                    samesite=settings.SIMPLE_JWT['REFRESH_TOKEN_COOKIE_OPTIONS'].get('samesite', 'Lax'),
                    secure=settings.SIMPLE_JWT['REFRESH_TOKEN_COOKIE_OPTIONS'].get('secure', True),
                    domain=settings.SIMPLE_JWT.get('AUTH_COOKIE_DOMAIN', None),
                )
                return response
            else:
                return Response({'error': 'User is inactive'}, status=status.HTTP_401_UNAUTHORIZED)
        except (TokenError, InvalidToken) as e:
            return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)


class ConfirmRegistrationView(APIView):
    permission_classes = (permissions.AllowAny,)
    def post(self, request, *args, **kwargs):
        verify_code = request.data.get('verify_code')
        currency = request.data.get("currency")
        user = CustomUser.objects.filter(verify_code=verify_code).first()

        if user:
            user.is_active = True
            user.verify_code = "verified"
            user.save()

            space = Space.objects.create(title="Main", currency=currency)

            MemberPermissions.objects.create(
                member=user,
                space=space,
                owner=True
            )

            TotalBalance.objects.create(father_space=space, balance=0)

            Category.objects.create(
                title="Food",
                limit=1000,
                spent=0,
                father_space=space,
                color="#FF9800",
                icon="Donut"
            )

            Category.objects.create(
                title="Home",
                spent=0,
                father_space=space,
                color="#FF5050",
                icon="Home"
            )

            Account.objects.create(
                title="Main",
                balance=0,
                currency=self.request.data.get("currency"),
                father_space=space
            )

            notification = Notification.objects.create(importance="standard",
                                                       message="Welcome, we're glad you're with us. SpendSplif - the "
                                                               "best helper for your financial well-being")
            notification.who_can_view.set((user,))

            return Response({'detail': 'Registration verified.'}, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Unknown code.'}, status=status.HTTP_400_BAD_REQUEST)


class ConfirmNewEmailView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        verify_code = request.data.get('verify_code')
        code_from_new_email = request.data.get('code_from_new_email')

        if request.user.verify_code == verify_code and request.user.code_from_new_email == code_from_new_email:
            request.user.verify_code = "verified"
            request.user.code_from_new_email = None
            request.user.email = request.user.new_email
            request.user.new_email = None
            request.user.save()
            if request.user.new_password:
                request.user.set_password(request.user.new_password)
                request.user.new_password = None
                request.user.password_reset_code = None
                request.user.save()
            return Response({'detail': 'Email verified.'}, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Unknown code.'}, status=status.HTTP_400_BAD_REQUEST)


class CustomUserUpdateAPIView(generics.GenericAPIView):
    serializer_class = CustomUserSerializer

    def get_object(self):
        return self.request.user

    def put(self, request, *args, **kwargs):
        instance = self.get_object()

        if len(request.data) == 1 and 'username' in request.data:
            instance.username = request.data['username']
            instance.save()
            return Response({'username': instance.username})
        
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        return self.put(request, *args, **kwargs)


@define
class GoogleLoginCredentials:
    client_id: str
    client_secret: str
    project_id: str


def google_login_get_credentials() -> GoogleLoginCredentials:
    client_id = settings.GOOGLE_CLIENT_ID
    client_secret = settings.GOOGLE_CLIENT_SECRET
    project_id = settings.GOOGLE_PROJECT_ID

    if not client_id:
        raise ImproperlyConfigured("GOOGLE_CLIENT_ID missing in env.")

    if not client_secret:
        raise ImproperlyConfigured("GOOGLE_CLIENT_SECRET missing in env.")

    if not project_id:
        raise ImproperlyConfigured("GOOGLE_PROJECT_ID missing in env.")

    credentials = GoogleLoginCredentials(
        client_id=client_id,
        client_secret=client_secret,
        project_id=project_id
    )

    return credentials


@define
class GoogleAccessTokens:
    id_token: str
    access_token: str

    def decode_id_token(self) -> Dict[str, str]:
        id_token = self.id_token
        decoded_token = jwt.decode(jwt=id_token, options={"verify_signature": False})
        return decoded_token


class PublicApi(APIView):
    authentication_classes = ()
    permission_classes = ()


class GoogleLoginRedirectApi(PublicApi):
    def get(self, request, *args, **kwargs):
        google_login_flow = GoogleLoginFlowService()

        authorization_url, state = google_login_flow.get_authorization_url()

        request.session["google_oauth2_state"] = state

        return redirect(authorization_url)


class GoogleLoginFlowService:
    API_URI = reverse_lazy("customuser:google_callback")

    GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
    GOOGLE_ACCESS_TOKEN_OBTAIN_URL = "https://oauth2.googleapis.com/token"
    GOOGLE_USER_INFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

    SCOPES = [
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
        "openid",
    ]

    def __init__(self):
        self._credentials = google_login_get_credentials()

    @staticmethod
    def _generate_state_session_token(length=30, chars=UNICODE_ASCII_CHARACTER_SET):
        rand = SystemRandom()
        state = "".join(rand.choice(chars) for _ in range(length))
        return state

    def _get_redirect_uri(self):
        domain = settings.BASE_BACKEND_URL
        api_uri = self.API_URI
        redirect_uri = f"{domain}{api_uri}"
        return redirect_uri

    def get_authorization_url(self):
        redirect_uri = self._get_redirect_uri()

        state = self._generate_state_session_token()

        params = {
            "response_type": "code",
            "client_id": self._credentials.client_id,
            "redirect_uri": redirect_uri,
            "scope": " ".join(self.SCOPES),
            "state": state,
            "access_type": "offline",
            "include_granted_scopes": "true",
            "prompt": "select_account",
        }

        query_params = urlencode(params)
        authorization_url = f"{self.GOOGLE_AUTH_URL}?{query_params}"

        return authorization_url, state

    def get_tokens(self, *, code: str) -> GoogleAccessTokens:
        redirect_uri = self._get_redirect_uri()

        data = {
            "code": code,
            "client_id": self._credentials.client_id,
            "client_secret": self._credentials.client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }

        response = requestss.post(self.GOOGLE_ACCESS_TOKEN_OBTAIN_URL, data=data)

        if not response.ok:
            raise APIException("Failed to obtain access token from Google.")

        tokens = response.json()
        google_tokens = GoogleAccessTokens(
            id_token=tokens["id_token"],
            access_token=tokens["access_token"]
        )

        return google_tokens

    def get_user_info(self, *, google_tokens: GoogleAccessTokens):
        access_token = google_tokens.access_token

        response = requestss.get(
            self.GOOGLE_USER_INFO_URL,
            params={"access_token": access_token}
        )

        if not response.ok:
            raise APIException("Failed to obtain user info from Google.")

        return response.json()


class GoogleLoginApi(APIView):
    permission_classes = ()

    class InputSerializer(serializers.Serializer):
        code = serializers.CharField(required=False)
        error = serializers.CharField(required=False)
        state = serializers.CharField(required=False)

    def get(self, request, *args, **kwargs):
        input_serializer = self.InputSerializer(data=request.GET)
        input_serializer.is_valid(raise_exception=True)

        validated_data = input_serializer.validated_data

        code = validated_data.get("code")
        error = validated_data.get("error")
        state = validated_data.get("state")

        if error is not None:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

        if code is None or state is None:
            return Response({"error": "Missing code or state"}, status=status.HTTP_400_BAD_REQUEST)

        session_state = request.session.get("google_oauth2_state")

        if session_state is None:
            return Response({"error": "CSRF check failed."}, status=status.HTTP_400_BAD_REQUEST)

        del request.session["google_oauth2_state"]

        if state != session_state:
            return Response({"error": "CSRF check failed."}, status=status.HTTP_400_BAD_REQUEST)

        google_login_flow = GoogleLoginFlowService()

        try:
            google_tokens = google_login_flow.get_tokens(code=code)
            id_token_decoded = google_tokens.decode_id_token()
            user_info = google_login_flow.get_user_info(google_tokens=google_tokens)

            email = id_token_decoded["email"]
            username = email.split('@')[0]

            user, created = CustomUser.objects.get_or_create(
                email=email,
                defaults={
                    'username': username,
                    'is_active': True,
                    'verify_code': 'verified'
                }
            )

            response = redirect(settings.FRONTEND_URL)

            if created:
                response = redirect(settings.FRONTEND_URL + "/google/choose_currency")
                user.set_unusable_password()
                user.save()

                currency = validated_data.get('currency', 'USD')
                space = Space.objects.create(title="Main", currency=currency)

                MemberPermissions.objects.create(
                    member=user,
                    space=space,
                    owner=True
                )

                TotalBalance.objects.create(father_space=space, balance=0)

                Category.objects.create(
                    title="Food",
                    limit=1000,
                    spent=0,
                    father_space=space,
                    color="#FF9800",
                    icon="Donut"
                )

                Category.objects.create(
                    title="Home",
                    spent=0,
                    father_space=space,
                    color="#FF5050",
                    icon="Home"
                )

                Account.objects.create(
                    title="Main",
                    balance=0,
                    currency=currency,
                    father_space=space
                )

                notification = Notification.objects.create(importance="standard",
                                                           message="Welcome, we're glad you're with us. SpendSplif - "
                                                                   "the best helper for your financial well-being")
                notification.who_can_view.set((user,))

            refresh = RefreshToken.for_user(user)
            user_data = CustomUserSerializer(user).data

            refresh_token_expiration = datetime.utcnow() + settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME']

            response.set_cookie(
                key=settings.SIMPLE_JWT['REFRESH_TOKEN_COOKIE_NAME'],
                value=str(refresh),
                expires=refresh_token_expiration,
                httponly=True,
                samesite=settings.SIMPLE_JWT['REFRESH_TOKEN_COOKIE_OPTIONS'].get('samesite', 'Lax'),
                secure=settings.SIMPLE_JWT['REFRESH_TOKEN_COOKIE_OPTIONS'].get('secure', True),
            )

            return response

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class GoogleLoginApiMobileView(GenericAPIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        access_token_value = request.data.get("accessToken")  # Получаем access_token

        if not access_token_value:
            return Response({"error": "Missing access_token in the request."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Используем запрос к Google API для валидации и получения данных по access_token
            token_info_url = f"https://www.googleapis.com/oauth2/v1/userinfo?alt=json&access_token={access_token_value}"
            token_info_response = requestss.get(token_info_url)

            if token_info_response.status_code != 200:
                return Response({"error": "Invalid access_token."}, status=status.HTTP_400_BAD_REQUEST)

            id_info = token_info_response.json()

            email = id_info["email"]
            name = id_info.get("name", "")
            username = email.split('@')[0]

            user, created = CustomUser.objects.get_or_create(
                email=email,
                defaults={
                    'username': username,
                    'is_active': True,
                    'verify_code': 'verified'
                }
            )

            if created:
                user.set_unusable_password()
                user.save()

                space = Space.objects.create(title="Main", currency="USD")

                MemberPermissions.objects.create(
                    member=user,
                    space=space,
                    owner=True
                )

                TotalBalance.objects.create(father_space=space, balance=0)

                Category.objects.create(
                    title="Food",
                    limit=1000,
                    spent=0,
                    father_space=space,
                    color="#FF9800",
                    icon="Donut"
                )

                Category.objects.create(
                    title="Home",
                    spent=0,
                    father_space=space,
                    color="#FF5050",
                    icon="Home"
                )

                Account.objects.create(
                    title="Main",
                    balance=0,
                    currency="USD",
                    father_space=space
                )

                notification = Notification.objects.create(importance="standard",
                                                           message="Welcome, we're glad you're with us. SpendSplif - "
                                                                   "the best helper for your financial well-being")
                notification.who_can_view.set((user,))

                action = "registration"
            else:
                action = "login"

            refresh = RefreshToken.for_user(user)
            user_data = CustomUserSerializer(user).data

            response_data = {
                "action": action,
                "user": user_data,
                "access_token": str(refresh.access_token),
            }

            response = Response(response_data, status=status.HTTP_200_OK)

            refresh_token_expiration = datetime.utcnow() + settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME']

            response.set_cookie(
                key=settings.SIMPLE_JWT['REFRESH_TOKEN_COOKIE_NAME'],
                value=str(refresh),
                expires=refresh_token_expiration,
                httponly=True,
                samesite=settings.SIMPLE_JWT['REFRESH_TOKEN_COOKIE_OPTIONS'].get('samesite', 'Lax'),
                secure=settings.SIMPLE_JWT['REFRESH_TOKEN_COOKIE_OPTIONS'].get('secure', True),
            )

            return response

        except requestss.exceptions.RequestException as e:
            return Response({"error": "Error validating access_token."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CheckAppVersion(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = CheckAppVersionSerializer

    def post(self, request, *args, **kwargs):
        actual_version = settings.MOBILE_APP_ACTUAL_VERSION
        if actual_version != request.data['version']:
            return Response({"status": False}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"status": True}, status=status.HTTP_200_OK)


class ConfirmNewPasswordView(GenericAPIView):
    def post(self, request, *args, **kwargs):
        reset_code = request.data.get('reset_code')
        if not reset_code:
            return Response({'detail': 'Reset code is required.'}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user

        if user.password_reset_code == reset_code:
            user.set_password(user.new_password)
            user.new_password = None
            user.password_reset_code = None
            user.save()

            return Response({'detail': 'Password has been reset successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Invalid or expired reset code.'}, status=status.HTTP_400_BAD_REQUEST)
