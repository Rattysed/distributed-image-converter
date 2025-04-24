import os

from celery import Celery
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

app = Celery("backend")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.conf.worker_send_task_events = True
app.worker_send_task_events = True

app.autodiscover_tasks()
