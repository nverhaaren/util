import unittest

from util.memory import get_all_referents, get_all_referrers


class TestReferences(unittest.TestCase):
    def test_basic(self):
        inner_d = {}
        outer_d = {'d': inner_d}
        referents = get_all_referents([outer_d])
        self.assertIn(inner_d, referents)
        referrers = get_all_referrers([inner_d])
        self.assertIn(outer_d, referrers)
