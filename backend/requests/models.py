from django.db import models
import uuid
from requests.storage_backends import UploadedStorage, EditedStorage
from django.core.files.base import ContentFile


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


class File(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    request = models.ForeignKey(Request, on_delete=models.CASCADE)

    @classmethod
    def get_by_id(cls, id):
        return cls.objects.get(id=id)

    class Meta:
        abstract = True


class UploadedFile(File):
    status = models.CharField(max_length=10, choices=RequestStatus.choices,
                              default=RequestStatus.WAITING)
    uploaded_name = models.CharField(max_length=100)

    file = models.FileField(storage=UploadedStorage())
    
    def get_file_data(self):
        with self.file.file.open('rb') as f:
            return f.read()

    @classmethod
    def create_file(cls, request: Request, uploaded_name: str, file):
        id = uuid.uuid4()
        file.name = str(id) + "." + uploaded_name.split('.')[-1]
        
        return cls.objects.create(id=id, request=request, uploaded_name=uploaded_name, file=file)



class EditedFile(File):
    file = models.FileField(storage=EditedStorage())

    @classmethod
    def create_file(cls, request: Request, name: str, data):
        file = ContentFile(data, name=name)
        
        return cls.objects.create(request=request, file=file)
