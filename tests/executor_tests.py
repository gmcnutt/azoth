from tools import eq_, ok_, assert_raises, raises_
from azoth import executor, place, terrain, terrainmap
from azoth.hax2 import item, pragma, weapon
import unittest


class TestException(Exception):
    pass


def check_raise(func):
    def fwrap(instance, *args):
        if hasattr(instance, 'exception'):
            raise instance.exception
        func(instance, *args)
    return fwrap


def assert_item_at(obj, pla, x, y):
    eq_(obj.loc, (pla, x, y))
    ok_(obj in pla.get_items(x, y))


def assert_being_at(obj, pla, x, y):
    eq_(obj.loc, (pla, x, y))
    eq_(obj, pla.get_occupant(x, y))


def assert_not_at(obj, pla, x, y):
    ok_(obj.loc != (pla, x, y))
    ok_(obj not in pla.get_items(x, y))
    ok_(obj != pla.get_occupant(x, y))


def test_impassable_exc():
    pla = place.Sector()
    print(pla)
    exc = executor.Impassable(pragma.Pragma(), terrain.RockWall,
                           'place', 'x', 'y')
    print(exc)

DIRMAP = {'north': (0, -1),
          'northeast': (1, -1),
          'east': (1,  0),
          'southeast': (1,  1),
          'south': (0,  1),
          'southwest': (-1,  1),
          'west': (-1,  0),
          'northwest': (-1, -1)}


class Passability(unittest.TestCase):

    def setUp(self):
        self.obj = pragma.Pragma()
        self.place = place.Sector(default_terrain=terrain.Grass)
        self.rules = executor.Ruleset()
        self.hax2 = executor.Executor(self.rules)

    def test_impassability(self):
        wall = terrain.RockWall
        self.obj.mmode = 'walk'
        self.rules.set_passability('walk', 'wall', executor.PASS_NONE)
        self.place.set_terrain(6, 5, wall)
        assert_raises(executor.Impassable, self.rules.assert_passable,
                      self.obj, self.place, 6, 5)


class Default(unittest.TestCase):
    def setUp(self):
        self.rules = executor.Ruleset()
        self.hax2 = executor.Executor(self.rules)
        self.tmap = terrainmap.load_from_nazghul_scm('gregors-hut.scm')
        self.obj = pragma.Pragma()
        self.place = place.Sector(default_terrain=terrain.Grass)


class PutOnMap(Default):

    def test_put_object(self):
        self.hax2.put_item_on_map(self.obj, self.place, 0, 0)
        assert_item_at(self.obj, self.place, 0, 0)

    def test_impassable_occupant(self):
        o1 = pragma.Pragma()
        o2 = pragma.Pragma()
        self.hax2.put_being_on_map(o1, self.place, 0, 0)
        assert_raises(executor.Occupied, self.hax2.put_being_on_map, o2,
                      self.place, 0, 0)
        assert_being_at(o1, self.place, 0, 0)
        eq_(o2.loc, (None, None, None))

    def test_item(self):
        itm = item.Item()
        self.hax2.put_item_on_map(itm, self.place, 0, 0)
        assert_item_at(itm, self.place, 0, 0)

    def test_sword(self):
        sword = weapon.Sword()
        self.hax2.put_item_on_map(sword, self.place, 0, 0)
        assert_item_at(sword, self.place, 0, 0)


class RemoveFromMap(Default):

    def test_remove_occupant(self):
        self.hax2.put_item_on_map(self.obj, self.place, 0, 0)
        self.hax2.remove_item_from_map(self.obj)
        eq_((None, None, None), self.obj.loc)
        eq_(None, self.place.get_occupant(0, 0))

    def test_remove_nonexisting(self):
        self.obj.loc = (self.place, 0, 0)
        assert_raises(place.NotThereError, self.hax2.remove_item_from_map, 
                      self.obj)


class MoveOnMap(Default):

    def check_move(self, direction, dx, dy, newx, newy):
        loc = self.obj.loc
        self.hax2.move_being_on_map(self.obj, *DIRMAP[direction])
        assert_being_at(self.obj, self.place, newx, newy)
        assert_not_at(self.obj, self.place, loc[1], loc[2])

    def test_move(self):
        self.hax2.put_being_on_map(self.obj, self.place, 0, 0)
        self.check_move('east',  1,  0, 1, 0)
        self.check_move('south', 0,  1, 1, 1)
        self.check_move('west', -1,  0, 0, 1)
        self.check_move('north', 0, -1, 0, 0)
        self.check_move('southeast', 1, 1, 1, 1)
        self.check_move('northeast', 1,-1, 2, 0)
        self.check_move('southwest',-1, 1, 1, 1)
        self.check_move('northwest',-1,-1, 0, 0)
        
    def test_impassable_terrain(self):
        wall = terrain.RockWall
        self.obj.mmode = 'walk'
        self.rules.set_passability('walk', 'wall', executor.PASS_NONE)
        self.place.set_terrain(6, 5, wall)
        self.hax2.put_being_on_map(self.obj, self.place, 5, 5)
        assert_raises(executor.Impassable, self.hax2.move_being_on_map, 
                      self.obj, *DIRMAP['east'])
        assert_being_at(self.obj, self.place, 5, 5)

    def test_occupant(self):
        o1 = pragma.Pragma()
        o2 = pragma.Pragma()
        self.hax2.put_being_on_map(o1, self.place, 0, 0)
        self.hax2.put_being_on_map(o2, self.place, 1, 0)
        assert_raises(executor.Occupied, self.hax2.move_being_on_map, o1,
                      *DIRMAP['east'])
        assert_being_at(o1, self.place, 0, 0)
        assert_being_at(o2, self.place, 1, 0)

    def test_swap(self):
        o1 = pragma.Pragma()
        o2 = pragma.Pragma()
        self.hax2.put_being_on_map(o1, self.place, 0, 0)
        self.hax2.put_being_on_map(o2, self.place, 1, 0)
        try:
            self.hax2.move_being_on_map(o1, *DIRMAP['east'])
        except executor.Occupied as e:
            self.hax2.rotate_beings_on_map(o1, e.obj)
        assert_being_at(o1, self.place, 1, 0)
        assert_being_at(o2, self.place, 0, 0)


class MoveFromMapToBag(Default):

    def setUp(self):
        super(MoveFromMapToBag, self).setUp()
        self.bag = pragma.Bag(limit=1)
    
    def test_ok(self):
        self.hax2.put_item_on_map(self.obj, self.place, 0, 0)
        self.hax2.move_item_from_map_to_bag(self.obj, self.bag)
        assert_not_at(self.obj, self.place, 0, 0)
        ok_(self.obj in self.bag)

    def test_full(self):
        self.hax2.put_item_on_map(self.obj, self.place, 0, 0)
        obj2 = pragma.Pragma()
        self.hax2.put_item_on_map(obj2, self.place, 0, 0)
        self.hax2.move_item_from_map_to_bag(self.obj, self.bag)
        raises_(executor.WontFitError, self.hax2.move_item_from_map_to_bag, 
                obj2, self.bag)
        assert_item_at(obj2, self.place, 0, 0)
        ok_(obj2 not in self.bag)
        assert_not_at(self.obj, self.place, 0, 0)
        ok_(self.obj in self.bag)

