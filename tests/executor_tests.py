from tools import *
from azoth import executor
from azoth.hax2 import item, plane, pragma, terrain, terrainmap, weapon
import unittest

class TestException(Exception):
    pass

def check_raise(func):
    def fwrap(instance, *args):
        if hasattr(instance, 'exception'):
            raise instance.exception
        func(instance, *args)
    return fwrap

def assert_at(obj, pla, x, y):
    eq_(obj.loc, (pla, x, y))
    ok_(obj in pla.get(x, y))

def assert_not_at(obj, pla, x, y):
    ok_(obj.loc != (pla, x, y))
    ok_(obj not in pla.get(x, y))

def test_impassable_exc():
    pla = plane.Plane()
    print(pla)
    exc = executor.Impassable(pragma.Pragma(), terrain.RockWall, 
                           'place', 'x', 'y')
    print(exc)

class Passability(unittest.TestCase):

    def setUp(self):
        self.obj = pragma.Pragma()
        self.plane = plane.Plane(terrain=terrain.Grass)
        self.rules = executor.Ruleset()
        self.hax2 = executor.Transactor(self.rules)

    def test_impassability(self):
        wall = terrain.RockWall
        self.obj.mmode = 'walk'
        self.rules.set_passability('walk', 'wall', executor.PASS_NONE)
        self.plane.set_terrain(6, 5, wall)
        assert_raises(executor.Impassable, self.rules.assert_passable, self.obj, 
                      self.plane, 6, 5)

class Default(unittest.TestCase):
    def setUp(self):
        self.rules = executor.Ruleset()
        self.hax2 = executor.Transactor(self.rules)
        self.tmap = terrainmap.load_from_nazghul_scm('gregors-hut.scm')
        self.obj = pragma.Pragma()
        self.plane = plane.Plane(terrain=terrain.Grass)

class PutOnMap(Default):

    def test_put_object(self):
        self.hax2.put_on_map(self.obj, self.plane, 0, 0)
        assert_at(self.obj, self.plane, 0, 0)

    def test_impassable_occupant(self):
        o1 = pragma.Pragma()
        o1.occupant = True
        o2 = pragma.Pragma()
        o2.occupant = True
        self.hax2.put_on_map(o1, self.plane, 0, 0)
        assert_raises(executor.Occupied, self.hax2.put_on_map, o2, self.plane, 0, 0)
        assert_at(o1, self.plane, 0, 0)
        eq_(o2.loc, (None, None, None))

    def test_item(self):
        itm = item.Item()
        self.hax2.put_on_map(itm, self.plane, 0, 0)
        assert_at(itm, self.plane, 0, 0)

    def test_sword(self):
        sword = weapon.Sword()
        self.hax2.put_on_map(sword, self.plane, 0, 0)
        assert_at(sword, self.plane, 0, 0)

class RemoveFromMap(Default):

    def test_remove_occupant(self):
        self.hax2.put_on_map(self.obj, self.plane, 0, 0)
        self.hax2.remove_from_map(self.obj)
        eq_((None, None, None), self.obj.loc)
        eq_([], self.plane.get(0, 0))

    def test_remove_nonexisting(self):
        self.obj.loc = (self.plane, 0, 0)
        assert_raises(plane.NotThereError, self.hax2.remove_from_map, self.obj)

class MoveOnMap(Default):


    def check_move(self, direction, dx, dy, newx, newy):
        loc = self.obj.loc
        self.hax2.move_on_map(self.obj, direction=direction)
        assert_at(self.obj, self.plane, newx, newy)
        eq_([], self.plane.get(loc[1], loc[2]))

    def test_move(self):
        self.hax2.put_on_map(self.obj, self.plane, 0, 0)
        self.check_move('east',  1,  0, 1, 0)
        self.check_move('south', 0,  1, 1, 1)
        self.check_move('west', -1,  0, 0, 1)
        self.check_move('north', 0, -1, 0, 0)
        self.check_move('southeast', 1, 1, 1, 1)
        self.check_move('northeast', 1,-1, 2, 0)
        self.check_move('southwest',-1, 1, 1, 1)
        self.check_move('northwest',-1,-1, 0, 0)
        
    def test_move_invalid_direction(self):
        self.hax2.put_on_map(self.obj, self.plane, 0, 0)
        loc = self.obj.loc
        assert_raises(KeyError, self.hax2.move_on_map, self.obj, 'yonder')
        assert_at(self.obj, *loc)

    def test_impassable_terrain(self):
        wall = terrain.RockWall
        self.obj.mmode = 'walk'
        self.rules.set_passability('walk', 'wall', executor.PASS_NONE)
        self.plane.set_terrain(6, 5, wall)
        self.hax2.put_on_map(self.obj, self.plane, 5, 5)
        assert_raises(executor.Impassable, self.hax2.move_on_map, self.obj, 'east')
        assert_at(self.obj, self.plane, 5, 5)

    def test_occupant(self):
        o1 = pragma.Pragma()
        o1.occupant = True
        o2 = pragma.Pragma()
        o2.occupant = True
        self.hax2.put_on_map(o1, self.plane, 0, 0)
        self.hax2.put_on_map(o2, self.plane, 1, 0)
        assert_raises(executor.Occupied, self.hax2.move_on_map, o1, 'east')
        assert_at(o1, self.plane, 0, 0)
        assert_at(o2, self.plane, 1, 0)

    def test_swap(self):
        o1 = pragma.Pragma()
        o1.occupant = True
        o2 = pragma.Pragma()
        o2.occupant = True
        self.hax2.put_on_map(o1, self.plane, 0, 0)
        self.hax2.put_on_map(o2, self.plane, 1, 0)
        try:
            self.hax2.move_on_map(o1, 'east')
        except executor.Occupied as e:
            self.hax2.rotate_on_map(o1, e.obj)
        assert_at(o1, self.plane, 1, 0)
        assert_at(o2, self.plane, 0, 0)


class MoveFromMapToBag(Default):

    def setUp(self):
        super(MoveFromMapToBag, self).setUp()
        self.bag = pragma.Bag(limit=1)
    
    def test_ok(self):
        self.hax2.put_on_map(self.obj, self.plane, 0, 0)
        self.hax2.move_from_map_to_bag(self.obj, self.bag)
        assert_not_at(self.obj, self.plane, 0, 0)
        ok_(self.obj in self.bag)

    def test_full(self):
        self.hax2.put_on_map(self.obj, self.plane, 0, 0)
        obj2 = pragma.Pragma()
        self.hax2.put_on_map(obj2, self.plane, 0, 0)
        self.hax2.move_from_map_to_bag(self.obj, self.bag)
        raises_(executor.WontFitError, self.hax2.move_from_map_to_bag, obj2,
                self.bag)
        assert_at(obj2, self.plane, 0, 0)
        ok_(obj2 not in self.bag)
        assert_not_at(self.obj, self.plane, 0, 0)
        ok_(self.obj in self.bag)

