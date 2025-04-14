from django.views.generic.edit import FormView
from .forms import FileFieldForm
from .models import UploadedImage
from django.conf import settings
from django.core.files.storage import FileSystemStorage

def handle_uploaded_file(file):
    fs = FileSystemStorage(location=settings.MEDIA_ROOT / 'uploads/')
    filename = fs.save(file.name, file)
    return fs.url(filename)

class FileFieldFormView(FormView):
    form_class = FileFieldForm
    template_name = "upload_images.html"  # Replace with your template.
    success_url = "/"  # Replace with your URL or reverse().

    def form_valid(self, form):
        files = form.cleaned_data["file_field"]
        for file in files:
            if file.name.endswith('.jpg') or file.name.endswith('.png'):
                file_url = handle_uploaded_file(file)
                # UploadedImage.objects.create(image=file_url)
            else:
                print("Not an image")
        return super().form_valid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))