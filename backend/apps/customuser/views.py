from rest_framework import generics, permissions, authentication, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView

from django.db import transaction

from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from django.conf import settings

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


class CustomUserRegistrationView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (permissions.AllowAny,)


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

            return Response({'detail': 'Registration verified.'}, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Unknown code.'}, status=status.HTTP_400_BAD_REQUEST)


class SendResetCodeView(generics.RetrieveAPIView):
    """
    sending a code for reset password
    """
    serializer_class = CustomUserSerializer
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (authentication.TokenAuthentication, authentication.SessionAuthentication)

    def get(self, request, *args, **kwargs):
        user = CustomUser.objects.get(email=request.user.email)

        try:
            code = get_verify_code()
            send_code_to_new_user(user.email, code, "resetPassword")

            user.password_reset_code = code
            user.save()

            return Response({"message": "successfully"})

        except (Exception,):
            return Response({"message": "sending error"})


class ResetPasswordView(generics.UpdateAPIView):
    """
    Verification almost
    """
    serializer_class = ResetPasswordSerializer
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (authentication.TokenAuthentication, authentication.SessionAuthentication)
