import boto3
from django.conf import settings

from abc import ABC, abstractmethod

class ImageTasking(ABC):
    @abstractmethod
    def edit(self, image_bytes):
        ...
