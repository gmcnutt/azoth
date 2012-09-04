from tools import *
from azoth import place, session, terrain, terrainmap
import azoth.obj as obj
import unittest

class SessionTest(unittest.TestCase):

    def setUp(self):
        self.session = session.Session()

    def save(self):
        self.session.save('session_tests.p')

    def load(self):
        self.session = session.load('session_tests.p')

    def test_basic(self):
        self.session.player = 'player'
        self.save()
        self.load()
        eq_(self.session.player, 'player')

    def test_player_loc(self):
        tmap = terrainmap.load_from_nazghul_scm('gregors-hut.scm')
        self.session.player = obj.Obj()
        self.session.player.glyph = '@'
        self.session.player.name = 'player'
        self.session.world = place.Sector(name='gh', 
                                          default_terrain=terrain.Grass)
        self.session.world.blit_terrain_map(0, 0, tmap)
        self.session.player.mmode = 'walk'
        self.session.hax2.put_being_on_map(self.session.player, 
                                           self.session.world, 10, 10)
        eq_(self.session.player.place, self.session.world)
        self.save()
        self.load()

