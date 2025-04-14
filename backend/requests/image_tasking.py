import boto3
from django.conf import settings

from abc import ABC, abstractmethod

class ImageTasking(ABC):
    @abstractmethod
    def edit(self, image_bytes):
        ...
    
    
    # def __init__(self, bucket_name=None):
    #     self.s3_client = boto3.client(
    #         's3',
    #         aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    #         aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    #         endpoint_url=settings.AWS_S3_ENDPOINT_URL,
    #     )
    #     self.bucket_name = bucket_name or settings.AWS_STORAGE_BUCKET_NAME

    # def upload_to_s3(self, file_name, file_content):
    #     self.s3_client.put_object(
    #         Bucket=self.bucket_name,
    #         Key=settings.PUBLIC_EDITED_LOCATION + '/' + file_name,
    #         Body=file_content,
    #         ContentType="image/jpg",
    #     )

    # def download_from_s3(self, file_name):
    #     try:
    #         response = self.s3_client.get_object(
    #             Bucket=self.bucket_name,
    #             Key=settings.PUBLIC_MEDIA_LOCATION + '/' + file_name + '.jpg'
    #         )
    #         return response['Body'].read()
    #     except Exception as e:
    #         print(f"Ошибка загрузки файла: {e}")
    #     return None
