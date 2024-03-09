from rest_framework import generics, permissions, authentication, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from django.conf import settings

from backend.apps.customuser.models import CustomUser
from backend.apps.customuser.serializers import (
    CustomUserSerializer,
    EmailTokenObtainPairSerializer,
    VerifyEmailSerializer,
    ResetPasswordSerializer,
)
from backend.apps.customuser.utils import get_verify_code, send_code_to_new_user, cookie_response_payload_handler


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


class ConfirmRegistrationView(APIView):
    permission_classes = (permissions.AllowAny,)
    def post(self, request, *args, **kwargs):
        verify_code = request.data.get('verify_code')
        user = CustomUser.objects.filter(verify_code=verify_code).first()

        if user:
            user.is_active = True
            user.verify_code = "verified"
            user.save()
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
