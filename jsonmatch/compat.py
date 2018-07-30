from __future__ import absolute_import, unicode_literals

import sys

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

if PY2:
    PY2_STR = str
else:
    PY2_STR = None
