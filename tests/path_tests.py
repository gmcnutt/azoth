import unittest
from tools import *
from azoth import path

class PathTest(unittest.TestCase):

    def is_valid(self, loc):
        return ((loc[0] >= 0) and (loc[0] < self.dims[0]) and (loc[1] >= 0) and 
                (loc[1] < self.dims[1]))

    def heuristic(self, loc, dst):
        # use city-block distance
        dx = abs(dst[0] - loc[0])
        dy = abs(dst[1] - loc[1])
        return 1, dx + dy

    def test_1x1(self):
        self.dims = (1, 1)
        p = path.find((0, 0), (0, 0), self.is_valid, self.heuristic)
        eq_(p, [(0, 0)])

    def test_simple_2x2(self):
        self.dims = (2, 2)
        # start at (0, 0)
        p = path.find((0, 0), (0, 1), self.is_valid, self.heuristic)
        eq_(len(p), 2)
        p[-1] == (0, 1)
        p = path.find((0, 0), (1, 0), self.is_valid, self.heuristic)
        eq_(len(p), 2)
        p[-1] == (1, 0)
        p = path.find((0, 0), (1, 1), self.is_valid, self.heuristic)
        eq_(len(p), 3)
        p[-1] == (1, 1)
        # start at (1, 1)
        p = path.find((1, 1), (0, 1), self.is_valid, self.heuristic)
        eq_(len(p), 2)
        p[-1] == (0, 1)
        p = path.find((1, 1), (1, 0), self.is_valid, self.heuristic)
        eq_(len(p), 2)
        p[-1] == (1, 0)
        p = path.find((1, 1), (0, 0), self.is_valid, self.heuristic)
        eq_(len(p), 3)
        p[-1] == (0, 0)

    def test_simple_3x3(self):
        self.dims = (3, 3)
        # start at (0, 0)
        p = path.find((0, 0), (2, 2), self.is_valid, self.heuristic)
        eq_(p, [(0, 0), (0, 1), (1, 1), (2, 1), (2, 2)])

    def test_offmap_destination(self):
        self.dims = (2, 2)
        p = path.find((0, 0), (2, 3), self.is_valid, self.heuristic)
        eq_(p, [])
