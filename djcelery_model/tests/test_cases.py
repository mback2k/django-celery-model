from celery.contrib.testing.worker import start_worker
from django.test import TransactionTestCase

from djcelery_model.tests import celery_app


class CeleryTestCase(TransactionTestCase):
    def setUp(self):
        self.celery_worker = start_worker(celery_app)
        self.celery_worker.__enter__()
    
    def tearDown(self):
        self.celery_worker.__exit__(None, None, None)
