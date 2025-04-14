from requests.models import Request, UploadedFile, EditedFile
from time import sleep
from requests.cutom_image_handler import ImageHandler

from backend.celery import app


@app.task
def task1(number):
    res = Request.objects.create(test_field=number)
    return True

# Изменить изображение


@app.task
def task2(file_id):
    image = UploadedFile.get_by_id(file_id)

    image_handler = ImageHandler()
    
    edited_image = image_handler.edit(image.get_file_data())

    EditedFile.create_file(image.request, image.uploaded_name, edited_image)

    return True
