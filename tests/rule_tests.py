from nose.tools import *
from azoth.hax2 import transactor
from azoth.hax2 import plane, pragma, rules, terrain
import unittest

def test_impassable_exc():
    pla = plane.Plane()
    print(pla)
    exc = rules.Impassable(pragma.Pragma(), terrain.RockWall, 
                           'place', 'x', 'y')
    print(exc)

class Passability(unittest.TestCase):

    def setUp(self):
        self.obj = pragma.Pragma()
        self.plane = plane.Plane(terrain=terrain.Grass)
        self.rules = rules.Ruleset()
        self.hax2 = transactor.Transactor(self.rules)

    def test_impassability(self):
        wall = terrain.RockWall
        self.obj.mmode = 'walk'
        self.rules.set_passability('walk', 'wall', rules.PASS_NONE)
        self.plane.set_terrain(6, 5, wall)
        assert_raises(rules.Impassable, self.rules.assert_passable, self.obj, 
                      self.plane, 6, 5)
