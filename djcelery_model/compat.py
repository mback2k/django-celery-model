try:
    from six import python_2_unicode_compatible
except ImportError:
    from django.utils.encoding import python_2_unicode_compatible
