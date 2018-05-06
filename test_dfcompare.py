from dfcompare import BufferedIterator, compare, Identical, Different, InLeftOnly, InRightOnly
import pandas as pd
import unittest

class TestBufferedIterator(unittest.TestCase):

    def test_head(self):
        it = BufferedIterator(iter([1, 2, 3]))
        self.assertEqual(it.head(), 1)
        self.assertEqual(next(it), 1)
        self.assertEqual(next(it), 2)
        self.assertEqual(it.head(), 3)
        self.assertEqual(next(it), 3)
        with self.assertRaises(StopIteration):
            it.head()

    def test_bool(self):
        it = BufferedIterator(iter([42]))
        self.assertTrue(it)
        next(it)
        self.assertFalse(it)

class TestCompare(unittest.TestCase):

    def test_no_sort(self):
        l = pd.DataFrame({'A': [1, 2, 3], 'B': ['foo', 'bar', 'quux']})
        r = pd.DataFrame({'A': [1, 4, 3], 'B': ['foo', 'bar', 'quuy']})
        d = list(compare(l, r, sort=False))
        self.assertEqual(len(d), 3)
        self.assertIsInstance(d[0], Identical)
        self.assertEqual(d[0].left, d[0].right)
        self.assertIsInstance(d[1], Different)
        self.assertEqual(d[1].left, (1, 2, 'bar'))
        self.assertEqual(d[1].right, (1, 4, 'bar'))
        self.assertEqual(d[1].diff, [0])
        self.assertIsInstance(d[2], Different)
        self.assertEqual(d[2].diff, [1])

    def test_multi_index(self):
        index = pd.MultiIndex.from_tuples(((2, 1), (1, 2), (1, 1)))
        l = pd.DataFrame({'A': [1, 2, 3]}, index=index)
        index = pd.MultiIndex.from_tuples(((1, 2), (1, 1), (2, 1)))
        r = pd.DataFrame({'A': [4, 3, 1]}, index=index)
        d = list(compare(l, r))
        self.assertEqual(len(d), 3)
        self.assertIsInstance(d[0], Identical)
        self.assertIsInstance(d[1], Different)
        self.assertEqual(d[1].left, ((1, 2), 2))
        self.assertEqual(d[1].right, ((1, 2), 4))
        self.assertIsInstance(d[2], Identical)

    def test_in_left_only(self):
        l = pd.DataFrame({'A': [1, 2, 3]}, index=(1, 2, 3))
        r = pd.DataFrame({'A': [1, 2]}, index=(1, 3))
        d = list(compare(l, r))
        self.assertEqual(len(d), 3)
        self.assertIsInstance(d[1], InLeftOnly)

    def test_in_right_only(self):
        l = pd.DataFrame({'A': [1, 2]}, index=(1, 3))
        r = pd.DataFrame({'A': [1, 2, 3]}, index=(1, 2, 3))
        d = list(compare(l, r))
        self.assertEqual(len(d), 3)
        self.assertIsInstance(d[1], InRightOnly)

    def test_external_sort(self):
        l = [pd.DataFrame({'A': [1, 2, 3]}, index=(1, 2, 3)),
             pd.DataFrame({'A': [4, 5, 6]}, index=(4, 5, 6))]
        r = [pd.DataFrame({'A': [6, 5, 4]}, index=(6, 5, 4)),
             pd.DataFrame({'A': [3, 2, 1]}, index=(3, 2, 1))]
        d = list(compare(iter(l), iter(r), iterator=True))
        self.assertEqual(len(d), 6)
        for diff in d:
            self.assertIsInstance(diff, Identical)
        self.assertEqual([diff.left[0] for diff in d], list(range(1, 7)))

    def test_external_sort_multi_index(self):
        l = [pd.DataFrame({'A': [1, 2, 3], 'B': [1, 2, 3], 'C': [1, 2, 3]}).set_index(['A', 'B']),
             pd.DataFrame({'A': [4, 5, 6], 'B': [4, 5, 6], 'C': [4, 5, 6]}).set_index(['A', 'B'])]
        r = [pd.DataFrame({'A': [6, 5, 4], 'B': [6, 5, 4], 'C': [6, 5, 4]}).set_index(['A', 'B']),
             pd.DataFrame({'A': [3, 2, 1], 'B': [3, 2, 1], 'C': [3, 2, 1]}).set_index(['A', 'B'])]
        d = list(compare(iter(l), iter(r), iterator=True))
        self.assertEqual(len(d), 6)
        for diff in d:
            self.assertIsInstance(diff, Identical)
        self.assertEqual([diff.left[0] for diff in d], [(i, i) for i in range(1, 7)])

if __name__ == '__main__' and '__file__' in globals():
    unittest.main()
