from django.db import models

class JPEGFile(models.Model):
    file = models.FileField()
    etag = models.CharField(max_length=255)
