import unittest
from tools import *
from azoth import sprites
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
        print(sprite.get_image(0).get_offset())
        self.screen.blit(sprite.get_image(0), (0, 0))
        pygame.display.flip()
        self.prompt()


class WaveSpriteTest(BaseTest):
    
    def test_water(self):
        sprite = sprites.WaveSprite(self.sheet, 0)
        if self.prompt_all:
            self.animate(sprite, rows=3, columns=3)
