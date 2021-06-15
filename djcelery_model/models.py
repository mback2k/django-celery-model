#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.db import models
from django.db.models import Q
from django.db.models.query import QuerySet
from django.contrib.contenttypes.models import ContentType

try:
    from six import python_2_unicode_compatible
except ImportError:
    from django.utils.encoding import python_2_unicode_compatible

try:
    # Django >= 1.7
    from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
except ImportError:
    from django.contrib.contenttypes.generic import GenericForeignKey, GenericRelation

from celery.result import AsyncResult
from celery.utils import uuid
from celery import signals

class ModelTaskMetaState(object):
    PENDING =   0
    STARTED =   1
    RETRY   =   2
    FAILURE =   3
    SUCCESS =   4
    REJECTED =  5

    @classmethod
    def lookup(cls, state):
        return getattr(cls, state)

class ModelTaskMetaFilterMixin(object):
    def pending(self):
        return self.filter(state=ModelTaskMetaState.PENDING)

    def started(self):
        return self.filter(state=ModelTaskMetaState.STARTED)

    def retrying(self):
        return self.filter(state=ModelTaskMetaState.RETRY)

    def failed(self):
        return self.filter(state=ModelTaskMetaState.FAILURE)

    def successful(self):
        return self.filter(state=ModelTaskMetaState.SUCCESS)

    def rejected(self):
        return self.filter(state=ModelTaskMetaState.REJECTED)

    def running(self):
        return self.filter(Q(state=ModelTaskMetaState.PENDING)|
                           Q(state=ModelTaskMetaState.STARTED)|
                           Q(state=ModelTaskMetaState.RETRY))

    def ready(self):
        return self.filter(Q(state=ModelTaskMetaState.FAILURE)|
                           Q(state=ModelTaskMetaState.REJECTED)|
                           Q(state=ModelTaskMetaState.SUCCESS))

class ModelTaskMetaQuerySet(ModelTaskMetaFilterMixin, QuerySet):
    pass

class ModelTaskMetaManager(ModelTaskMetaFilterMixin, models.Manager):
    use_for_related_fields = True

    def get_queryset(self):
        return ModelTaskMetaQuerySet(self.model, using=self._db)

@python_2_unicode_compatible
class ModelTaskMeta(models.Model):
    STATES = (
        (ModelTaskMetaState.PENDING, 'PENDING'),
        (ModelTaskMetaState.STARTED, 'STARTED'),
        (ModelTaskMetaState.RETRY,   'RETRY'),
        (ModelTaskMetaState.FAILURE, 'FAILURE'),
        (ModelTaskMetaState.SUCCESS, 'SUCCESS'),
        (ModelTaskMetaState.REJECTED, 'REJECTED'),
    )

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()
    task_id = models.CharField(max_length=255, unique=True)
    state = models.PositiveIntegerField(choices=STATES,
                                        default=ModelTaskMetaState.PENDING)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    updated = models.DateTimeField(auto_now=True)

    objects = ModelTaskMetaManager()

    def __str__(self):
        return '%s: %s' % (self.task_id, dict(self.STATES)[self.state])

    @property
    def result(self):
        return ModelAsyncResult(self.task_id)


class ModelAsyncResult(AsyncResult):
    def forget(self):
        ModelTaskMeta.objects.filter(task_id=self.id).delete()
        return super(ModelAsyncResult, self).forget()


class TaskFilterMixin(object):
    def with_tasks(self):
        return self.filter(tasks__state__isnull=False)

    def with_pending_tasks(self):
        return self.filter(tasks__state=ModelTaskMetaState.PENDING)

    def with_started_tasks(self):
        return self.filter(tasks__state=ModelTaskMetaState.STARTED)

    def with_retrying_tasks(self):
        return self.filter(tasks__state=ModelTaskMetaState.RETRY)

    def with_failed_tasks(self):
        return self.filter(tasks__state=ModelTaskMetaState.FAILURE)

    def with_successful_tasks(self):
        return self.filter(tasks__state=ModelTaskMetaState.SUCCESS)

    def with_rejected_tasks(self):
        return self.filter(tasks__state=ModelTaskMetaState.REJECTED)

    def with_running_tasks(self):
        return self.filter(Q(tasks__state=ModelTaskMetaState.PENDING)|
                           Q(tasks__state=ModelTaskMetaState.STARTED)|
                           Q(tasks__state=ModelTaskMetaState.RETRY))

    def with_ready_tasks(self):
        return self.filter(Q(tasks__state=ModelTaskMetaState.FAILURE)|
                           Q(tasks__state=ModelTaskMetaState.REJECTED)|
                           Q(tasks__state=ModelTaskMetaState.SUCCESS))

    def without_tasks(self):
        return self.exclude(tasks__state__isnull=False)

    def without_pending_tasks(self):
        return self.exclude(tasks__state=ModelTaskMetaState.PENDING)

    def without_started_tasks(self):
        return self.exclude(tasks__state=ModelTaskMetaState.STARTED)

    def without_retrying_tasks(self):
        return self.exclude(tasks__state=ModelTaskMetaState.RETRY)

    def without_failed_tasks(self):
        return self.exclude(tasks__state=ModelTaskMetaState.FAILURE)

    def without_successful_tasks(self):
        return self.exclude(tasks__state=ModelTaskMetaState.SUCCESS)

    def without_rejected_tasks(self):
        return self.exclude(tasks__state=ModelTaskMetaState.REJECTED)

    def without_running_tasks(self):
        return self.exclude(Q(tasks__state=ModelTaskMetaState.PENDING)|
                            Q(tasks__state=ModelTaskMetaState.STARTED)|
                            Q(tasks__state=ModelTaskMetaState.RETRY))

    def without_ready_tasks(self):
        return self.exclude(Q(tasks__state=ModelTaskMetaState.FAILURE)|
                            Q(tasks__state=ModelTaskMetaState.REJECTED)|
                            Q(tasks__state=ModelTaskMetaState.SUCCESS))

class TaskQuerySet(TaskFilterMixin, QuerySet):
    pass

class TaskManager(TaskFilterMixin, models.Manager):
    use_for_related_fields = True

    def get_queryset(self):
        return TaskQuerySet(self.model, using=self._db)

class TaskMixin(models.Model):
    tasks = GenericRelation(ModelTaskMeta)

    objects = TaskManager()

    class Meta:
        abstract = True

    @property
    def has_running_task(self):
        return self.tasks.running().exists()

    @property
    def has_ready_task(self):
        return self.tasks.ready().exists()

    def apply_async(self, task, *args, **kwargs):
        if 'task_id' in kwargs:
            task_id = kwargs['task_id']
        else:
            task_id = kwargs['task_id'] = uuid()
        forget_if_ready(AsyncResult(task_id))
        try:
            taskmeta = ModelTaskMeta.objects.get(task_id=task_id)
            taskmeta.content_object = self
        except ModelTaskMeta.DoesNotExist:
            taskmeta = ModelTaskMeta(task_id=task_id, content_object=self)
        taskmeta.save()
        return task.apply_async(*args, **kwargs)

    def get_task_results(self):
        return map(lambda x: x.result, self.tasks.all())

    def get_task_result(self, task_id):
        return self.tasks.get(task_id=task_id).result

    def clear_task_results(self):
        for task_result in self.get_task_results():
            forget_if_ready(task_result)

    def clear_task_result(self, task_id):
        task_result = self.get_task_result(task_id)
        forget_if_ready(task_result)


def forget_if_ready(async_result):
    if async_result and async_result.ready():
        async_result.forget()


@signals.after_task_publish.connect
def handle_after_task_publish(sender=None, body=None, **kwargs):
    if body and 'id' in body:
        queryset = ModelTaskMeta.objects.filter(task_id=body['id'])
        queryset.update(state=ModelTaskMetaState.PENDING)

@signals.task_prerun.connect
def handle_task_prerun(sender=None, task_id=None, **kwargs):
    if task_id:
        queryset = ModelTaskMeta.objects.filter(task_id=task_id)
        queryset.update(state=ModelTaskMetaState.STARTED)

@signals.task_postrun.connect
def handle_task_postrun(sender=None, task_id=None, state=None, **kwargs):
    if task_id and state:
        queryset = ModelTaskMeta.objects.filter(task_id=task_id)
        queryset.update(state=ModelTaskMetaState.lookup(state))

@signals.task_failure.connect
def handle_task_failure(sender=None, task_id=None, **kwargs):
    if task_id:
        queryset = ModelTaskMeta.objects.filter(task_id=task_id)
        queryset.update(state=ModelTaskMetaState.FAILURE)

@signals.task_revoked.connect
def handle_task_revoked(sender=None, request=None, **kwargs):
    if request and request.id:
        queryset = ModelTaskMeta.objects.filter(task_id=request.id)
        queryset.delete()
