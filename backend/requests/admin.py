from django.contrib import admin

from .models import EditedFile, Request, UploadedFile


admin.site.register(Request)
admin.site.register(UploadedFile)
admin.site.register(EditedFile)