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

def check_index(func):
    """ Decorator to wrap a method with a coordinate check. """
    def fwrap(instance, xloc, yloc, *args):
        """ Wrapped function. """
        if not instance.onmap(xloc, yloc):
            raise IndexError(xloc, yloc)
        return func(instance, xloc, yloc, *args)
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
        return self.terrain_map[x][y]

    def set_terrain(self, x, y, terrain):
        self.terrain_map[x][y] = terrain

    def get_items(self, x, y):
        return self.items[(x, y)]

    def add_item(self, x, y, item):
        self.items[(x, y)].append(item)

    def remove_item(self, x, y, item):
        self.items[(x, y)].remove(item)

    def get_occupant(self, x, y):
        return self.occupants.get((x, y))

    def set_occupant(self, x, y, occupant):
        self.occupants[(x, y)] = occupant

    def remove_occupant(self, x, y):
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
