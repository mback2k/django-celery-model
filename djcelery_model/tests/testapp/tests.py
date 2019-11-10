from celery.contrib.testing.tasks import ping
from celery.contrib.testing.worker import start_worker
from django.test import TestCase, TransactionTestCase

from djcelery_model.models import ModelTaskMeta, TaskMixin
from djcelery_model.tests import celery_app

from .models import JPEGFile


class CeleryTestCase(TransactionTestCase):
    def setUp(self):
        self.celery_worker = start_worker(celery_app)
        self.celery_worker.__enter__()
    
    def tearDown(self):
        self.celery_worker.__exit__(None, None, None)


class TestAppIntegrationTests(TestCase):
    def test_model_is_taskmixin(self):
        self.assertIsInstance(JPEGFile(), TaskMixin)
    

class TestAppCeleryTests(CeleryTestCase):
    def test_worker(self):
        result = ping.delay()
        pong = result.get(timeout=10)
        self.assertEqual(pong, 'pong')
