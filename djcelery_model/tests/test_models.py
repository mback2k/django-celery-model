import time

from django.contrib.sites.models import Site
from django.db import IntegrityError
from django.test import TestCase
from celery.contrib.testing.tasks import ping

from ..models import ModelTaskMeta, ModelTaskMetaState
from .base import CeleryTestCase
from .testapp.models import JPEGFile


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
    def test_ping_across_models(self):
        task_id = 'c51352f0-cf93-4781-9288-ae5e4a362648'
        ModelTaskMeta.objects.create(content_object=self.site_a, task_id=task_id)
        ModelTaskMeta.objects.create(content_object=self.site_b, task_id=task_id)
        ModelTaskMeta.objects.create(content_object=self.record, task_id=task_id)
        self.assertEqual(3, ModelTaskMeta.objects.filter(task_id=task_id).count())
        self.assertEqual(3, ModelTaskMeta.objects.filter(task_id=task_id, state=ModelTaskMetaState.PENDING).count())
        result = ping.apply_async(task_id=task_id)
        time.sleep(1)
        self.assertTrue(result.ready())
        self.assertTrue(result.successful())
        self.assertEqual(3, ModelTaskMeta.objects.filter(task_id=task_id, state=ModelTaskMetaState.SUCCESS).count())
        ModelTaskMeta.objects.filter(task_id=task_id).first().result.forget()
        self.assertEqual(0, ModelTaskMeta.objects.filter(task_id=task_id).count())
