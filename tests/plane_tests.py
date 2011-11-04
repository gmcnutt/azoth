from nose.tools import *
from azoth.hax2 import plane, terrainmap
import cPickle
import unittest
import warnings

def test_not_there_error():
    exc = plane.NotThereError('Yonder', 4, 5, 'Sumethin')
    assert_equal('Sumethin not in Yonder at (4, 5)', '%s' % exc)

def test_already_there_error():
    exc = plane.AlreadyThereError('Yonder', 4, 5, 'Sumethin')
    assert_equal('Sumethin already in Yonder at (4, 5)', '%s' % exc)


class Plane(unittest.TestCase):

    def setUp(self):
        self.plane = plane.Plane()

    def test_plane(self):
        assert_is_not_none(self.plane)

    def test_put(self):
        self.plane.put(0, 0, 'a')
        eq_(['a'], self.plane.get(0, 0))

    def test_get_nothing(self):
        eq_([], self.plane.get(0, 0))

    def test_put_2(self):
        self.plane.put(0, 0, 'i1')
        self.plane.put(0, 0, 'i2')
        eq_(set(['i1', 'i2']), set(self.plane.get(0, 0)))

    def test_double_put_same(self):
        item = 'i1'
        self.plane.put(0, 0, item)
        assert_raises(plane.AlreadyThereError, self.plane.put, 0, 0, item)
        eq_([item], self.plane.get(0, 0))

    def test_remove(self):
        self.test_put()
        self.plane.remove(0, 0, 'a')
        eq_([], self.plane.get(0, 0))

    def test_remove_not_there(self):
        assert_raises(plane.NotThereError, self.plane.remove, 0, 0, 'a')

    def test_remove_2(self):
        self.test_put_2()
        self.plane.remove(0, 0, 'i1')
        eq_(['i2'], self.plane.get(0, 0))
        self.plane.remove(0, 0, 'i2')
        eq_([], self.plane.get(0, 0))

    def test_remove_all_of_nothing(self):
        assert_raises(KeyError, self.plane.remove_all, 0, 0)
        eq_([], self.plane.get(0, 0))

    def test_remove_all_of_2(self):
        self.test_put_2()
        self.plane.remove_all(0, 0)
        eq_([], self.plane.get(0, 0))

class Terrain(unittest.TestCase):

    def setUp(self):
        self.plane = plane.Plane(terrain={'name':'grass', 'pclass':'soft'})

    def test_get_default_terrain_only(self):
        assert_equal({'name':'grass', 'pclass':'soft'}, 
                     self.plane.get_terrain(0, 0))
    
    def test_set_get_scratch_terrain(self):
        ter = {'name':'trees', 'pclass':'brush'}
        self.plane.set_terrain(1, 1, ter)
        assert_equal(ter, self.plane.get_terrain(1, 1))

    def test_set_scratch_get_default(self):
        ter = {'name':'trees', 'pclass':'brush'}
        self.plane.set_terrain(1, 1, ter)
        assert_equal(self.plane.terrain, self.plane.get_terrain(1, 2))

    def setup_terrain(self):
        tmap1 = terrainmap.TerrainMap(terrain=[['.',  'x'],
                                               [None, None]])
        tmap2 = terrainmap.TerrainMap(terrain=[['q',  'w'],
                                               [None, 'z']])
        self.plane.push_terrain_map(0, 0, tmap2)
        self.plane.push_terrain_map(0, 0, tmap1)
        self.plane.set_terrain(0, 0, '*')

    def check_terrain(self):
        assert_equal('*', self.plane.get_terrain(0, 0)) # scratch
        assert_equal('x', self.plane.get_terrain(1, 0)) # tmap 1
        assert_equal(self.plane.terrain, self.plane.get_terrain(0, 1)) # def
        assert_equal('z', self.plane.get_terrain(1, 1)) # tmap 2
        self.plane.pop_terrain_map() # pop 1
        assert_equal('w', self.plane.get_terrain(1, 0)) # tmap 2

    def test_push_pop_terrain_map(self):
        self.setup_terrain()
        self.check_terrain()

    def test_pickle(self):
        self.setup_terrain()
        save = open('plane_tests.p', 'w')
        cPickle.dump(self.plane, save)
        save.close()
        loadfile = open('plane_tests.p')
        self.plane = cPickle.load(loadfile)
        self.check_terrain()
