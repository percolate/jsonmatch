"""
jsonmatch
---------

A small utility for testing flexible schemas against JSON dicts in Python.
"""

from .matcher import ( # noqa
    compile,
    TypeMatch,
    RegexpMatch,
    MissingKey
)
