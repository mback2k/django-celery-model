# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from celery.result import BaseAsyncResult
from celery.utils import uuid

class ModelTaskMeta(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey()
    task_id = models.CharField(max_length=255, unique=True)

    def __unicode__(self):
        return self.task_id

class ModelAsyncResult(BaseAsyncResult):
    def forget(self):
        ModelTaskMeta.objects.filter(task_id=self.id).delete()
        return super(ModelAsyncResult, self).forget()

class TaskMixin(object):
    class Meta:
        abstract = True

    @property
    def tasks(self):
        content_type = ContentType.objects.get_for_model(self)
        queryset = ModelTaskMeta.objects.filter(content_type=content_type)
        return queryset.filter(object_id=self.pk)

    def apply_async(self, task, *args, **kwargs):
        if 'task_id' in kwargs:
            task_id = kwargs['task_id']
        else:
            task_id = kwargs['task_id'] = uuid()
        try:
            taskmeta = ModelTaskMeta.objects.get(task_id=task_id)
            taskmeta.content_object = self
            forget_if_ready(BaseAsyncResult(task_id))
        except ModelTaskMeta.DoesNotExist:
            taskmeta = ModelTaskMeta(task_id=task_id, content_object=self)
        taskmeta.save()
        return task.apply_async(*args, **kwargs)

    def get_task_results(self):
        return map(lambda task_id: ModelAsyncResult(task_id),
                   self.tasks.values_list('task_id', flat=True))

    def get_task_result(self, task_id):
        if self.tasks.filter(task_id=task_id).exists():
            return ModelAsyncResult(task_id)
        return BaseAsyncResult(task_id)

    def clear_task_results(self):
        map(forget_if_ready, self.get_task_results())

    def clear_task_result(self, task_id):
        forget_if_ready(self.get_task_result(task_id))

    @property
    def has_running_task(self):
        return len(filter(lambda x: not x.ready(), self.get_task_results())) > 0

def forget_if_ready(async_result):
    if async_result and async_result.ready():
        async_result.forget()
