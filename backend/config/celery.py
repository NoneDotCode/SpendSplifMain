from __future__ import absolute_import, unicode_literals
import os
import sys

from celery import Celery
from celery.schedules import crontab

from django.conf import settings

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
app = Celery("backend.config")
app.config_from_object(settings, namespace="CELERY")
app.conf.broker_connection_retry_on_startup = True

# Celery Beat settings
app.conf.beat_schedule = {
    "clear_spent_in_categories_every_month": {
        "task": "backend.apps.category.tasks.clear_all_spent",
        "schedule": crontab(hour="00", minute="00", day_of_month="01")
    },
    "update_finapi_tokens_hourly": {
        "task": "backend.apps.cards.tasks.update_finapi_tokens",
        "schedule": crontab(minute="0"),  
    },
    "delete_not_verify_users_every_day": {
        "task": "backend.apps.account.tasks.delete_not_verify_users",
        "schedule": crontab(hour="00", minute="00"),
    },
    "update_rates_for_converter_every_day": {
        "task": "backend.apps.converter.tasks.update_rates",
        "schedule": crontab(hour="00", minute="00")
    },
    'update_stock_prices_1_every_11_minutes': {
        'task': 'backend.apps.api_stocks.tasks.update_stock_prices_1',
        'schedule': crontab(minute="*/11"),
    },
    'update_stock_prices_2_every_13_minutes': {
        'task': 'backend.apps.api_stocks.tasks.update_stock_prices_2',
        'schedule': crontab(minute="*/13"),
    },
    'update_stock_prices_3_every_14_minutes': {
        'task': 'backend.apps.api_stocks.tasks.update_stock_prices_3',
        'schedule': crontab(minute="*/14"),
    },
    'update_stock_prices_4_every_10_minutes': {
        'task': 'backend.apps.api_stocks.tasks.update_stock_prices_4',
        'schedule': crontab(minute="*/10"),
    },
    'update_stock_prices_5_every_12_minutes': {
        'task': 'backend.apps.api_stocks.tasks.update_stock_prices_5',
        'schedule': crontab(minute="*/12")
    },
    "update_crypto_prices_every_2_minutes": {
        "task": "backend.apps.cryptocurrency.tasks.update_crypto_prices",
        "schedule": crontab(minute="*/2"),
    },
    "create_space_backup_end_of_month": {
        "task": "backend.apps.space.tasks.create_space_backup",
        "schedule": crontab(hour="23", minute="59", day_of_month="last"),
    },
}

app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Request {self.request!r}")
