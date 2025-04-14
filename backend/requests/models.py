from django.db import models
import uuid
from requests.storage_backends import UploadedStorage, EditedStorage


class RequestStatus(models.TextChoices):
    WAITING = 'waiting', 'Waiting'
    PROCESSING = 'processing', 'Processing'
    DONE = 'done', 'Done'


class Request(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status = models.CharField(max_length=10, choices=RequestStatus.choices,
                              default=RequestStatus.WAITING)
    time_end = models.DateTimeField(null=True, blank=True)

    @classmethod
    def create_request(cls):
        return cls.objects.create()

    def __str__(self):
        return str(self.id) + " — " + str(self.status)


class UploadedFile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status = models.CharField(max_length=10, choices=RequestStatus.choices,
                              default=RequestStatus.WAITING)
    request = models.ForeignKey(Request, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default=uuid.uuid4)

    data = models.FileField(storage=UploadedStorage())

    @classmethod
    def create_file(cls, request: Request, name: str, data):
        id = uuid.uuid4()
        name = str(id) + "." + name.split('.')[-1]
        return cls.objects.create(id=id, request=request, name=name, data=data)


class EditedFile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    request = models.ForeignKey(Request, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default=uuid.uuid4)

    data = models.FileField(storage=EditedStorage())

    @classmethod
    def create_file(cls, request: Request, name: str, data):
        return cls.objects.create(request=request, name=name, data=data)
