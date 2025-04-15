from django.http import JsonResponse, HttpResponseNotFound

from django.shortcuts import render, get_object_or_404


from .models import Request, UploadedFile, UploadedFile, EditedFile
from tasks import task_image_edit, task_to_zip, task_clear_request
from celery import chord, group

from django.views.generic.edit import FormView
from .forms import FileFieldForm
from django.core.files.storage import FileSystemStorage


def get_task_status(request_id):
    return Request.is_request_done(request_id)


def request_status(request, request_id):
    try:
        if Request.get_request(request_id) is None:
            return HttpResponseNotFound("404, No request")
    except Exception as e:
        return HttpResponseNotFound("404, No request")
    return render(request, 'request.html', {'request_id': request_id})


def check_status(request, request_id):
    try:
        task = Request.get_request(request_id)
        url = task.get_resulting_link()
        return JsonResponse({'status': 'ready', 'link': f'{url}'})
    except Exception as e:
        print(e)
        return JsonResponse({'status': 'pending'})


class FileFieldFormView(FormView):
    form_class = FileFieldForm
    template_name = "upload_images.html"
    success_url = "/"

    def form_valid(self, form):
        files = form.cleaned_data["file_field"]
        request = Request.create_request()
        file_ids = []
        
        for file in files:
            if file.name.endswith('.jpg') or file.name.endswith('.jpeg') or file.name.endswith('.png'):
                file_ids.append(UploadedFile.create_file(request, file.name, file).id)
            else:
                print("Not an image")
        
        tasks = group(task_image_edit.s(file_id) for file_id in file_ids)
        res = chord(tasks)(task_to_zip.s())
            
        self.success_url = f"/request/{str(request.id)}"
        return super().form_valid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))
