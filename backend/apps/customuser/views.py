from rest_framework import generics, permissions, authentication, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from backend.apps.customuser.models import CustomUser
from backend.apps.customuser.serializers import (
    CustomUserSerializer,
    EmailTokenObtainPairSerializer,
    VerifyEmailSerializer,
    ResetPasswordSerializer,
)
from backend.apps.customuser.utils import get_verify_code, send_code_to_new_user


class CustomUserRegistrationView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (permissions.AllowAny,)


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    View to receive a JWT-token via e-mail.
    """

    serializer_class = EmailTokenObtainPairSerializer


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
