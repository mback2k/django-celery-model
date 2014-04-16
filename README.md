[Django-Celery-Model](https://github.com/mback2k/django-celery-model) is an
extension to [Django-Celery](https://github.com/celery/django-celery)
which adds supports for tracking tasks aligned to Django model instances.

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

License
-------
* Released under MIT License
* Copyright (c) 2014 Marc Hoersken <info@marc-hoersken.de>
