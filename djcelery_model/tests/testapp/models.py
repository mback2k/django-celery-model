from django.db import models
from djcelery_model.models import TaskMixin

class JPEGFile(TaskMixin, models.Model):
    file = models.FileField()
    etag = models.CharField(max_length=255)
