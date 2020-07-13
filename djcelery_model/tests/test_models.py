from django.contrib.sites.models import Site
from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError
from django.test import TestCase

from ..models import ModelTaskMeta


class ModelTaskMetaTests(TestCase):
    def setUp(self):
        self.site_a = Site.objects.create(domain='www.a.com', name='a.com')
        self.site_b = Site.objects.create(domain='www.b.com', name='b.com')
    
    def test_task_id_unique_per_relation(self):
        ModelTaskMeta.objects.create(content_object=self.site_a, task_id='foo')
        with self.assertRaises(IntegrityError):
            ModelTaskMeta.objects.create(content_object=self.site_a, task_id='foo')
    
    def test_task_id_not_unique_per_relation_type(self):
        ModelTaskMeta.objects.create(content_object=self.site_a, task_id='foo')
        ModelTaskMeta.objects.create(content_object=self.site_b, task_id='foo')
    
    def test_task_id_not_unique_per_relation_id(self):
        ModelTaskMeta.objects.create(content_object=self.site_a, task_id='foo')
        record = ContentType.objects.get(pk=self.site_a.pk)
        ModelTaskMeta.objects.create(content_object=record, task_id='foo')
