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
    "update_rates_for_converter_every_day": {
        "task": "backend.apps.converter.tasks.update_rates",
        "schedule": crontab(hour="00", minute="00")
    },
    "update_crypto_prices_every_2_minutes": {
        "task": "backend.apps.cryptocurrency.tasks.update_crypto_prices",
        "schedule": crontab(minute="*/2")
    }
}

app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Request {self.request!r}")
