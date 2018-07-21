jsonmatch
=========

`jsonmatch` is a small library for matching Python JSON dictionaries against a
specification in a flexible, informative way. It was created to make testing
API responses simple, quick, and easy.

```python
>>> import jsonmatch, re

>>> m = jsonmatch.compile({'a': int, 'b': re.compile(r'\d+'), 'c': 'c'})

>>> m.matches({'a': 1, 'b': '321', 'c': 'c'})
True

>>> m.matches({'a': 1, 'b': 'not a digit', 'c': 'c'})
False

>>> m.assert_matches({'a': 1, 'b': 'not a digit', 'c': 'c'})
Expected:
{'a': <type 'int'>, 'b': <_sre.SRE_Pattern object at 0x7f70340d5160>, 'c': 'c'}

Got:
{'a': 1, 'b': 'not a digit', 'c': 'c'}

Diffs:
{('b',): (RegexpMatch(r'\d+'), 'not a digit')}

---------------------------------------------------------------------------
AssertionError                            Traceback (most recent call last)
...

>>> m.breaks({'a': 1, 'b': 'not a digit', 'c': 'c'}).paths_to_breaks
{('b',): (RegexpMatch(r'\d+'), 'not a digit')}
```

## Installing

jsonmatch is on [pypi](https://pypi.python.org/pypi/jsonmatch)

```
pip install jsonmatch
```


## Features

- Flexible matching based on
    - type
    - regexp
    - callable
    - or plain ol' object.
- Return unmet expectations in a useful datastructure, not just
  a string.
    - `{('path', 'to', 'diff'): (expected_val, actual_val), ...}`
- Optionally ignore ordering in lists.


## Related projects

There are some other great solutions out there for doing data validation in
Python, including

- [onctuous](https://pypi.python.org/pypi/onctuous)
- [voluptuous](https://github.com/alecthomas/voluptuous)
- [colander](http://docs.pylonsproject.org/projects/colander/en/latest/basics.html#defining-a-colander-schema)

These libraries are much more robust than jsonmatch, but they're also
significantly more complex.


## Example

```python
>>> import jsonmatch
>>> import re

>>> matcher = jsonmatch.compile({
  'a': 123,
  'b': {
    'c': re.compile('[abc][ABC]{3}'),  # we can use regexp
    'd': [1, 2, 3]},
  'e': lambda x: len(x) == 3,          # and callables
  'f': list,                           # and also types
})

# candidates that match the specification yield no breaks
>>> None == matcher.breaks({
  'a': 123,
  'b': {
    'c': 'aABC',
    'd': [1, 2, 3],
  },
  'e': 'one',
  'f': [],
})

True


# on the other hand, mismatches yield Breaks objects (scalar breakage in 'a')
>>> print matcher.breaks({
  'a': 1234,
  'b': {
    'c': 'aABC',
    'd': [1, 2, 3],
  },
  'e': 'one',
  'f': [],
}).breaks_str

"""
Expected:
{'a': 123,
 'b': {'c': <_sre.SRE_Pattern object at 0x2c8ed78>, 'd': [1, 2, 3]},
 'e': <function <lambda> at 0x2e8c1b8>,
 'f': []}

Got:
{'a': 1234, 'b': {'c': 'aABCeee', 'd': [1, 2, 3]}, 'e': 'one', 'f': []}

Diffs:
{('a',): (123, 1234)}
"""


# regexp breakage in 'b.c'
>>> print matcher.breaks({
  'a': 123,
  'b': {
    'c': "doesn't match",
    'd': [1, 2, 3],
  },
  'e': 'one',
  'f': [],
}).breaks_str

"""
Expected:
{'a': 123,
 'b': {'c': <_sre.SRE_Pattern object at 0x2c8ed78>, 'd': [1, 2, 3]},
 'e': <function <lambda> at 0x2e8c1b8>,
 'f': []}

Got:
{'a': 123, 'b': {'c': "doesn't match", 'd': [1, 2, 3]}, 'e': 'one', 'f': []}

Diffs:
{('b', 'c'): (RegexpMatch('[abc][ABC]{3}'), "doesn't match")}
"""
```


## Python 2/3 compatibility

```python
from __future__ import print_function, unicode_literals

>>> import jsonmatch
>>> msg = '\U0001f600'
>>> print(msg)
😀

# In PY2, the `str` type will match both unicode and byte string

>>> matcher = jsonmatch.compile({'message': str})
>>> print(matcher.matches({'message': b'bytestring'}))
True
>>> print(matcher.matches({'message': msg}))
True


# In PY3, `str` will ONLY match unicode string

>>> matcher = jsonmatch.compile({'message': str})
>>> print(matcher.matches({'message': b'bytestring'}))
False
>>> print(matcher.matches({'message': msg}))
True

# In order to match byte string, we must compile as `bytes`

>>> matcher = jsonmatch.compile({'message': bytes})
>>> print(matcher.matches({'message': b'bytestring'}))
True
>>> print(matcher.matches({'message': msg}))
False
```
