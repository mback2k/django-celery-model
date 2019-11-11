from celery.contrib.testing.tasks import ping
from celery.contrib.testing.worker import start_worker
from django.contrib.staticfiles import finders
from django.core.files import File
from django.test import TestCase, TransactionTestCase

from djcelery_model.models import TaskMixin
from djcelery_model.tests import celery_app

from .models import JPEGFile
from .tasks import calculate_etag


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
    
    def test_state_properties(self):
        jpeg = JPEGFile.objects.create(
            file=File(open(finders.find('testapp/flower.jpg'), 'rb'), name='flower.jpg')
        )
        
        self.assertFalse(jpeg.has_running_task)
        self.assertFalse(jpeg.has_ready_task)
        
        result = jpeg.apply_async(calculate_etag, [jpeg.pk])
        self.assertTrue(jpeg.has_running_task)
        self.assertFalse(jpeg.has_ready_task)
        self.assertFalse(result.ready())
        
        result.get(timeout=10)
        self.assertTrue(result.ready())
        
        self.assertEqual(jpeg.etag, '')
        self.assertFalse(jpeg.has_running_task)
        self.assertTrue(jpeg.has_ready_task)
        
        jpeg.refresh_from_db()
        
        self.assertEqual(jpeg.etag, '80b098e6cd95b9901fa29799d48731433dfaeab0')
        self.assertFalse(jpeg.has_running_task)
        self.assertTrue(jpeg.has_ready_task)
