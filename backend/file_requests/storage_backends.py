from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class UploadedStorage(S3Boto3Storage):
    location = 'uploaded'
    default_acl = 'public-read'
    file_overwrite = False


class EditedStorage(S3Boto3Storage):
    location = 'edited'
    default_acl = 'public-read'
    file_overwrite = False


class ResultStorage(S3Boto3Storage):
    location = 'result'
    default_acl = 'public-read'
    file_overwrite = False
