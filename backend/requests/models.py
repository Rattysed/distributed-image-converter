from django.db import models

from requests.storage_backends import PublicMediaStorage


class Request(models.Model):
    test_field = models.IntegerField()

    def __str__(self):
        return str(self.test_field)


class Upload(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(storage=PublicMediaStorage())







