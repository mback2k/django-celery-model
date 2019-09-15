#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
django-celery-model is an extension to Celery which adds support
for tracking Celery tasks assigned to Django model instances.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

__version_info__ = {
    'major': 0,
    'minor': 2,
    'micro': 1,
    'releaselevel': 'final',
}

def get_version():
    """
    Return the formatted version information
    """
    vers = ["%(major)i.%(minor)i" % __version_info__, ]

    if __version_info__['micro']:
        vers.append(".%(micro)i" % __version_info__)
    if __version_info__['releaselevel'] != 'final':
        vers.append('%(releaselevel)s' % __version_info__)
    return ''.join(vers)

__version__ = get_version()
