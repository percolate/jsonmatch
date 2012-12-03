jsonmatch
=========

`jsonmatch` is a small library for matching Python JSON dictionaries against a
specification in a flexible, informative way.

### But don't we already have JSON diff tools in Python?

Yes we do; this isn't a JSON diff tool. This is a tool that matches a 
possibly-general schema (including regexps, types, and functions as matcher 
values) against candidate JSON dicts.

## Example

```python
>>> import jsonmatch
>>> import re

>>> spec = {
  'a': 123,
  'b': {
    'c': re.compile('[abc][ABC]{3}'),  # we can use regexp
    'd': [1, 2, 3]},
  'e': lambda x: len(x) == 3,          # and callables
  'f': list,                           # and also types
}


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
})

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
})

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


