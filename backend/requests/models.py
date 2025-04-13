from django.db import models


class Request(models.Model):
    test_field = models.IntegerField()
    
    def __str__(self):
        return str(self.test_field)