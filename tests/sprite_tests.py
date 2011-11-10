import unittest
from tools import *
from azoth import sprites
import pygame

class SpriteTest(unittest.TestCase):

    def setUp(self):
        pygame.init()
        self.screen = pygame.display.set_mode((320, 240), 0)
        self.prompt_all=False

    def prompt(self):
        if not self.prompt_all:
            return
        event = pygame.event.wait()
        while event.type != pygame.KEYDOWN:
            event = pygame.event.wait()

    def test_32x32x1x1_1x1(self):
        sheet = sprites.Sheet(32, 32, 1, 1, 'shapes.png')
        sprite = sprites.Sprite(sheet, 1, 0, False, 0)
        self.screen.blit(sprite.frames[0], (0, 0))
        pygame.display.flip()
        self.prompt()

    def test_32x32x16x16_1x2(self):
        sheet = sprites.Sheet(32, 32, 16, 16, 'shapes.png')
        sprite = sprites.Sprite(sheet, 1, 2, False, 0)
        self.screen.blit(sprite.frames[0], (0, 0))
        pygame.display.flip()
        self.prompt()

    def test_32x32x16x16_1x15(self):
        sheet = sprites.Sheet(32, 32, 16, 16, 'shapes.png')
        sprite = sprites.Sprite(sheet, 1, 15, False, 0)
        self.screen.blit(sprite.frames[0], (0, 0))
        pygame.display.flip()
        self.prompt()

    def test_32x32x16x16_1x16(self):
        sheet = sprites.Sheet(32, 32, 16, 16, 'shapes.png')
        sprite = sprites.Sprite(sheet, 1, 16, False, 0)
        print(sprite.frames[0].get_offset())
        self.screen.blit(sprite.frames[0], (0, 0))
        pygame.display.flip()
        self.prompt()
