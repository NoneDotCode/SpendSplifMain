import requests

from celery import shared_task

from apps.converter.models import Currency

import environ
import os

from apps.total_balance.models import TotalBalance

from apps.space.models import Space

from apps.category.models import Category

env = environ.Env()
BASE_DIR = os.path.dirname(os.path.abspath("../../config/.."))
environ.Env.read_env(os.path.join(BASE_DIR, "dev.env"))


@shared_task(bing=True)
def update_rates():
    url = str.__add__('http://data.fixer.io/api/latest?access_key=', env("FIXER_API_TOKEN"))
    data = requests.get(url).json()
    rates = data["rates"]

    for i in Currency.objects.all():
        old_rate = i.euro
        new_rate = rates[i.iso_code]
        i.euro = new_rate
        i.save()

        total_balances = TotalBalance.objects.filter(currency=i.iso_code)
        for total_balance in total_balances:
            total_balance.balance = float(total_balance.balance) * (new_rate / float(old_rate))
            total_balance.save()
            space = Space.objects.get(pk=total_balance.father_space_id)
            for category in Category.objects.filter(father_space=space):
                category.spent = float(category.spent) * (new_rate / float(old_rate))
                category.save()
    return "All rates updated"
