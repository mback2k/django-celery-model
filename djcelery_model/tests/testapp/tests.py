import datetime
from contextlib import contextmanager
from time import sleep
from unittest import mock

from django.contrib.staticfiles import finders
from django.core.files import File
from django.test import TestCase
from django.utils import timezone

from djcelery_model.models import ModelTaskMeta, TaskMixin, perform_update
from djcelery_model.signals import post_bulk_update

from ..base import CeleryTestCase
from .models import JPEGFile
from .tasks import calculate_etag


@contextmanager
def catch_signal(signal):
    """Catch django signal and return the mocked call."""
    handler = mock.Mock()
    signal.connect(handler)
    yield handler
    signal.disconnect(handler)


class SignalTests(TestCase):
    @mock.patch('django.utils.timezone.now')
    def test_post_bulk_update(self, mocked_now):
        updated_at = datetime.datetime(2020, 7, 5, tzinfo=timezone.utc)
        mocked_now.return_value = updated_at
        with catch_signal(post_bulk_update) as handler:
            perform_update('a-task-id', state=1)
        handler.assert_called_once_with(
            sender=ModelTaskMeta,
            task_id='a-task-id',
            count=0,
            update_kwargs=dict(
                state=1,
                updated=updated_at,
            ),
            signal=post_bulk_update,
        )


class TestAppIntegrationTests(TestCase):
    def test_model_is_taskmixin(self):
        self.assertIsInstance(JPEGFile(), TaskMixin)
    

class TestAppCeleryTests(CeleryTestCase):
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
        
        # not the greatest way to wait for async stuff to happen, but we need
        # the signals to complete before testing for side effects
        sleep(3)
        
        self.assertEqual(jpeg.etag, '')
        self.assertFalse(jpeg.has_running_task)
        self.assertTrue(jpeg.has_ready_task)
        
        jpeg.refresh_from_db()
        
        self.assertEqual(jpeg.etag, '80b098e6cd95b9901fa29799d48731433dfaeab0')
        self.assertFalse(jpeg.has_running_task)
        self.assertTrue(jpeg.has_ready_task)

    def test_signals_set_updated(self):
        started_at = timezone.now()
        sleep(1)
        jpeg = JPEGFile.objects.create(
            file=File(open(finders.find('testapp/flower.jpg'), 'rb'), name='flower.jpg')
        )
        result = jpeg.apply_async(calculate_etag, [jpeg.pk])
        jpeg.refresh_from_db()
        taskmeta = jpeg.tasks.filter(task_id=result.id).first()
        self.assertTrue(taskmeta)
        
        updated_at = taskmeta.updated
        self.assertIsInstance(updated_at, datetime.datetime)
        self.assertGreater(updated_at, started_at)
        
        result.get(timeout=10)
        self.assertTrue(result.ready())
        
        # not the greatest way to wait for async stuff to happen, but we need
        # the signals to complete before testing for side effects
        sleep(3)
        taskmeta.refresh_from_db()
        self.assertLess(updated_at, taskmeta.updated)
        self.assertLess(taskmeta.updated, timezone.now())
