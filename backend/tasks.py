from requests.models import Request
from time import sleep
from requests.cutom_image_handler import ImageHandler

from backend.celery import app

@app.task
def task1(number):
    res = Request.objects.create(test_field=number)
    return True

# Изменить изображение 
@app.task
def task2(request_id, file_id):
    image_handler = ImageHandler()
    image = image_handler.download_from_s3(str(request_id) + '/' + str(file_id))
    
    edited_image = image_handler.edit(image)
    
    image_handler.upload_to_s3(
        file_name=str(request_id) + '/' + str(file_id),
        file_content=edited_image
    )
    
    return True