from backend.apps.converter.models import Currency

import decimal


def convert_currencies(*, from_currency, to_currency, amount: float):
    euro_amount = decimal.Decimal(amount) / Currency.objects.get(iso_code=from_currency).euro
    converted_amount = round(euro_amount * Currency.objects.get(iso_code=to_currency).euro, 2)
    return converted_amount


def convert_number_to_letter(number: float) -> str:
    """Convert a number to string with multiplier 
    for example from 1700 to 1.7k"""

    suffixes = {1000000000: 'b', 1000000: 'm', 1000: 'k'}

    if number:
        for key in sorted(suffixes.keys(), reverse=True):
            if number >= key:
                cuted_number = number / key
                if int(cuted_number) == cuted_number:
                    return f"{int(cuted_number)}{suffixes[key]}"
                else:
                    return f"{cuted_number:.1f}{suffixes[key]}"
        return str(int(number))  # If the number is less than 1000
    else:
        return '0'