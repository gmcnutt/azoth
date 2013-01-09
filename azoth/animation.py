import config
import os
import pygame


_image_cache = {}


def _image_load(filename):
    """ Load an image from a file and return it as a pygame surface compatible
    with the main display surface. """
    path = os.path.join(config.SPRITE_DIRECTORY, filename)
    surface = pygame.image.load(path)
    surface.convert_alpha()
    return surface


def _get_image(filename):
    """ Fetch an image from the cache, adding it to the cache if necessary. """
    global _image_cache
    if filename not in _image_cache:
        _image_cache[filename] = _image_load(filename)
    return _image_cache[filename]


class Sequence(object):
    """ A sequence of frames. """
    def __init__(self, frames=None):
        self.frames = frames

    def __getitem__(self, index):
        return self.frames[index]
        
    def __len__(self):
        return len(self.frames)


class Loop(Sequence):
    """ A sequence of frames that loops around. """
    def __init__(self, *args, **kwargs):
        super(Loop, self).__init__(*args, **kwargs)

    def __getitem__(self, index):
        return self.frames[index % len(self.frames)]


class Frame(object):
    """ An image that is part of an animation. This includes how long in
    seconds the image should be maintained and at what offset from the origin
    it should be painted."""
    def __init__(self, filename, duration, offset=None):
        self._image = None
        if isinstance(filename, (list, tuple)):
            self.filename = os.path.join(*filename)
        else:
            self.filename = filename
        self.duration = duration
        self.offset = offset or (0, 0)

    @property
    def image(self):
        if self._image is None:
            self._image = _get_image(self.filename)
        return self._image
