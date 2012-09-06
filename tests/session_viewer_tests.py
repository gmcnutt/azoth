import unittest
from tools import *
from azoth import controller, event, executor, gui, place, session, sprite, \
    terrain, terrainmap
from azoth.obj import being, weapon
import pygame

scm_path = "../haxima/scm/"


class SessionViewerTest(unittest.TestCase):

    def setUp(self):
        pygame.init()
        pygame.display.set_mode((320, 240), 0)
        sheet = sprite.Sheet(32, 32, 16, 16, 'shapes.png')
        being.Human.sprite = sprite.AnimatedSprite(sheet, 4, 192)
        terrain.Grass.sprite = sprite.AnimatedSprite(sheet, 1, 4)
        terrain.CobbleStone.sprite = sprite.AnimatedSprite(sheet, 1, 22)
        terrain.Ankh.sprite = sprite.AnimatedSprite(sheet, 1, 61)
        self.session = session.Session()
        self.session.player = being.Human()
        self.session.player.controller = controller.Player(self.session.player,
                                                           self.session)
        self.session.world = place.Sector(name='gh', 
                                          default_terrain=terrain.Grass)
        self.session.hax2.put_being_on_map(self.session.player, 
                                           self.session.world, 0, 0)
        self.viewer = gui.SessionViewer(self.session)
        self.prompt_all = False

    def prompt(self):
        event = pygame.event.wait()
        while event.type != pygame.KEYDOWN:
            event = pygame.event.wait()

    def show(self, prompt=False):
        self.viewer.render()
        if self.prompt_all or prompt:
            self.prompt()

    def sendkey(self, key):
        """ Curried wrapper to send a key event to the session viewer. """
        try:
            self.session.player.controller.on_keypress(key)
        except event.Handled:
            pass

    def test_scroll(self):
        self.session.world.set_terrain(1, 0, terrain.CobbleStone)
        self.session.world.set_terrain(0, 1, terrain.CobbleStone)
        self.session.world.set_terrain(29, 0, terrain.CobbleStone)
        self.session.world.set_terrain(30, 1, terrain.CobbleStone)
        self.session.world.set_terrain(30, 29, terrain.CobbleStone)
        self.session.world.set_terrain(29, 30, terrain.CobbleStone)
        self.session.world.set_terrain(0, 29, terrain.CobbleStone)
        self.session.world.set_terrain(1, 30, terrain.CobbleStone)
        for x in xrange(self.session.world.width + 1):
            self.sendkey(pygame.K_RIGHT)
            self.viewer.render()
        eq_(self.session.player.xy, (self.session.world.width - 1, 0))
        self.show()
        for y in xrange(self.session.world.height + 1):
            self.sendkey(pygame.K_DOWN)
            self.viewer.render()
        self.show()
        for x in xrange(self.session.world.width + 1):
            self.sendkey(pygame.K_LEFT)
            self.viewer.render()
        self.show()
        for y in xrange(self.session.world.height + 1):
            self.sendkey(pygame.K_UP)
            self.viewer.render()
        self.show()

    def test_impassability(self):
        self.session.world.set_terrain(1, 0, terrain.Ankh)
        self.sendkey(pygame.K_RIGHT)
        eq_(self.session.player.xy, (0, 0))
        
    def test_get(self):
        sword = weapon.Sword()
        self.session.hax2.put_item_on_map(sword, self.session.world, 0, 0)
        eq_(sword.loc, (self.session.world, 0, 0))
        self.sendkey(pygame.K_g)
        eq_(sword.loc, (None, None, None))
        ok_(self.session.player.body.has(sword))

    def test_drop(self):
        sword = weapon.Sword()
        self.session.player.body.put(sword)
        self.sendkey(pygame.K_d)
        eq_(sword.loc, (self.session.world, 0, 0))
        ok_(not self.session.player.body.has(sword))
