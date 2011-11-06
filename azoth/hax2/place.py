""" A map level.  """

import array
import collections
import cPickle

class PlaceError(Exception):
    """ Base exception for all place errors. """
    def __init__(self, place):
        super(PlaceError, self).__init__()
        self.place = place
        

class AlreadyThereError(PlaceError):
    """ Put failed because the item is already there.  """
    def __init__(self, place, xloc, yloc, item):
        super(AlreadyThereError, self).__init__(place)
        self.item = item
        self.xloc = xloc
        self.yloc = yloc
    def __str__(self):
        return '{} already in {} at ({}, {})'.format(self.item, self.place,
                                                     self.xloc, self.yloc)

class NotThereError(PlaceError):
    """ Remove failed because the item was not there. """
    def __init__(self, place, xloc, yloc, item):
        super(NotThereError, self).__init__(place)
        self.item = item
        self.xloc = xloc
        self.yloc = yloc
    def __str__(self):
        return '{} not in {} at ({}, {})'.format(self.item, self.place,
                                                 self.xloc, self.yloc)


class OffMapError(PlaceError):
    """ Index failed because coordinates not on map.  """
    def __init__(self, x, y, place):
        super(OffMapError, self).__init__(place)
        self.x = x
        self.y = y
    def __str__(self):
        return '({}, {}) not on {} {}'.format(self.x, self.y, type(self.place),
                                              self.place.name)


def check_index(func):
    """ Decorator to wrap a method with a coordinate check. """
    def fwrap(instance, x, y, *args):
        """ Wrapped function. """
        if not instance.onmap(x, y):
            raise OffMapError(x, y, instance)
        return func(instance, x, y, *args)
    return fwrap


class Place(object):
    """ A place has a map of the terrain in every cell and keeps track of
    object xloc, ylocations. """

    def __init__(self, name=None, terrain=None, items=None):
        self.name = name
        self.terrain = terrain
        self.items = items or collections.defaultdict(list)

    @property
    def width(self):
        """ Width of the place in tiles. """
        return self.terrain.width

    @property
    def height(self):
        """ Height of the place in tiles. """
        return self.terrain.height

    def onmap(self, xloc, yloc):
        """ Return True iff the xloc, ylocation is on the map. """
        return xloc >= 0 and yloc >= 0 and xloc < self.width and \
            yloc < self.height

    @check_index
    def put(self, xloc, yloc, item):
        """ Put an item on the place at xloc, yloc. """
        if item in self.items[(xloc, yloc)]:
            raise AlreadyThereError(self, xloc, yloc, item)
        self.items[(xloc, yloc)].append(item)

    @check_index
    def get(self, xloc, yloc):
        """ Return the list of items at xloc, yloc. """
        return list(self.items[(xloc, yloc)])

    @check_index
    def remove(self, xloc, yloc, item):
        """ Remove an item from xloc, yloc. """
        try:
            self.items[(xloc, yloc)].remove(item)
        except ValueError:
            raise NotThereError(self, xloc, yloc, item)

    @check_index
    def remove_all(self, xloc, yloc):
        """ Remove all items from xloc, yloc. """
        del self.items[(xloc, yloc)]


class Sector(object):
    """ Fixed-size chunk of map, meant to be stitched together with other
    sectors to form a whole map. """

    width = 31
    height = 31

    def __init__(self, name=None, default_terrain=None):
        self.name = name
        self.terrain_map = []
        for column in range(self.width):
            self.terrain_map.append([default_terrain,] * self.height)
        self.items = collections.defaultdict(list)
        self.occupants = {}
        self.explored = []
        for x in range(self.width):
            self.explored.append(array.array('b', '\0' * self.height))

    def get_terrain(self, x, y):
        """ Return terrain at x, y. """
        return self.terrain_map[x][y]

    def set_terrain(self, x, y, terrain):
        """ Set terrain at x, y. """
        self.terrain_map[x][y] = terrain

    def get_items(self, x, y):
        """ Return a list of items at x, y. """
        return self.items[(x, y)]

    def add_item(self, x, y, item):
        """ Add an item at x, y. """
        self.items[(x, y)].append(item)

    def remove_item(self, x, y, item):
        """ Remove an item at x, y. """
        self.items[(x, y)].remove(item)

    def get_occupant(self, x, y):
        """ Get the occupant at x,y, or None. """
        return self.occupants.get((x, y))

    def set_occupant(self, x, y, occupant):
        """ Set the occupant at x, y. """
        self.occupants[(x, y)] = occupant

    def remove_occupant(self, x, y):
        """ Remove the occupant at x, y. """
        del self.occupants[(x, y)]

    def get_explored(self, x, y):
        """ Return if the tile has been seen (for FOW). """
        return self.explored[x][y]

    def set_explored(self, x, y, val):
        """ Set the tile as explored (for FOW). """
        self.explored[x][y] = val

    def save(self, savefile):
        """ Save to an open file. """
        cPickle.dump(self, savefile)

    @staticmethod
    def load(loadfile):
        """ Load from an open file. """
        return cPickle.load(loadfile)


class World(object):
    """ 
    A plane of sectors.

    Lazily creates sectors when none specified.
    """
    def __init__(self, width, height, name=None, default_terrain=None):
        self.width = width
        self.height = height
        self.name = name
        self.default_terrain = default_terrain
        self.sectors = []
        for x in range(width):
            self.sectors.append([None,] * height)

    def onmap(self, x, y):
        """ Return True iff x, y is on the map. """
        return x >= 0 and y >= 0 and x < self.width and y < self.height
        
    @check_index
    def get_sector(self, x, y):
        """ Return the sector at x, y. If there is no sector create one.""" 
        sector = self.sectors[x][y]
        if sector is None:
            sector = Sector(name='auto-%d-%d'%(x, y), 
                            default_terrain=self.default_terrain)
            self.set_sector(x, y, sector)
        return sector

    @check_index
    def set_sector(self, x, y, sector):
        """ Set the sector at x, y  """
        self.sectors[x][y] = sector
