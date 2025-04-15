from rest_framework import serializers
from .models import Request, UploadedFile

class RequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = ['id', 'status', 'time_end', 'url']
        read_only_fields = ['id', 'status', 'time_end', 'url']

class UploadedFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedFile
        fields = ['id', 'request', 'status', 'uploaded_name']
        read_only_fields = ['id', 'request', 'status'] 