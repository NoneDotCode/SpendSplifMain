from backend.apps.converter.models import Currency

import decimal


def convert_currencies(*, from_currency, to_currency, amount: float):
    euro_amount = decimal.Decimal(amount) / Currency.objects.get(iso_code=from_currency).euro
    converted_amount = round(euro_amount * Currency.objects.get(iso_code=to_currency).euro, 2)
    return converted_amount
