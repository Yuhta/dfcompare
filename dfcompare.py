import functools
import heapq
import os.path
import pandas as pd
import shutil
import tempfile

try:
    from itertools import zip_longest
except ImportError:
    from itertools import izip_longest as zip_longest

@functools.total_ordering
class BufferedIterator(object):

    def __init__(self, it):
        self._it = it
        self._buffered = False

    def head(self):
        if not self._buffered:
            self._head = next(self._it)
            self._buffered = True
        return self._head

    def __next__(self):
        if self._buffered:
            self._buffered = False
            return self._head
        else:
            return next(self._it)

    next = __next__

    def __eq__(self, other):
        return self.head() == other.head()

    def __lt__(self, other):
        return self.head() < other.head()

    def __bool__(self):
        try:
            self.head()
            return True
        except StopIteration:
            return False

    __nonzero__ = __bool__

def _external_sort(dfs):
    dir = tempfile.mkdtemp()
    try:
        q = []
        for df in dfs:
            if isinstance(df.index, pd.MultiIndex):
                index_col = list(range(len(df.index.levels)))
            else:
                index_col = 0
            df = df.sort_index()
            path = os.path.join(dir, str(len(q)) + '.csv')
            df.to_csv(path)
            chunks = pd.read_csv(path, chunksize=16, index_col=index_col)
            rows = BufferedIterator(row for df in chunks for row in df.itertuples())
            if rows:
                q.append(rows)
        heapq.heapify(q)
        while q:
            rows = heapq.heappop(q)
            yield next(rows)
            if rows:
                heapq.heappush(q, rows)
    finally:
        shutil.rmtree(dir)

class Identical(object):

    def __init__(self, l, r):
        self.left, self.right = l, r

class Different(object):

    def __init__(self, l, r, diff):
        self.left, self.right = l, r
        self.diff = diff

class InLeftOnly(object):

    def __init__(self, l):
        self.left = l

class InRightOnly(object):

    def __init__(self, r):
        self.right = r

def _compare_row(l, r):
    if r is None:
        return InLeftOnly(l)
    if l is None:
        return InRightOnly(r)
    assert len(l) == len(r)
    diff = []
    for i in range(1, len(l)):
        if l[i] != r[i]:
            diff.append(i-1)
    return Different(l, r, diff) if diff else Identical(l, r)

def compare(left, right, iterator=False, sort=True):
    def to_iter(df):
        if iterator:
            dfs = df
            if sort:
                return BufferedIterator(_external_sort(dfs))
            else:
                return BufferedIterator(row for df in dfs for row in df.itertuples())
        else:
            if sort:
                df = df.sort_index()
            return BufferedIterator(df.itertuples())
    left, right = to_iter(left), to_iter(right)
    while left and right:
        index = min(left.head()[0], right.head()[0])
        rows_l, rows_r = [], []
        while left and left.head()[0] == index:
            rows_l.append(next(left))
        while right and right.head()[0] == index:
            rows_r.append(next(right))
        for l, r in zip_longest(rows_l, rows_r):
            yield _compare_row(l, r)
    while left:
        yield _compare_row(next(left), None)
    while right:
        yield _compare_row(None, next(right))

if __name__ == '__main__' and '__file__' in globals():
    pass
