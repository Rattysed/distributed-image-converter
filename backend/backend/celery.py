import os
import datetime

from celery import Celery
from django.conf import settings
from dataclasses import dataclass

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

app = Celery("backend")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()

@dataclass
class TaskSchedule:
    task: str
    schedule: datetime.timedelta
    args: tuple = ()

app.conf.beat_schedule = {
    'delete-requests': TaskSchedule(
        task='tasks.task_clear_requests',
        schedule=datetime.timedelta(minutes=1),
        args=()
    ).__dict__,
}