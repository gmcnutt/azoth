"""
Sprites - animations for objects.
"""
import config
import os
import pygame


class Sheet(object):
    """ An single large image composed of smaller images used for sprite
    animations. All the sprites on the sheet must be the same size. The width x
    height give the sprite dimensions in pixels. The rows x columns give the
    sheet dimensions in images. """

    def __init__(self, width, height, rows, columns, filename):
        self.rows = rows
        self.columns = columns
        self.width = width
        self.height = height
        path = os.path.join(config.SPRITE_DIRECTORY, filename)
        self.surface = pygame.image.load(path)
        self.surface.convert_alpha()

    def get_image(self, index):
        x = (index % self.columns) * self.width
        y = (index / self.columns) * self.height
        rect = pygame.Rect(x, y, self.width, self.height)
        return self.surface.subsurface(rect)


class Sprite(object):
    """ Abstract base class for all sprites. """

    def __init__(self, sheet):
        self.sheet = sheet

    @property
    def height(self):
        """ The height in pixels. """
        return self.sheet.height

    @property
    def width(self):
        """ The width in pixels. """
        return self.sheet.width

class CompositeSprite(Sprite):
    """ A sprite that is composed of multiples sprites layered on top of each
    other. The first sprite goes on the bottom, the next above that, and so
    on. The sprites should all be the same size (the first sprite sets the
    size; they will all be anchored to the top left corner)."""

    def __init__(self, sprites):
        super(CompositeSprite, self).__init__(sprites[0].sheet)
        self.sprites = sprites
        self.surface = pygame.Surface((self.width, self.height))
        self.surface.convert_alpha()

    def get_image(self, frame):
        """ Return the layered image for the given animation frame number. """
        self.surface.fill((0, 0, 0, 0))
        for sprite in self.sprites:
            self.surface.blit(sprite.get_image(frame), (0, 0))
        return self.surface
        

class AnimatedSprite(Sprite):
    """ The animation for an object. Each sprite refers to a sheet, a starting
    image and a number of sequential animation images. The facings bitmask
    indicates the number and type of facings which the sprite supports. The
    sprite's frames attribute is the image sequence."""

    # XXX: facings not handled yet
    def __init__(self, sheet, num_frames, start_frame, facings=0):
        super(AnimatedSprite, self).__init__(sheet)
        self.num_frames = num_frames
        self.facings = facings
        self.frames = []
        for frame in range(num_frames):
            index = start_frame + frame
            self.frames.append(sheet.get_image(index))
            
    def get_image(self, frame):
        """ Return the image for the given animation frame number. """
        msec = frame * config.MS_PER_FRAME
        frame = msec // 250
        return self.frames[frame % self.num_frames]


class WaveSprite(Sprite):
    """ A sprite with a single frame that animates by "rolling". """

    def __init__(self, sheet, frame):
        super(WaveSprite, self).__init__(sheet)
        self.num_frames = self.height

        # pygame's surface scroll *almost* does what I want, but it doesn't
        # wrap. So I double the image and scroll up the double.
        self.double = pygame.Surface((self.width, self.height * 2))
        self.double.convert_alpha()
        image = sheet.get_image(frame)
        self.double.blit(image, (0, 0))
        self.double.blit(image, (0, self.height))

    def get_image(self, frame):
        """ Return the image for the given animation frame number. """
        rect = pygame.Rect(0, 0, self.width, self.height)
        msec = frame * config.MS_PER_FRAME
        frame = msec // 100
        rect.y = self.height - (frame % self.height)
        return self.double.subsurface(rect)

        
class Fade(object):
    """ A shaded semi-transparent surface.  """
    def __init__(self, width, height):
        self.surf = pygame.Surface((width, height), flags=pygame.SRCALPHA)
        self.surf.convert_alpha()
        self.surf.fill(pygame.Color(0, 0, 0, 128))
