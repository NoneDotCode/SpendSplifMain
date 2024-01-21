from django.core.mail import send_mail

from random import randint


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
