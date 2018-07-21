from __future__ import absolute_import, unicode_literals

import six

PY3 = six.PY3


# Copied from python-future (which it comes from django.utils.encoding).
# https://github.com/PythonCharmers/python-future/blob/d78983763f6de1c375ee9356ea6e21db723314d5/src/future/utils/__init__.py#L65
def python_2_unicode_compatible(cls):
    """
    A decorator that defines __unicode__ and __str__ methods under Python
    2. Under Python 3, this decorator is a no-op.

    To support Python 2 and 3 with a single code base, define a __str__
    method returning unicode text and apply this decorator to the class, like
    this::

    >>> from future.utils import python_2_unicode_compatible

    >>> @python_2_unicode_compatible
    ... class MyClass(object):
    ...     def __str__(self):
    ...         return u'Unicode string: \u5b54\u5b50'

    >>> a = MyClass()

    Then, after this import:

    >>> from future.builtins import str

    the following is ``True`` on both Python 3 and 2::

    >>> str(a) == a.encode('utf-8').decode('utf-8')
    True

    and, on a Unicode-enabled terminal with the right fonts, these both print
    the Chinese characters for Confucius::

    >>> print(a)
    >>> print(str(a))

    The implementation comes from django.utils.encoding.
    """
    if not PY3:
        cls.__unicode__ = cls.__str__
        cls.__str__ = lambda self: self.__unicode__().encode('utf-8')
    return cls
