import time

from django.contrib.sites.models import Site
from django.db import IntegrityError
from django.test import TestCase
from celery.contrib.testing.tasks import ping
from celery.utils import uuid
from celery import states

from ..models import ModelTaskMeta, ModelTaskMetaState
from .base import CeleryTestCase
from .testapp.models import JPEGFile
from .testapp.tasks import forced_failure, retry_forever, sleep_for_success


class SetUpMixin(object):
    def setUp(self):
        super().setUp()
        self.site_a = Site.objects.create(domain='www.a.com', name='a.com')
        self.site_b = Site.objects.create(domain='www.b.com', name='b.com')
        self.record = JPEGFile.objects.create(pk=self.site_a.pk)
        self.instances = (self.site_a, self.site_b, self.record)


class ModelTaskMetaTests(SetUpMixin, TestCase):
    def test_task_id_unique_per_relation(self):
        ModelTaskMeta.objects.create(content_object=self.site_a, task_id='foo')
        with self.assertRaises(IntegrityError):
            ModelTaskMeta.objects.create(content_object=self.site_a, task_id='foo')
    
    def test_task_id_not_unique_per_relation_type(self):
        ModelTaskMeta.objects.create(content_object=self.site_a, task_id='foo')
        ModelTaskMeta.objects.create(content_object=self.site_b, task_id='foo')
    
    def test_task_id_not_unique_per_relation_id(self):
        ModelTaskMeta.objects.create(content_object=self.site_a, task_id='foo')
        ModelTaskMeta.objects.create(content_object=self.record, task_id='foo')


class MultiModelStateUpdateTests(SetUpMixin, CeleryTestCase):
    def setUp(self):
        super().setUp()
        self.task_id = uuid()
        ModelTaskMeta.objects.create(content_object=self.site_a, task_id=self.task_id)
        ModelTaskMeta.objects.create(content_object=self.site_b, task_id=self.task_id)
        ModelTaskMeta.objects.create(content_object=self.record, task_id=self.task_id)
    
    def test_count(self):
        self.assertEqual(3, ModelTaskMeta.objects.filter(task_id=self.task_id).count())
    
    def test_pending(self):
        self.assertEqual(3, ModelTaskMeta.objects.filter(task_id=self.task_id, state=ModelTaskMetaState.PENDING).count())
    
    def test_forget(self):
        ModelTaskMeta.objects.filter(task_id=self.task_id).first().result.forget()
        self.assertEqual(0, ModelTaskMeta.objects.filter(task_id=self.task_id).count())
        
    def test_success(self):
        result = ping.apply_async(task_id=self.task_id)
        time.sleep(1)
        self.assertTrue(result.ready())
        self.assertTrue(result.successful())
        self.assertEqual(3, ModelTaskMeta.objects.filter(task_id=self.task_id, state=ModelTaskMetaState.SUCCESS).count())

    def test_failed(self):
        result = forced_failure.apply_async(task_id=self.task_id)
        time.sleep(1)
        self.assertTrue(result.ready())
        self.assertTrue(result.failed())
        self.assertEqual(3, ModelTaskMeta.objects.filter(task_id=self.task_id, state=ModelTaskMetaState.FAILURE).count())

    def test_retried(self):
        result = retry_forever.apply_async(task_id=self.task_id)
        time.sleep(1)
        self.assertEqual(result.state, states.RETRY)
        self.assertEqual(3, ModelTaskMeta.objects.filter(task_id=self.task_id, state=ModelTaskMetaState.RETRY).count())

    def test_started(self):
        result = sleep_for_success.apply_async(task_id=self.task_id)
        time.sleep(1)
        self.assertEqual(result.state, states.STARTED)
        self.assertEqual(3, ModelTaskMeta.objects.filter(task_id=self.task_id, state=ModelTaskMetaState.STARTED).count())
    
    def test_revoked(self):
        result = retry_forever.apply_async(task_id=self.task_id)
        time.sleep(1)
        result.revoke(terminate=True, wait=True, timeout=2)
        time.sleep(10)  #  avoid sqlite3.OperationalError: database table is locked
        self.assertEqual(0, ModelTaskMeta.objects.filter(task_id=self.task_id).count())
