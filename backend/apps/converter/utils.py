from backend.apps.converter.models import Currency

import decimal

from decimal import Decimal
from typing import Union


def convert_currencies(*, from_currency, to_currency, amount: float):
    euro_amount = decimal.Decimal(amount) / Currency.objects.get(iso_code=from_currency).euro
    converted_amount = round(euro_amount * Currency.objects.get(iso_code=to_currency).euro, 2)
    return converted_amount


def convert_number_to_letter(number: Union[int, float, Decimal]) -> str:
    """Convert a number to string with multiplier
    for example from 1700 to 1.7k"""

    suffixes = {1000000000: 'b', 1000000: 'm', 1000: 'k'}

    if number == 0:
        return '0'

    def is_whole(n):
        return n == int(n)

    def format_number(n):
        if isinstance(n, Decimal):
            formatted = str(n.normalize()).rstrip('0').rstrip('.')
        else:
            formatted = f"{n:.10f}".rstrip('0').rstrip('.')
        return formatted.rstrip('.0')  # Удаляем '.0' в конце, если оно есть

    number = abs(number)  # Обрабатываем абсолютное значение
    for key in sorted(suffixes.keys(), reverse=True):
        if number >= key:
            cuted_number = number / key
            if is_whole(cuted_number):
                return f"{int(cuted_number)}{suffixes[key]}"
            else:
                formatted = format_number(cuted_number)
                # Ограничиваем до одного знака после запятой, если есть дробная часть
                parts = formatted.split('.')
                if len(parts) > 1:
                    formatted = f"{parts[0]}.{parts[1][:1]}"
                formatted = formatted.rstrip('.0')  # Удаляем '.0' в конце, если оно есть
                return f"{formatted}{suffixes[key]}"

    # Если число меньше 1000
    if is_whole(number):
        return str(int(number))
    else:
        return format_number(number)
