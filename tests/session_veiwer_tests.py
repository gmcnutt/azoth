import unittest
from tools import *
from azoth import executor, gui, human, place, session, sprites, terrain, terrainmap
import pygame

scm_path = "../haxima/scm/"


class SessionViewerTest(unittest.TestCase):

    def setUp(self):
        pygame.init()
        pygame.display.set_mode((320, 240), 0)
        sheet = sprites.Sheet(32, 32, 16, 16, 'shapes.png')
        human.Human.sprite = sprites.AnimatedSprite(sheet, 4, 192)
        terrain.Grass.sprite = sprites.AnimatedSprite(sheet, 1, 4)
        terrain.CobbleStone.sprite = sprites.AnimatedSprite(sheet, 1, 22)
        terrain.Ankh.sprite = sprites.AnimatedSprite(sheet, 1, 61)
        self.session = session.Session()
        self.session.player = human.Human()
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
            self.viewer.on_keypress(pygame.event.Event(pygame.USEREVENT, 
                                                       key=pygame.K_RIGHT))
            self.viewer.render()
        eq_(self.session.player.xy, (self.session.world.width - 1, 0))
        self.show()
        for y in xrange(self.session.world.height + 1):
            self.viewer.on_keypress(pygame.event.Event(pygame.USEREVENT, 
                                                       key=pygame.K_DOWN))
            self.viewer.render()
        self.show()
        for x in xrange(self.session.world.width + 1):
            self.viewer.on_keypress(pygame.event.Event(pygame.USEREVENT, 
                                                       key=pygame.K_LEFT))
            self.viewer.render()
        self.show()
        for y in xrange(self.session.world.height + 1):
            self.viewer.on_keypress(pygame.event.Event(pygame.USEREVENT, 
                                                       key=pygame.K_UP))
            self.viewer.render()
        self.show()

    def test_impassability(self):
        self.session.world.set_terrain(1, 0, terrain.Ankh)
        self.viewer.on_keypress(pygame.event.Event(pygame.USEREVENT, 
                                                   key=pygame.K_RIGHT))
        eq_(self.session.player.xy, (0, 0))
        
