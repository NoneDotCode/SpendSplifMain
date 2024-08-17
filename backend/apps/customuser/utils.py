from django.core.mail import send_mail
from django.conf import settings

from rest_framework_simplejwt.tokens import RefreshToken

from random import randint

from datetime import datetime
from django.utils.html import strip_tags


from django.core.mail import send_mail
from django.utils.html import strip_tags

def send_code_for_verify_email(email: str, code: int, flag: str):
    from_email = 'spendsplif@gmail.com'
    to_email = email

    if flag == "registration":
        subject = f'Verification Code: {code} - SpendSplif Registration'
        html_message = f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SpendSplif Email Verification</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .code {{
            font-size: 24px;
            font-weight: bold;
            color: #FFA800;
            text-align: center;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Welcome to SpendSplif</h1>
        <div class="code">{code}</div>
        <p>Dear User,</p>
        <p>Welcome to SpendSplif - your reliable assistant in personal finance management. We are glad that you have joined our community and would like to confirm your account registration.</p>
        <p>To verify your email address, please enter the verification code above in the appropriate field in the application.</p>
        <p>After successful confirmation, you will be able to fully utilize all the features of SpendSplif for tracking income, controlling expenses, and achieving your financial goals.</p>
        <p>Feel free to contact us if you have any questions or need assistance. We are always happy to help!</p>
        <p>We wish you a pleasant and effective experience using SpendSplif!</p>
        <p>Sincerely,<br>The SpendSplif Team</p>
    </div>
</body>
</html>
        '''
        text_message = f"{code}\n\n" + strip_tags(html_message)
    elif flag == "change email":
        subject = f"Verification Code: {code} - SpendSplif Email Change"
        html_message = f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SpendSplif Email Verification</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .code {{
            font-size: 24px;
            font-weight: bold;
            color: #FFA800;
            text-align: center;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Email Verification</h1>
        <div class="code">{code}</div>
        <p>Please use the code above to verify your email change in the SpendSplif application.</p>
    </div>
</body>
</html>
        '''
        text_message = f"{code}\n\nPlease use this code to verify your email change in the SpendSplif application."
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
