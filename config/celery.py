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
    }
}

app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Request {self.request!r}")
