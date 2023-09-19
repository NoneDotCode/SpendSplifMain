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
        "task": "category.tasks.clear_all_spent",
        # "schedule": crontab(day_of_month="1", hour="0", minute="0")
        "schedule": crontab(hour="15", minute="02")
    }
}

app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Request {self.request!r}")
