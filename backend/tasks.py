from requests.models import Request, UploadedFile, EditedFile
from time import sleep
from requests.cutom_image_handler import ImageHandler

import zipfile
from io import BytesIO

from django.utils import timezone

from backend.celery import app

@app.task
def task_image_edit(file_id):
    try:
        image = UploadedFile.get_by_id(file_id)

        image_handler = ImageHandler()

        edited_image = image_handler.edit(image.get_file_data())

        file = EditedFile.create_file(image.request, image.uploaded_name, edited_image)
    except Exception:
        return file_id, False
    
    return file.id, True


@app.task
def task_to_zip(file_ids):
    example_id = None

    buffer_archive = BytesIO()
    with zipfile.ZipFile(buffer_archive, 'w') as archive:
        for file_id, is_edited in file_ids:
            if not is_edited:
                continue

            example_id = file_id
            file = EditedFile.get_by_id(file_id)
            buffer_file = file.get_file_data()
            archive.writestr(file.file.name, buffer_file)
    buffer_archive.seek(0)

    if example_id is None:
        request = UploadedFile.get_by_id(file_ids[0][0]).request
        request.delete()
        return False

    file_example = EditedFile.get_by_id(example_id)
    
    file_example.request.update_file(str(file_example.request.id) + '.zip', buffer_archive.getvalue())
    file_example.request.update_status_done()
    
    file_example.request.update_expiration_date()

    return True


@app.task
def task_clear_requests():
    print(timezone.now())
    requests = Request.objects.all()
    for request in requests:
        if request.expiration_date < timezone.now():
            request.delete()
        
    return True
