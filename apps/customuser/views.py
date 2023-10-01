from rest_framework import generics, permissions, authentication
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import CustomUser
from .serializers import (
    CustomUserSerializer,
    EmailTokenObtainPairSerializer,
    VerifyEmailSerializer,
    ResetPasswordSerializer,
)
from .utils import *


class CustomUserRegistrationView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (permissions.AllowAny,)



class CustomTokenObtainPairView(TokenObtainPairView):
    """
    View to receive a JWT-token via e-mail.
    """

    serializer_class = EmailTokenObtainPairSerializer



class VerifyEmailView(generics.UpdateAPIView):
    '''
    Verification almost
    '''
    serializer_class = VerifyEmailSerializer
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (authentication.TokenAuthentication, authentication.SessionAuthentication)



class SendVerifCodeView(generics.RetrieveAPIView):
    """
    Sending a verification code
    """
    serializer_class = CustomUserSerializer
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (authentication.TokenAuthentication, authentication.SessionAuthentication)


    def get(self, request, *args, **kwargs):
        user = CustomUser.objects.get(email=request.user.email)

        try:
            code = getVerifyCode()
            sendCodeToNewUser(user.email, code, "register")

            user.verify_code = code
            user.save()

            return Response({"message": "successfully"})

        except Exception:
            return Response({"message": "sending error"})



class SendResetCodeView(generics.RetrieveAPIView):
    '''
    sending a code for reset password
    '''
    serializer_class = CustomUserSerializer
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (authentication.TokenAuthentication, authentication.SessionAuthentication)


    def get(self, request, *args, **kwargs):
        user = CustomUser.objects.get(email=request.user.email)

        try:
            code = getVerifyCode()
            sendCodeToNewUser(user.email, code, "resetPassword")

            user.password_reset_code = code
            user.save()

            return Response({"message": "successfully"})

        except Exception:
            return Response({"message": "sending error"})



class ResetPasswordView(generics.UpdateAPIView):
    '''
    Verification almost
    '''
    serializer_class = ResetPasswordSerializer
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (authentication.TokenAuthentication, authentication.SessionAuthentication)