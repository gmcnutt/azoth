import unittest
from tools import *
from azoth import path

class PathTest(unittest.TestCase):

    def is_valid(self, loc):
        x, y = loc
        height = len(self.map)
        width = len(self.map[0])
        onmap = ((x >= 0) and (x < width) and (y >= 0) and (y < height))
        return onmap and self.map[y][x] != 9

    def heuristic(self, loc, dst):
        # use city-block distance; return cost, nearness
        x, y = loc
        dx = abs(dst[0] - x)
        dy = abs(dst[1] - y)
        nearness = dx + dy
        cost = 1 + self.map[y][x]
        return nearness, cost
    
    def test_1x1(self):
        self.map = ((0,),)
        p = path.find((0, 0), (0, 0), self.is_valid, self.heuristic)
        eq_(p, [(0, 0)])

    def test_simple_2x2(self):
        self.map = ((0, 0),
                    (0, 0))
        # start at (0, 0)
        p = path.find((0, 0), (0, 1), self.is_valid, self.heuristic)
        eq_(p, [(0, 0), (0, 1)])
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
        self.map = ((0, 0, 0),
                    (0, 0, 0),
                    (0, 0, 0))
        # start at (0, 0)
        p = path.find((0, 0), (2, 2), self.is_valid, self.heuristic)
        eq_(p, [(0, 0), (1, 0), (2, 0), (2, 1), (2, 2)])

    def test_offmap_destination(self):
        self.map = ((0, 0),
                    (0, 0))
        p = path.find((0, 0), (2, 3), self.is_valid, self.heuristic)
        eq_(p, [])

    def test_unpassable_destination(self):
        self.map = ((0, 0, 0),
                    (0, 9, 0),
                    (0, 0, 0))
        p = path.find((0, 0), (1, 1), self.is_valid, self.heuristic)
        eq_ (p, [])

    def test_5x5_room(self):
        self.map = ((0, 0, 0, 0, 0),
                    (0, 9, 9, 9, 0),
                    (0, 0, 9, 0, 0),
                    (9, 0, 9, 0, 9),
                    (0, 0, 0, 0, 0))
        p = path.find((0, 0), (4, 4), self.is_valid, self.heuristic)
        eq_ (p, [(0, 0), (0, 1), (0, 2), (1, 2), (1, 3), (1, 4), (2, 4),
                 (3, 4), (4, 4)])

    def test_unreachable(self):
        self.map = ((0, 0, 0, 0, 0),
                    (0, 0, 0, 0, 0),
                    (0, 0, 0, 0, 0),
                    (0, 0, 0, 9, 9),
                    (0, 0, 0, 9, 0))
        p = path.find((0, 0), (4, 4), self.is_valid, self.heuristic)
        eq_(p, [])
        
    def test_too_deep(self):
        self.map = ((0, 0, 0, 0, 0),
                    (0, 0, 0, 0, 0),
                    (0, 0, 0, 0, 0),
                    (0, 0, 0, 0, 0),
                    (0, 0, 0, 0, 0))
        p = path.find((0, 0), (4, 4), self.is_valid, self.heuristic, max_depth=7)
        eq_(p, [])

    def test_terrain_cost(self):
        self.map = ((0, 3, 4, 3, 0),
                    (0, 2, 5, 2, 0),
                    (0, 2, 4, 2, 0),
                    (0, 0, 3, 1, 0),
                    (0, 0, 0, 0, 0))
        p = path.find((0, 0), (4, 0), self.is_valid, self.heuristic)
        eq_(p, [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4),
                (1, 4), (2, 4), (3, 4), (4, 4),
                (4, 3), (4, 2), (4, 1), (4, 0)])
