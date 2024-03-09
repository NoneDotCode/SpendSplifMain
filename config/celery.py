from __future__ import absolute_import, unicode_literals
import os

from celery import Celery
from celery.schedules import crontab

from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
app = Celery("config")
app.config_from_object(settings, namespace="CELERY")

# Celery Beat settings

app.conf.beat_schedule = {
    "clear_spent_in_categories_every_month": {
        "task": "apps.category.tasks.clear_all_spent",
        "schedule": crontab(hour="00", minute="00", day_of_month="01")
    },
    "update_rates_for_converter_every_day": {
        "task": "apps.converter.tasks.update_rates",
        "schedule": crontab(hour="00", minute="00")
    },
    'update_stock_prices_1_every_11_minutes': {
        'task': 'apps.api_stocks.tasks.update_stock_prices_1',
        'schedule': crontab(minute="*/11"),
    },
    'update_stock_prices_2_every_13_minutes': {
        'task': 'apps.api_stocks.tasks.update_stock_prices_2',
        'schedule': crontab(minute="*/13"),
    },
    'update_stock_prices_3_every_14_minutes': {
        'task': 'apps.api_stocks.tasks.update_stock_prices_3',
        'schedule': crontab(minute="*/14"),
    },
    'update_stock_prices_4_every_10_minutes': {
        'task': 'apps.api_stocks.tasks.update_stock_prices_4',
        'schedule': crontab(minute="*/10"),
    },
    'update_stock_prices_5_every_12_minutes': {
        'task': 'apps.api_stocks.tasks.update_stock_prices_5',
        'schedule': crontab(minute="*/12")
    },
    "update_crypto_prices_every_2_minutes": {
        "task": "apps.cryptocurrency.tasks.update_crypto_prices",
        "schedule": crontab(minute="*/2"),
    },
}

app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Request {self.request!r}")
