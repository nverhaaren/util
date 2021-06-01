import unittest
from functools import partial

from util.simple_lrucache import SimpleLRUCache, memoize_lru


class TestSimpleLRUCache(unittest.TestCase):
    @classmethod
    def square(cls, x):
        return x * x

    @classmethod
    def audit_square(cls, out, x):
        out.append(x)
        return x * x

    def test_correctness(self):
        cache = SimpleLRUCache(8)
        memoized = memoize_lru(cache)(self.square)
        squares = list(map(memoized, range(16)))
        self.assertEqual(len(cache), 8)
        self.assert_(not any(((i,), frozenset()) in cache for i in range(8)))
        self.assert_(all(((i,), frozenset()) in cache for i in range(8, 16)))
        self.assertEqual(set(cache), {((i,), frozenset()) for i in set(range(8, 16))})
        reversed_squares = list(map(memoized, reversed(range(16))))

        self.assertEqual(squares, list(reversed(reversed_squares)))

    def test_audit(self):
        cache = SimpleLRUCache(4)
        audit = []
        memoized = memoize_lru(cache)(partial(self.audit_square, audit))
        list(map(memoized, range(8)))
        squares = list(map(memoized, range(8)))
        reversed_squares = list(map(memoized, reversed(range(8))))

        self.assertEqual(squares, list(reversed(reversed_squares)))
        self.assertEqual(audit, range(8) * 2 + list(reversed(range(4))))

    def test_complex_access(self):
        cache = SimpleLRUCache(4)
        audit = []
        memoized = memoize_lru(cache)(partial(self.audit_square, audit))
        for i in range(8):
            inputs = [(i + 1) * j % 8 for j in range(8)]
            list(map(memoized, inputs))

        self.assertEqual(audit,
                         range(8) +
                         [0, 2, 4, 6] +
                         [3, 1, 4, 7, 2, 5, 0] +
                         [4] +
                         [7, 4, 1, 6, 3] +
                         [0, 4, 2] +
                         [7, 6, 5, 4, 3, 2, 1] +
                         [0])
