#from nose.tools import *
from tools import *
from azoth import place
from azoth.hax2 import terrain, terrainmap
import unittest
import warnings

def test_not_there_error():
    exc = place.NotThereError('Yonder', 4, 5, 'Sumethin')
    assert_equal('Sumethin not in Yonder at (4, 5)', '%s' % exc)

def test_already_there_error():
    exc = place.AlreadyThereError('Yonder', 4, 5, 'Sumethin')
    assert_equal('Sumethin already in Yonder at (4, 5)', '%s' % exc)

def test_offmap_error():
    exc = place.OffMapError(place.Sector(name='Yonder'), 4, 5)
    assert_equal('(4, 5) not in Sector Yonder', '%s' % exc)

class Place(unittest.TestCase):

    def setUp(self):
        self.place = place.Place(1, 1)

    def save(self):
        sfile = open('place_tests.p', 'w')
        self.place.save(sfile)
        sfile.close()

    def load(self):
        lfile = open('place_tests.p')
        self.place = place.Place.load(lfile)
        lfile.close()

    def test_place(self):
        assert_is_not_none(self.place)

    def test_put(self):
        self.place.add_item(0, 0, 'a')
        eq_(['a'], self.place.get_items(0, 0))

    def test_get_nothing(self):
        eq_([], self.place.get_items(0, 0))

    def test_put_2(self):
        self.place.add_item(0, 0, 'i1')
        self.place.add_item(0, 0, 'i2')
        eq_(set(['i1', 'i2']), set(self.place.get_items(0, 0)))

    def test_double_put_same(self):
        item = 'i1'
        self.place.add_item(0, 0, item)
        assert_raises(place.AlreadyThereError, self.place.add_item, 0, 0, item)
        eq_([item], self.place.get_items(0, 0))

    def test_remove(self):
        self.test_put()
        self.place.remove_item(0, 0, 'a')
        eq_([], self.place.get_items(0, 0))

    def test_remove_not_there(self):
        assert_raises(place.NotThereError, self.place.remove_item, 0, 0, 'a')
        assert_raises(place.NotThereError, self.place.remove_occupant, 0, 0)

    def test_remove_2(self):
        self.test_put_2()
        self.place.remove_item(0, 0, 'i1')
        eq_(['i2'], self.place.get_items(0, 0))
        self.place.remove_item(0, 0, 'i2')
        eq_([], self.place.get_items(0, 0))

    def test_remove_all_of_nothing(self):
        self.place.remove_all(0, 0)
        eq_([], self.place.get_items(0, 0))
        eq_(None, self.place.get_occupant(0, 0))

    def test_remove_all_of_2(self):
        self.test_put_2()
        self.place.remove_all(0, 0)
        eq_([], self.place.get_items(0, 0))

    def test_put_offmap(self):
        assert_raises(place.OffMapError, self.place.add_item, -1,  0, 'a')
        assert_raises(place.OffMapError, self.place.add_item,  0, -1, 'a')
        assert_raises(place.OffMapError, self.place.add_item, 10,  0, 'a')
        assert_raises(place.OffMapError, self.place.add_item,  0, 10, 'a')

    def test_blit_terrain_map(self):
        tmap = terrainmap.load_from_nazghul_scm('../haxima/scm/gregors-hut.scm')
        self.place.blit_terrain_map(0, 0, tmap)

    def test_set_occupant(self):
        self.place.set_occupant(0, 0, 'a')
        eq_('a', self.place.get_occupant(0, 0))

    def test_remove_all_with_occupant(self):
        self.place.set_occupant(0, 0, 'a')
        self.place.remove_all(0, 0)
        eq_(None, self.place.get_occupant(0, 0))

    def test_explored(self):
        eq_(False, self.place.get_explored(0, 0))
        self.place.set_explored(0, 0, True)
        ok_(self.place.get_explored(0, 0))
        self.place.set_explored(0, 0, False)
        eq_(False, self.place.get_explored(0, 0))

    def test_save_load(self):
        self.place.add_item(0, 0, 'a')
        self.place.set_occupant(0, 0, 'b')
        self.place.set_explored(0, 0, True)
        self.save()
        self.load()
        eq_(['a'], self.place.get_items(0, 0))
        eq_('b', self.place.get_occupant(0, 0))
        ok_(self.place.get_explored(0, 0))

class WorldTest(unittest.TestCase):

    def test_init(self):
        world = place.World(1, 1, default_terrain=terrain.Grass)
        sector = world.get_sector(0, 0)
        ok_(sector is not None)
        ttt = sector.get_terrain(0, 0)
        ok_(ttt is not None)

    def test_offmap(self):
        world = place.World(1, 1, default_terrain=terrain.Grass)
        raises_(place.OffMapError, world.get_sector, 1, 0)
        raises_(place.OffMapError, world.get_sector, 0, 1)
        raises_(place.OffMapError, world.get_sector, -1, 0)
        raises_(place.OffMapError, world.get_sector, 0, -1)

    def test_set_sector(self):
        world = place.World(2, 3, default_terrain=terrain.Grass)
        s1 = place.Sector(default_terrain=terrain.Forest)
        s2 = place.Sector(default_terrain=terrain.Boulder)
        world.set_sector(0, 0, s1)
        eq_(s1, world.get_sector(0, 0))
        world.set_sector(1, 2, s2)
        eq_(s2, world.get_sector(1, 2))
        
