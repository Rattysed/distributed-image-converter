from django.contrib import admin

from .models import Request, UploadedFile, EditedFile


admin.site.register(Request)
admin.site.register(UploadedFile)
admin.site.register(EditedFile)
