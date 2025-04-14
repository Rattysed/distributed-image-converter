from django.contrib import admin

from .models import Request, EditedFile, UploadedFile


admin.site.register(Request)
admin.site.register(UploadedFile)
admin.site.register(EditedFile)
