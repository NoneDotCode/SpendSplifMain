from random import randint


def get_verify_code():
    """
    Returns verification code
    """
    return randint(1000, 9999)
