from celery.contrib.testing.tasks import ping

from .base import CeleryTestCase


class TestCeleryTestCase(CeleryTestCase):
    def test_worker(self):
        result = ping.delay()
        pong = result.get(timeout=10)
        self.assertEqual(pong, 'pong')
