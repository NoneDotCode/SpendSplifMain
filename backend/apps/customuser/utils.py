from django.core.mail import send_mail
from django.conf import settings

from rest_framework_simplejwt.tokens import RefreshToken

from random import randint

from datetime import datetime
from django.utils.html import strip_tags
from backend.apps.customuser import translate

from django.core.mail import send_mail
from django.utils.html import strip_tags


def send_code_for_verify_email(email: str, code: str, flag: str, language: str):
    from_email = 'spendsplif@spendsplif.com'
    to_email = email

    if flag == "registration":
        subject = f'Verification Code: {code} - SpendSplif Registration'
        html_message = translate.reg_message(code=code, language=language)
        text_message = f"{code}\n\n" + strip_tags(html_message)
    elif flag == "change email":
        subject = f"Verification Code: {code} - SpendSplif Email Change"
        html_message = translate.change_email_message(code=code, language=language)
        text_message = f"{code}\n\n" + strip_tags(html_message)
    else:
        raise ValueError("Invalid flag provided")

    send_mail(
        subject=subject,
        message=text_message,
        from_email=from_email,
        recipient_list=[to_email],
        html_message=html_message,
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
