import requests

from celery import shared_task

from backend.apps.converter.models import Currency

import environ
import os

env = environ.Env()
BASE_DIR = os.path.dirname(os.path.abspath("../../.."))
environ.Env.read_env(os.path.join(BASE_DIR, "../../../config/dev.env"))


@shared_task(bing=True)
def update_rates():
    url = str.__add__('http://data.fixer.io/api/latest?access_key=', env("FIXER_API_TOKEN"))
    data = requests.get(url).json()
    rates = data["rates"]

    for i in Currency.objects.all():
        i.euro = rates[i.iso_code]
        i.save()
    return "All rates updated"
