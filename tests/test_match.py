"""
Test matching JSON dicts.
"""

import copy
import unittest
import re
import jsonmatch


class TestMatch(unittest.TestCase):

    def setUp(self):
        self.length_lambda = lambda x: len(x) == 3
        self.crazy_regexp = re.compile(r'[a-z][A-Z]{3}')

        self.spec = {
            'foo': 1,
            'b': str,
            'c': {
                'd': [1],
                'e': list,
                'f': self.crazy_regexp,
                'g': self.length_lambda,
            }
        }

        self.matchingd = {
            'foo': 1,
            'b': 'abcd',
            'c': {
                'd': [1],
                'e': [1, 2, 3],
                'f': "aBBB",
                'g': '123',
            }
        }
        self.shuffled = copy.deepcopy(self.matchingd)
        self.shuffled['c']['e'] = [3, 1, 2]


        self.matcher = jsonmatch.compile(self.spec)
        self.ordermatcher = jsonmatch.compile(self.matchingd)

    def test_match(self):
        """Test that we can match by type and regexp properly."""
        bs = self.matcher.breaks(self.matchingd)
        print bs
        print type(bs)

        assert not bs

        assert self.matcher.matches(self.matchingd)
        self.matcher.assert_matches(self.matchingd)

    def test_match_self(self):
        breaks = self.matcher.breaks(self.spec)
        assert breaks, ("Matcher doesn't match against its own spec because "
                        "of types.")

        self.assertEqual(
            breaks.paths_to_breaks,
            {
                ('b',): (jsonmatch.TypeMatch(str, unicode),
                         str),
                ('c', 'e'): (jsonmatch.TypeMatch(list),
                             list),
                ('c', 'f'): (self.crazy_regexp.pattern,
                             self.crazy_regexp),
                ('c', 'g'): (self.length_lambda,
                             self.length_lambda),
            })

    def test_mismatch(self):
        badd = dict(self.matchingd)
        badd['b'] = 2

        breaks = self.matcher.breaks(badd)
        assert breaks

        self.assertEqual(
            breaks.paths_to_breaks,
            {(u'b',): (jsonmatch.TypeMatch(str, unicode), 2)},
            "'b' should be a string type.")

    def test_bad_regexp(self):
        """Test that we break on violating a regexp expectation."""
        badd = dict(self.matchingd)
        badd['c']['f'] = "doesn't match"

        breaks = self.matcher.breaks(badd)
        assert breaks

        self.assertEqual(
            breaks.paths_to_breaks,
            {('c', 'f'): (jsonmatch.RegexpMatch(self.crazy_regexp.pattern),
                          "doesn't match")})

    def test_nonexistent_key(self):
        """Check that we report a nonexistent key properly."""
        badd = dict(self.matchingd)
        badd['whoa'] = 1

        breaks = self.matcher.breaks(badd)
        assert breaks

        self.assertEqual(
            breaks.paths_to_breaks,
            {('whoa',): (jsonmatch.MissingKey(), 1)})


    def test_callable_failure(self):
        """Test the failure of a callable expectation."""
        badd = dict(self.matchingd)
        badd['c']['g'] = [1, 2, 3, 4]

        breaks = self.matcher.breaks(badd)
        assert breaks

        self.assertEqual(
            breaks.paths_to_breaks,
            {('c', 'g'): (self.length_lambda, [1, 2, 3, 4])})

    def test_unordered(self):
        """Ordering is not enforced by default"""
        assert not self.ordermatcher.breaks(self.shuffled)

    def test_ordering_flag_makes_order_matter(self):
        """Ordering matters if you want it to"""
        # the flag does what you expect.
        assert not self.ordermatcher.breaks(self.shuffled, is_ordered=False)
        assert self.ordermatcher.breaks(self.shuffled, is_ordered=True)
