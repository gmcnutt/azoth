import unittest
from tools import *
from azoth import path

class PathTest(unittest.TestCase):

    def neighbors4(self, loc):
        """ Enumerate the 4 neighbors, filtering out off-map or impassable
        neighbors. """
        directions = ((-1, 0), (1, 0), (0, -1), (0, 1))
        for direction in directions:
            x = loc[0] + direction[0]
            y = loc[1] + direction[1]
            height = len(self.map)
            width = len(self.map[0])
            onmap = ((x >= 0) and (x < width) and (y >= 0) and (y < height))
            if not onmap:
                continue
            impassable = self.map[y][x] == 9
            if impassable:
                continue
            else:
                yield x, y

    def neighbors8(self, loc):
        """ Enumerate the 8 neighbors, filtering out off-map, impassable or
        diagonally blocked neighbors. """
        directions = ((-1, -1), ( 0, -1), (1, -1), 
                      (-1,  0),           (1,  0),
                      (-1,  1), ( 0,  1), (1,  1))
        blockers = {
            (-1, -1) : ((-1, 0), (0, -1)),
            (1, 1): ((0, -1), (1, 0)),
            (-1, 1): ((-1, 0), (0, 1)),
            (1, 1): ((1, 0), (0, 1))
            }
        x0, y0 = loc
        for direction in directions:
            x = x0 + direction[0]
            y = y0 + direction[1]
            height = len(self.map)
            width = len(self.map[0])
            onmap = ((x >= 0) and (x < width) and (y >= 0) and (y < height))
            if not onmap:
                continue
            impassable = self.map[y][x] == 9
            if impassable:
                continue
            blocked = False
            for b in blockers.get(direction, []):
                bx = x0 + b[0]
                by = y0 + b[1]
                blocked = self.map[by][bx] == 9
            if blocked:
                continue
            else:
                yield x, y

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
        p = path.find((0, 0), (0, 0), self.neighbors4, self.heuristic)
        eq_(p, [])

    def test_simple_2x2(self):
        self.map = ((0, 0),
                    (0, 0))
        # start at (0, 0)
        p = path.find((0, 0), (0, 1), self.neighbors4, self.heuristic)
        eq_(p, [(0, 1)])
        p = path.find((0, 0), (1, 0), self.neighbors4, self.heuristic)
        eq_(p, [(1, 0)])
        p = path.find((0, 0), (1, 1), self.neighbors4, self.heuristic)
        eq_(p, [(1, 0), (1, 1)])
        # start at (1, 1)
        p = path.find((1, 1), (0, 1), self.neighbors4, self.heuristic)
        eq_(p, [(0, 1)])
        p = path.find((1, 1), (1, 0), self.neighbors4, self.heuristic)
        eq_(p, [(1, 0)])
        p = path.find((1, 1), (0, 0), self.neighbors4, self.heuristic)
        eq_(p, [(0, 1), (0, 0)])

    def test_simple_3x3(self):
        self.map = ((0, 1, 0),
                    (0, 0, 0),
                    (0, 1, 0))
        # start at (0, 0)
        p = path.find((0, 0), (2, 2), self.neighbors4, self.heuristic)
        eq_(p, [(0, 1), (1, 1), (2, 1), (2, 2)])

    def test_offmap_destination(self):
        self.map = ((0, 0),
                    (0, 0))
        p = path.find((0, 0), (2, 3), self.neighbors4, self.heuristic)
        eq_(p, [])

    def test_unpassable_destination(self):
        self.map = ((0, 0, 0),
                    (0, 9, 0),
                    (0, 0, 0))
        p = path.find((0, 0), (1, 1), self.neighbors4, self.heuristic)
        eq_ (p, [])

    def test_5x5_room(self):
        self.map = ((0, 0, 0, 0, 0),
                    (0, 9, 9, 9, 0),
                    (0, 0, 9, 0, 0),
                    (9, 0, 9, 0, 9),
                    (0, 0, 0, 0, 0))
        p = path.find((0, 0), (4, 4), self.neighbors4, self.heuristic)
        eq_ (p, [(0, 1), (0, 2), (1, 2), (1, 3), (1, 4), (2, 4),
                 (3, 4), (4, 4)])

    def test_unreachable(self):
        self.map = ((0, 0, 0, 0, 0),
                    (0, 0, 0, 0, 0),
                    (0, 0, 0, 0, 0),
                    (0, 0, 0, 0, 9),
                    (0, 0, 0, 9, 0))
        p = path.find((0, 0), (4, 4), self.neighbors4, self.heuristic)
        eq_(p, [])
        p = path.find((0, 0), (4, 4), self.neighbors8, self.heuristic)
        eq_(p, [])
        
    def test_too_deep(self):
        self.map = ((0, 0, 0, 0, 0),
                    (0, 0, 0, 0, 0),
                    (0, 0, 0, 0, 0),
                    (0, 0, 0, 0, 0),
                    (0, 0, 0, 0, 0))
        p = path.find((0, 0), (4, 4), self.neighbors4, self.heuristic, 
                      max_depth=7)
        eq_(p, [])

    def test_terrain_cost(self):
        self.map = ((0, 3, 4, 3, 0),
                    (0, 2, 5, 2, 0),
                    (0, 2, 4, 2, 0),
                    (0, 0, 3, 1, 0),
                    (0, 0, 0, 0, 0))
        p = path.find((0, 0), (4, 0), self.neighbors4, self.heuristic)
        eq_(p, [(0, 1), (0, 2), (0, 3), (0, 4),
                (1, 4), (2, 4), (3, 4), (4, 4),
                (4, 3), (4, 2), (4, 1), (4, 0)])

    def test_8n_3x3(self):
        self.map = ((0, 0, 0),
                    (0, 0, 0),
                    (0, 0, 0))
        # start at (0, 0)
        p = path.find((0, 0), (2, 2), self.neighbors8, self.heuristic)
        eq_(p, [(1, 1), (2, 2)])
        
