jsonmatch
=========

`jsonmatch` is a small library for matching Python JSON dictionaries against a
specification in a flexible, informative way. It was created to make testing
API responses easier.

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

### But don't we already have JSON diff tools in Python?

We sure do; this isn't a JSON diff tool. This is a tool that determines if a
candidate JSON dict fits into a possibly-generic schema (or if it breaks it,
and how). Matching values can include regexps, types, and functions as well as
regular JSON values. At writing, I haven't come across a tool that does this.

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


