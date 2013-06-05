import pprint

import logging
log = logging.getLogger(__name__)


__all__ = ('compile',
           'TypeMatch',
           'RegexpMatch',
           'MissingKey')


def compile(spec):
    """
    Args:
        spec (dict): A specification dict that attempts to "break" test dicts

    Returns:
        JsonMatcher.
    """
    return JsonMatcher(spec)


class JsonMatcher(object):
    """Matches candidate dictionaries against a spec. Track any mismatches,
    'breaks'."""

    def __init__(self, spec):
        """
        Args:

            spec (dict|list): the dictionary or list that we're comparing to.
                Any value, nested or otherwise, can be a type in order to match
                a range of values.
        """
        self.spec = spec

    def matches(self, test_d, **kwargs):
        """
        Return True if `test_d` matches the specification dict.

        Kwargs:
            forwarded to JsonMatcher.breaks.
        """
        return (not self.breaks(test_d, **kwargs))

    def assert_matches(self, test_d, assertion_msg=None, **kwargs):
        """
        Assert that a test dict matches the schema. If not, print the breaks
        and throw an AssertionError.

        Kwargs:
            assertion_msg (str): Message to display if the assertion fails.
            other kwargs are forwarded to JsonMatcher.breaks.
        """
        bs = self.breaks(test_d, **kwargs)
        msg = assertion_msg or "Candidate dict doesn't match schema."

        if bs:
            print bs.breaks_str
            raise AssertionError(msg)

    def breaks(self, test_d, is_ordered=True):
        """
        Return None if `test_d` is an acceptable match to `self.spec`,
        Breaks object otherwise.

        Args:
            test_d (dict|list): the dictionary or list that may not be
                acceptable

        Kwargs:
            is_ordered (bool): should we care about the order of a
                list?

        Returns:
            Breaks or None.
        """
        breaks = Breaks(self.spec, test_d)

        exp_d = self.spec

        if isinstance(self.spec, (list, tuple)):
            exp_d = self._seq_to_dict(exp_d, is_ordered)

        if isinstance(test_d, (list, tuple)):
            test_d = self._seq_to_dict(test_d, is_ordered)

        bs = self._find_breaks(exp_d, test_d, tuple(), is_ordered, breaks)

        return bs if bs else None

    def _find_breaks(self, exp_d, test_d, key_trail, is_ordered, breaks):
        """
        Internal (mis)matching function. Fill out our Breaks object and return
        it.

        Args:
            exp_d (dict)
            test_d (dict): the dictionary that may not be acceptable
            key_trail (list): an accumulation of keys as we descend into the
                comparison
            is_ordered (bool): should we care about the order of a
                list?
            breaks (Breaks): for tracking mismatches

        Returns:
            Breaks.
        """
        if not isinstance(test_d, dict):
            log.info("`test_d` isn't a dict! Can't compare.")
            breaks.add_break('', TypeMatch(dict), type(test_d))

            return breaks

        exp_key_set = set(exp_d.keys())
        test_key_set = set(test_d.keys())

        only_in_exp = (exp_key_set - test_key_set)
        only_in_test = (test_key_set - exp_key_set)

        for key in only_in_exp:
            this_key_trail = key_trail + (key,)

            breaks.add_break(this_key_trail,
                             exp_d.get(key),
                             MissingKey())

        for key in only_in_test:
            this_key_trail = key_trail + (key,)

            breaks.add_break(this_key_trail,
                             MissingKey(),
                             test_d.get(key))

        if only_in_test or only_in_exp:
            log.info("Someone is missing keys.")
            return breaks

        for key, val in exp_d.items():
            test_val = test_d[key]
            this_key_trail = key_trail + (key,)

            # don't append a mismatch if we recurse
            append_diff = True
            val_to_record = None

            if isinstance(val, dict):
                is_val_match = self._find_breaks(val,
                                                 test_val,
                                                 this_key_trail,
                                                 is_ordered,
                                                 breaks)
                append_diff = False
            elif isinstance(val, (list, tuple)):
                exp_val_dict = self._seq_to_dict(val, is_ordered)
                test_val_dict = self._seq_to_dict(test_val, is_ordered)

                is_val_match = self._find_breaks(exp_val_dict,
                                                 test_val_dict,
                                                 this_key_trail,
                                                 is_ordered,
                                                 breaks)
                append_diff = False
            elif isinstance(val, type):
                if val == str:
                    val = (str, unicode)
                else:
                    val = (val,)

                is_val_match = isinstance(test_val, val)
                val_to_record = TypeMatch(*val)
            elif hasattr(val, 'match'):
                # regexp object
                try:
                    is_val_match = bool(val.match(test_val))
                except TypeError:
                    is_val_match = False

                val_to_record = RegexpMatch(val.pattern)
            elif callable(val):
                # use `val` as a callable
                try:
                    is_val_match = val(test_val)
                except Exception as e:
                    log.info("Value match for '%s' failed with %s." %
                             (this_key_trail, e))
                    is_val_match = False
            else:
                # kick to object equality
                is_val_match = (val == test_val)

            val_to_record = val_to_record or val

            if not is_val_match and append_diff:
                breaks.add_break(this_key_trail, val_to_record, test_val)

        return breaks

    def _seq_to_dict(self, seq, is_ordered=False):
        """Convert a sequence to a dict where each value is keyed by the seq
        index."""
        seq = seq or []

        if is_ordered:
            seq = sorted(seq)

        return dict(zip(range(len(seq)), seq))


class Breaks(object):
    """Represents the diff between a specification dict and a test dict."""

    def __init__(self, spec, against):
        """
        Args:
            spec (dict): the specification dict
            against (dict): the dict we're testing against
        """
        self.spec = spec
        self.against = against
        self.paths_to_breaks = {}

    def add_break(self, path_tuple, spec_val, against_val):
        self.paths_to_breaks[path_tuple] = (spec_val, against_val)

    def __nonzero__(self):
        return bool(self.paths_to_breaks)

    @property
    def breaks_str(self):
        """Print a comparison of expected vs. got."""
        return ("Expected:\n%s\n" % pprint.pformat(self.spec)
                + "\nGot:\n%s\n" % pprint.pformat(self.against)
                + "\nDiffs:\n%s\n" % pprint.pformat(self.paths_to_breaks))

    def __str__(self):
        return "<%d breaks>" % (len(self.paths_to_breaks.keys()))

    __unicode__ = __str__


class TypeMatch(object):

    def __init__(self, *to_match):
        """
        Args:
            to_match ([type, ...]): a list of types to match on
        """
        self.to_match = to_match

    def is_match(self, val):
        return isinstance(val, self.to_match)

    def __eq__(self, other):
        return other.to_match == self.to_match

    def __repr__(self):
        return "TypeMatch(%s)" % ', '.join([str(t) for t in self.to_match])

    __str__ = __repr__
    __unicode__ = __repr__


class RegexpMatch(object):
    """Represents a match that expects a value fitting a regexp pattern."""

    def __init__(self, pattern):
        self.pattern = pattern

    def __eq__(self, other):
        return getattr(other, 'pattern', other) == self.pattern

    def __repr__(self):
        return "RegexpMatch(r'%s')" % self.pattern

    __str__ = __repr__
    __unicode__ = __repr__


class MissingKey(object):
    """Represents a missing key in one of the dicts."""

    def __eq__(self, other):
        return isinstance(other, MissingKey)

    def __repr__(self):
        return "<MissingKey>"

    __str__ = __repr__
    __unicode__ = __repr__

