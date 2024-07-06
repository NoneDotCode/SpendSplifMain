from rest_framework import generics, permissions, authentication, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView

from django.db import transaction

from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from django.conf import settings

from backend.apps.account.models import Account
from backend.apps.category.models import Category
from backend.apps.customuser.models import CustomUser
from backend.apps.customuser.serializers import (
    CustomUserSerializer,
    EmailTokenObtainPairSerializer,
    VerifyEmailSerializer,
    CustomTokenRefreshSerializer,
    ResetPasswordSerializer,
)
from backend.apps.customuser.utils import get_verify_code, send_code_to_new_user, cookie_response_payload_handler

from backend.apps.space.models import Space, MemberPermissions

from backend.apps.messenger.models import SpaceGroup

from datetime import datetime

from backend.apps.total_balance.models import TotalBalance


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
    def post(self, request, *args, **kwargs):
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

            return Response({'detail': 'Registration verified.'}, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Unknown code.'}, status=status.HTTP_400_BAD_REQUEST)


class ConfirmNewEmailView(APIView):
    def post(self, request, *args, **kwargs):
        verify_code = request.data.get('verify_code')
        code_from_new_email = request.data.get('code_from_new_email')

        if request.user.verify_code == verify_code and request.user.code_from_new_email == code_from_new_email:
            request.user.verify_code = "verified"
            request.user.code_from_new_email = None
            request.user.email = request.user.new_email
            request.user.new_email = None
            request.user.save()
            return Response({'detail': 'Email verified.'}, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Unknown code.'}, status=status.HTTP_400_BAD_REQUEST)


class CustomUserUpdateAPIView(generics.UpdateAPIView):
    serializer_class = CustomUserSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        partial = True
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance = self.get_object()
            serializer = self.get_serializer(instance)

        return Response(serializer.data)
