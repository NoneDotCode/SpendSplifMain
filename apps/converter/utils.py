import requests
import datetime

from apps.converter.models import Currency
from apps.converter.constants import CURRENCIES


def update_currencies():
    model = Currency.objects.get(pk=1)
    if model.time_update.day < datetime.datetime.now().day or \
            model.time_update.month < datetime.datetime.now().month or \
            model.time_update.year < datetime.datetime.now().year:
        url = str.__add__('http://data.fixer.io/api/latest?access_key=', "65268712d3852ba0ad7d085115ac7118")
        data = requests.get(url).json()
        rates = data["rates"]

        for i in Currency.objects.all():
            i.euro = rates[i.iso_code]
            i.save()
