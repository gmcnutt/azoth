""" Terrain map module. Includes the base TerrainMap class and some factory
functions that will create an instance from various file formats. """

import pygame
import terrain


class TerrainMap(object):
    """ The base terrain map class. Just a 2d array of terrain types. """
    def __init__(self, terrain=None):
        self.terrain = terrain

    @property
    def width(self):
        """ The width of the map. """
        return len(self.terrain[0])

    @property
    def height(self):
        """ The height of the map. """
        return len(self.terrain)

    def get(self, xloc, yloc):
        """ Get terrain at location. """
        if xloc < 0 or yloc < 0:
            raise IndexError(xloc, yloc)
        return self.terrain[yloc][xloc]

    def set(self, xloc, yloc, val):
        """ Set terrain at (xloc, yloc). """
        if xloc < 0 or yloc < 0 or xloc >= self.width:
            raise IndexError(xloc, yloc)
        return self.terrain[yloc].insert(xloc, val)


def translate_nazghul_glyph(glyph):
    """ Translate glyphs from standard palette to terrains. """
    return {'|': terrain.HeavyForest,
            't': terrain.Forest,
            '.': terrain.Grass,
            '-': terrain.Grass,
            '/': terrain.Trail,
            'r': terrain.RockWall,
            '[': terrain.CounterTop,
            ']': terrain.CounterTop,
            '~': terrain.Water,
            'b': terrain.Boulder,
            'c': terrain.CobbleStone,
            '%': terrain.Bog,
            '@': terrain.CounterTop,
            '&': terrain.FirePlace,
            'w': terrain.Window,
            }.get(glyph[0], terrain.Unmapped)


def load_from_nazghul_scm(fname):
    """ Load a TerrainMap from a nazghul .scm file. This scans for (kern-mk-map
    ...) and attempts to parse out the ASCII map representation."""

    words = open(fname).read().split()
    idx = words.index('(kern-mk-map')
    words = words[idx + 1:]
    idx = words.index('(list')
    words = words[idx + 1:]
    idx = words.index(')')
    lines = ' '.join(words[:idx - 1]).split('" "')
    tmap = []
    for line in lines:
        line = line.replace('"', '').split(' ')
        while '' in line:
            line.remove('')
        line = [translate_nazghul_glyph(g) for g in line]
        tmap.append(line)

    # Note that tmap is in row, column order. The TerrainMap class reverses
    # this in the accessors.
    return TerrainMap(terrain=tmap)

def translate_color(x):
    return {
        -16777088: terrain.Trail,
         -16776961: terrain.Grass, # fixme:Lava,
         -16760832: terrain.HeavyForest,
         -16744448: terrain.Forest,
         -16744320: terrain.Fields,
         -16711936: terrain.Grass,
         -12566464: terrain.Mountains,
         -8388608: terrain.Sea,
         -8388480: terrain.Bog,
         -8355712: terrain.Hills,
         -65536: terrain.Lake,
         -65281: terrain.Grass, #fixme: towns
         -256: terrain.Water,
         -1: terrain.Mountains #fixme: peaks
         }.get(x)

def load_from_image(fname):
    surface = pygame.image.load(fname)
    pixels = pygame.surfarray.pixels2d(surface)
    width, height = surface.get_size()
    tmap = []
    for y in xrange(height):
        line = [translate_color(pixels[x][y]) for x in xrange(width)]
        tmap.append(line)
    return TerrainMap(terrain=tmap)
    
