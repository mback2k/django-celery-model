[django-celery-model](https://github.com/mback2k/django-celery-model) is an
extension to [Celery](https://github.com/celery/celery) which adds support
for tracking Celery tasks assigned to Django model instances.

Installation
------------
Install the latest version from pypi.python.org:

    pip install django-celery-model

Install the development version by cloning the source from github.com:

    pip install git+https://github.com/mback2k/django-celery-model.git

Configuration
-------------
Add the package to your `INSTALLED_APPS`:

    INSTALLED_APPS += (
        'djcelery_model',
    )

Make sure that you are receiving Celery events via:

    CELERY_TASK_TRACK_STARTED = True
    CELERY_TASK_SEND_SENT_EVENT = True
    CELERY_SEND_EVENTS = True

Example
-------
Add the TaskMixin to your Django model:

    from django.db import models
    from django.utils.translation import ugettext_lazy as _
    from djcelery_model.models import TaskMixin

    class MyModel(TaskMixin, models.Model):
        name = models.CharField(_('Name'), max_length=100)

Queue an asynchronous task from your Django model instance:

    from .models import MyModel
    from .tasks import mytask

    mymodel = MyModel.objects.get(name='test instance')
    mymodel.apply_async(mytask, ...)

Retrieve list of asynchronous tasks assigned to your Django model instance:

    mymodel.tasks.all()
    mymodel.tasks.pending()
    mymodel.tasks.started()
    mymodel.tasks.retrying()
    mymodel.tasks.failed()
    mymodel.tasks.successful()
    mymodel.tasks.running()
    mymodel.tasks.ready()

Check for a running or ready asynchronous task for your Django model instance:

    mymodel.has_running_task
    mymodel.has_ready_task

Handle asynchronous task results for your Django model instance:

    mymodel.get_task_results()
    mymodel.get_task_result(task_id)
    mymodel.clear_task_results()
    mymodel.clear_task_result(task_id)

Filter your Django model based upon asynchronous tasks:

    MyModel.objects.with_tasks()
    MyModel.objects.with_pending_tasks()
    MyModel.objects.with_started_tasks()
    MyModel.objects.with_retrying_tasks()
    MyModel.objects.with_failed_tasks()
    MyModel.objects.with_successful_tasks()
    MyModel.objects.with_running_tasks()
    MyModel.objects.with_ready_tasks()

    MyModel.objects.without_tasks()
    MyModel.objects.without_pending_tasks()
    MyModel.objects.without_started_tasks()
    MyModel.objects.without_retrying_tasks()
    MyModel.objects.without_failed_tasks()
    MyModel.objects.without_successful_tasks()
    MyModel.objects.without_running_tasks()
    MyModel.objects.without_ready_tasks()

License
-------
* Released under MIT License
* Copyright (c) 2014-2019 Marc Hoersken <info@marc-hoersken.de>
