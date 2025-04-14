import boto3
from botocore.exceptions import ClientError
from django.apps import AppConfig
from django.conf import settings


def create_bucket(bucket_name):
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
        )
        s3_client.create_bucket(Bucket=bucket_name)
        print(f"Bucket '{bucket_name}' создан.")
    except ClientError as e:
        if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
            print(f"Bucket '{bucket_name}' уже существует.")
        else:
            print(f"Ошибка при создании бакета: {e}")
            raise


class RequestsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'requests'

    def ready(self):
        create_bucket(settings.AWS_STORAGE_BUCKET_NAME)
