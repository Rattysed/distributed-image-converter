from requests.models import Request

from backend.celery import app

@app.task
def task1(number):
    res = Request.objects.create(test_field=number)
    return True
