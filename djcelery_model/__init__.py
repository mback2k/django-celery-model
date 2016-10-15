"""
django-celery-model is an extension to Celery and django-celery which adds
support for tracking Celery tasks assigned to Django model instances.
"""

__version_info__ = {
    'major': 0,
    'minor': 1,
    'micro': 2,
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
