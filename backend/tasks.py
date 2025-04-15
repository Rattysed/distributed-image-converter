from requests.models import Request, UploadedFile, EditedFile
from time import sleep
from requests.cutom_image_handler import ImageHandler

import zipfile
from io import BytesIO

from backend.celery import app


@app.task
def task_image_edit(file_id):
    image = UploadedFile.get_by_id(file_id)

    image_handler = ImageHandler()
    
    edited_image = image_handler.edit(image.get_file_data())

    file = EditedFile.create_file(image.request, image.uploaded_name, edited_image)

    return file.id

@app.task
def task_to_zip(file_ids):
    
    buffer_archive = BytesIO()
    with zipfile.ZipFile(buffer_archive, 'w') as archive:
        for file_id in file_ids:
            file = EditedFile.get_by_id(file_id)
            buffer_file = file.get_file_data()
            archive.writestr(file.file.name, buffer_file)
    buffer_archive.seek(0)
    
    file_1 = EditedFile.get_by_id(file_ids[0])
    
    file_1.request.update_file(str(file_1.request.id) + '.zip', buffer_archive.getvalue())
    file_1.request.update_status_done()

    return True

@app.task
def task_clear_request(request_id):
    request = Request.objects.get(id=request_id)
    
    uploaded_files = UploadedFile.objects.filter(request=request)
    for uploaded_file in uploaded_files:
        uploaded_file.delete_file()
        
    edited_files = EditedFile.objects.filter(request=request)
    for edited_file in edited_files:
        edited_file.delete_file()
        
    request.delete_file()
    request.delete()
    
    return True