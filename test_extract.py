import unittest

from util.extract import extract


class Foo(object):
    def __init__(self, bar):
        self.bar = bar


class TestExtract(unittest.TestCase):
    def test_simple(self):
        foos = map(Foo, 'acb')
        bars = map(extract.bar, foos)

        self.assertEqual(list(bars), list('acb'))

        matrix = [
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9],
        ]

        col2 = list(map(extract[1], matrix))

        self.assertEqual([2, 5, 8], col2)

    def test_compound(self):
        foos = [Foo('hello'), Foo('world')]
        bars = list(map(extract.bar[2], foos))

        self.assertEqual(['l', 'r'], bars)

        d1 = {'x': Foo('cat'), 'y': Foo('dog')}
        d2 = {'x': Foo('hound'), 'y': Foo('rabbit')}

        actual = list(map(extract['y'].bar[2], [d1, d2]))
        self.assertEqual(['g', 'b'], actual)

    def test_empty(self):
        foos = [Foo('abc'), Foo('123'), Foo('doremi')]
        self.assertEqual(foos, list(map(extract, foos)))
