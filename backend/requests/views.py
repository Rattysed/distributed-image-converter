from django import forms
from django.views.generic.edit import FormView
from .forms import FileFieldForm


class FileFieldFormView(FormView):
    form_class = FileFieldForm
    template_name = "upload_images.html"  # Replace with your template.
    success_url = "/"  # Replace with your URL or reverse().

    def form_valid(self, form):
        files = form.cleaned_data["file_field"]
        for f in files:
            if not f.name.lower().endswith('.jpg'):
                raise forms.ValidationError(f"Файл {f.name} не является JPG изображением.")
        return super().form_valid(form)