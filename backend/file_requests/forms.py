from django import forms

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = [single_file_clean(data, initial)]
        return result

class FileFieldForm(forms.Form):
    file_field = MultipleFileField()

    def clean(self):
        files = self.files.getlist('file_field')
        for file in files:
            if not file.name.endswith('.jpeg') and not file.name.endswith('.jpg') and not file.name.endswith('.png'):
                raise forms.ValidationError(f"{file.name} не является .jpg или .png файлом.")
        return super().clean()