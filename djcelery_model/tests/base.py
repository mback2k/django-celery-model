from django.test import TransactionTestCase
from celery.contrib.testing.worker import start_worker

from djcelery_model.tests import celery_app


class CeleryTestCase(TransactionTestCase):
    def setUp(self):
        super().setUp()
        self.worker_context = start_worker(celery_app, perform_ping_check=False)
        self.worker = self.worker_context.__enter__()
        self.worker.ensure_started()
    
    def tearDown(self):
        self.worker_context.__exit__(None, None, None)