from nose.tools import *
from azoth.hax2 import place, terrainmap
import unittest
import warnings

def test_not_there_error():
    exc = place.NotThereError('Yonder', 4, 5, 'Sumethin')
    assert_equal('Sumethin not in Yonder at (4, 5)', '%s' % exc)

def test_already_there_error():
    exc = place.AlreadyThereError('Yonder', 4, 5, 'Sumethin')
    assert_equal('Sumethin already in Yonder at (4, 5)', '%s' % exc)


class Place(unittest.TestCase):

    def setUp(self):
        self.place = place.Place(terrain=terrainmap.TerrainMap([['.']]))

    def test_place(self):
        assert_is_not_none(self.place)

    def test_put(self):
        self.place.put(0, 0, 'a')
        eq_(['a'], self.place.get(0, 0))

    def test_get_nothing(self):
        eq_([], self.place.get(0, 0))

    def test_put_2(self):
        self.place.put(0, 0, 'i1')
        self.place.put(0, 0, 'i2')
        eq_(set(['i1', 'i2']), set(self.place.get(0, 0)))

    def test_double_put_same(self):
        item = 'i1'
        self.place.put(0, 0, item)
        assert_raises(place.AlreadyThereError, self.place.put, 0, 0, item)
        eq_([item], self.place.get(0, 0))

    def test_remove(self):
        self.test_put()
        self.place.remove(0, 0, 'a')
        eq_([], self.place.get(0, 0))

    def test_remove_not_there(self):
        assert_raises(place.NotThereError, self.place.remove, 0, 0, 'a')

    def test_remove_2(self):
        self.test_put_2()
        self.place.remove(0, 0, 'i1')
        eq_(['i2'], self.place.get(0, 0))
        self.place.remove(0, 0, 'i2')
        eq_([], self.place.get(0, 0))

    def test_remove_all_of_nothing(self):
        assert_raises(KeyError, self.place.remove_all, 0, 0)
        eq_([], self.place.get(0, 0))

    def test_remove_all_of_2(self):
        self.test_put_2()
        self.place.remove_all(0, 0)
        eq_([], self.place.get(0, 0))

    def test_put_offmap(self):
        assert_raises(IndexError, self.place.put, -1,  0, 'a')
        assert_raises(IndexError, self.place.put,  0, -1, 'a')
        assert_raises(IndexError, self.place.put, 10,  0, 'a')
        assert_raises(IndexError, self.place.put,  0, 10, 'a')
