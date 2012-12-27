from nose.tools import eq_
from azoth import terrainmap
import unittest

scm_path = "../haxima/scm/"

class TestBasic(unittest.TestCase):

    def setUp(self):
        self.terrainmap = terrainmap.TerrainMap(terrain=[['.']])

    def test_dims(self):
        eq_(self.terrainmap.width, 1)
        eq_(self.terrainmap.height, 1)

    def test_set(self):
        self.terrainmap.set(0, 0, 'g')
        eq_('g', self.terrainmap.get(0, 0))

class Nazghul(unittest.TestCase):

    def test_gregors_hut(self):
        tmap = terrainmap.load_from_nazghul_scm(scm_path + "gregors-hut.scm")
        eq_(tmap.width, 32)
        eq_(tmap.height, 32)

    def test_glasdrin(self):
        tmap = terrainmap.load_from_nazghul_scm(scm_path + "glasdrin.scm")
        eq_(tmap.width, 31)
        eq_(tmap.height, 31)
