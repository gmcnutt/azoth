import cPickle
import unittest
from tools import *
from azoth import sprites, terrain
import pygame

class BaseTest(unittest.TestCase):

    prompt_all = False

    def setUp(self):
        pygame.init()
        self.screen = pygame.display.set_mode((640, 480), 0)
        self.sheet = sprites.Sheet(32, 32, 16, 16, 'shapes.png')
        self.clock = pygame.time.Clock()

    def prompt(self):
        if not self.prompt_all:
            return
        event = pygame.event.wait()
        while event.type != pygame.KEYDOWN:
            event = pygame.event.wait()

    def animate(self, sprite, rows=1, columns=1):
        while True:
            for i in range(sprite.num_frames):
                for row in range(rows):
                    y = row * sprite.height
                    for column in range(columns):
                        x = column * sprite.width
                        self.screen.blit(sprite.get_image(i), (x, y))
                pygame.display.flip()
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        return
                self.clock.tick(10)


class AnimatedSpriteTest(BaseTest):

    def test_32x32x1x1_1x1(self):
        sheet = sprites.Sheet(32, 32, 1, 1, 'shapes.png')
        sprite = sprites.AnimatedSprite(sheet, 1, 0)
        self.screen.blit(sprite.get_image(0), (0, 0))
        pygame.display.flip()
        self.prompt()

    def test_32x32x16x16_1x2(self):
        sprite = sprites.AnimatedSprite(self.sheet, 1, 2)
        self.screen.blit(sprite.get_image(0), (0, 0))
        pygame.display.flip()
        self.prompt()

    def test_32x32x16x16_1x15(self):
        sprite = sprites.AnimatedSprite(self.sheet, 1, 15)
        self.screen.blit(sprite.get_image(0), (0, 0))
        pygame.display.flip()
        self.prompt()

    def test_32x32x16x16_1x16(self):
        sprite = sprites.AnimatedSprite(self.sheet, 1, 16)
        self.screen.blit(sprite.get_image(0), (0, 0))
        pygame.display.flip()
        self.prompt()


class WaveSpriteTest(BaseTest):
    
    def test_water(self):
        sprite = sprites.WaveSprite(self.sheet, 0)
        if self.prompt_all:
            self.animate(sprite, rows=3, columns=3)

class SaveLoadTest(BaseTest):

    #prompt_all = True

    def setUp(self):
        super(SaveLoadTest, self).setUp()
        self.sprites = {'ship':sprites.AnimatedSprite(self.sheet, 1, 16)}
        self.reverse_sprites = dict(zip(self.sprites.values(), 
                                        self.sprites.keys()))

    def save(self, sprite):
        sfile = open('sprite_tests.p', 'w')
        p = cPickle.Pickler(sfile)
        p.persistent_id = self.persistent_id
        p.dump(sprite)

    def load(self):
        lfile = open('sprite_tests.p')
        p = cPickle.Unpickler(lfile)
        p.persistent_load = self.persistent_load
        return p.load()

    def persistent_id(self, obj):
        try: return self.reverse_sprites.get(obj)
        except TypeError: return None

    def persistent_load(self, persid):
        if persid not in self.sprites:
            raise cPickle.UnpicklingError('invalid id:{}'.format(persid))
        return self.sprites.get(persid)

    def test_save_load(self):
        self.save(self.sprites['ship'])
        sprite = self.load()
        self.screen.blit(sprite.get_image(0), (0, 0))
        pygame.display.flip()
        self.prompt()

    def test_referent_save_load(self):
        ter = terrain.Terrain('test', 'rock', self.sprites['ship'], True)
        self.save(ter)
        ter = self.load()
        self.screen.blit(ter.sprite.get_image(0), (0, 0))
        pygame.display.flip()
        self.prompt()
