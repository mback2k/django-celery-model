[django-celery-model](https://github.com/mback2k/django-celery-model) is an
extension to [Celery](https://github.com/celery/celery) and
[django-celery](https://github.com/celery/django-celery)
which adds support for tracking Celery tasks assigned to Django model instances.

Installation
------------
You can install the latest version from GitHub manually:

    git clone https://github.com/mback2k/django-celery-model.git
    cd django-celery-model
    python setup.py install

or via pip:

    pip install https://github.com/mback2k/django-celery-model/zipball/master

Configuration
-------------
Add the package to your `INSTALLED_APPS`:

    INSTALLED_APPS += (
        'djcelery',
        'djcelery_model',
    )

Example
-------
Add the TaskMixin to your Django model:

    from django.db import models
    from django.utils.translation import ugettext_lazy as _
    from djcelery_model.models import TaskMixin

    class MyModel(models.Model, TaskMixin):
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
    mymodel.tasks.ready()

Check if there is a running asynchronous task for your Django model instance:

    mymodel.has_running_task

Handle asynchronous task results for your Django model instance:

    mymodel.get_task_results()
    mymodel.get_task_result(task_id)
    mymodel.clear_task_results()
    mymodel.clear_task_result(task_id)

License
-------
* Released under MIT License
* Copyright (c) 2014 Marc Hoersken <info@marc-hoersken.de>
