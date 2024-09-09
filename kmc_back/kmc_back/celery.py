import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kmc_back.settings")

app = Celery("kmc_back")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


app.conf.beat_schedule = {
    "run-every-minute": {
        "task": "order.tasks.cancel_orders",
        "schedule": crontab(minute="*"),
    },
}


# @app.task(bind=True)
# def debug_task(self):
#     print(f"Request: {self.request!r}")