from __future__ import absolute_import, unicode_literals
from hashlib import sha1
from time import sleep
from celery import shared_task

from .models import JPEGFile


@shared_task
def calculate_etag(pk):
    jpeg = JPEGFile.objects.get(pk=pk)
    jpeg.etag = sha1(jpeg.file.read()).hexdigest()
    sleep(5)
    jpeg.save()
