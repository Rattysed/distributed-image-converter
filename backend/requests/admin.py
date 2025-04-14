from django.contrib import admin

from .models import Request, File


admin.site.register(Request)
admin.site.register(File)