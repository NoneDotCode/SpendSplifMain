from django.core.mail import send_mail
from django.conf import settings

from rest_framework_simplejwt.tokens import RefreshToken

from random import randint

from datetime import datetime


def send_code_to_new_user(email: str, code: int, flag: str):
    """
    Sending a verification code to a new user
    """
    if flag == "register":
        subject: str = "registration"
        message: str = f'''
                        Thank you for registering on our website!
                        Your email verification code: {code}
                        '''
    else:
        subject: str = "password reset"
        message: str = f'''
                        Your password reset code: {code}
                        '''

    send_mail(
        subject=subject,
        message=message,
        from_email="spendsplif@gmail.com",
        recipient_list=[email],
    )

    return True


def get_verify_code():
    """
    Returns verification code
    """
    return randint(1000, 9999)


def cookie_response_payload_handler(token, user=None, request=None):
    payload = dict()
    payload['access'] = str(token)  # Возвращаем только access_token

    refresh = RefreshToken.for_user(user)
    refresh_cookie_payload = dict()
    refresh_cookie_payload['refresh'] = str(refresh)
    refresh_cookie_payload['exp'] = datetime.utcnow() + settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME']
    refresh_cookie_payload['iat'] = datetime.utcnow()

    payload['refresh_cookie_payload'] = refresh_cookie_payload

    return payload
