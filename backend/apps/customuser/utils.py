from django.core.mail import send_mail
from django.conf import settings

from rest_framework_simplejwt.tokens import RefreshToken

from random import randint

from datetime import datetime

from email.message import EmailMessage
from email.utils import formataddr
import smtplib
import ssl


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


def send_code_for_verify_email(email: str, code: int, flag: str):
    smtp_server = "smtp.gmail.com"
    port = 587  # Для TLS
    sender_email = "spendsplif@gmail.com"
    password = "your_app_password_here"  # Используйте пароль приложения для Gmail

    if flag == "registration":
        subject = 'Email Verification'
        text_message = f'''
Dear User,

Welcome to SpendSplif - your reliable assistant in personal finance management. We are glad that you have joined our community and would like to confirm your account registration.

To verify your email address, please enter the following verification code in the appropriate field in the application:

{code}

After successful confirmation, you will be able to fully utilize all the features of SpendSplif for tracking income, controlling expenses, and achieving your financial goals.

Feel free to contact us if you have any questions or need assistance. We are always happy to help!

We wish you a pleasant and effective experience using SpendSplif!

Sincerely,
The SpendSplif Team
        '''
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
            color: #4CAF50;
            text-align: center;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Welcome to SpendSplif</h1>
        <p>Dear User,</p>
        <p>We are glad that you have joined our community and would like to confirm your account registration.</p>
        <p>To verify your email address, please enter the following verification code in the appropriate field in the application:</p>
        <div class="code">{code}</div>
        <p>After successful confirmation, you will be able to fully utilize all the features of SpendSplif for tracking income, controlling expenses, and achieving your financial goals.</p>
        <p>Feel free to contact us if you have any questions or need assistance. We are always happy to help!</p>
        <p>We wish you a pleasant and effective experience using SpendSplif!</p>
        <p>Sincerely,<br>The SpendSplif Team</p>
    </div>
</body>
</html>
        '''
    elif flag == "change email":
        subject = "Email Verification"
        text_message = f"Your verification code is: {code}"
        html_message = f"<html><body><h2>Your verification code is: <span style='color: #4CAF50;'>{code}</span></h2></body></html>"

    # Создаем объект EmailMessage
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = formataddr(("SpendSplif", sender_email))
    msg['To'] = email
    msg['X-Priority'] = '1'  # Высокий приоритет
    msg['X-MSMail-Priority'] = 'High'
    msg['Importance'] = 'High'
    msg['X-Entity-Ref-ID'] = str(code)  # Добавляем код в заголовок

    # Добавляем текстовую и HTML версии письма
    msg.set_content(text_message)
    msg.add_alternative(html_message, subtype='html')

    # Создаем защищенное SSL соединение
    context = ssl.create_default_context()

    try:
        # Подключаемся к серверу и отправляем письмо
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls(context=context)
            server.login(sender_email, password)
            server.send_message(msg)
        print(f"Email sent successfully to {email}")
        return True
    except Exception as e:
        print(f"Error sending email to {email}: {str(e)}")
        return False


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
