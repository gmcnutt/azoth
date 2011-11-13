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
    def __init__(self, place, x, y):
        super(OffMapError, self).__init__(place)
        self.x = x
        self.y = y
    def __str__(self):
        return '({}, {}) not in {} {}'.format(self.x, self.y,
                                              self.place.__class__.__name__,
                                              self.place.name)


def check_index(func):
    """ Decorator to wrap a method with a coordinate check. """
    def fwrap(instance, x, y, *args):
        """ Wrapped function. """
        if not instance.onmap(x, y):
            raise OffMapError(instance, x, y)
        return func(instance, x, y, *args)
    return fwrap


class Place(object):
    """ A place is a fixed-size grid that holds terrain, items and beings. """

    def __init__(self, width, height, name=None, default_terrain=None):
        self.width = width
        self.height = height
        self.name = name
        self.terrain_map = []
        for column in range(self.width):
            self.terrain_map.append([default_terrain,] * self.height)
        self.items = collections.defaultdict(list)
        self.occupants = {}
        self.explored = []
        for x in range(self.width):
            self.explored.append(array.array('b', '\0' * self.height))

    def onmap(self, xloc, yloc):
        """ Return True iff the x, y is on the map. This is used by the
        check_index decorator. """
        return xloc >= 0 and yloc >= 0 and xloc < self.width and \
            yloc < self.height

    @check_index
    def blit_terrain_map(self, offx, offy, tmap):
        """ Copy a TerrainMap over the sector at top left offset x, y.  """
        dest_y = offy
        src_y = 0
        while dest_y < self.height and src_y < tmap.height:
            dest_x = offx
            src_x = 0
            while dest_x < self.width and src_x < tmap.width:
                self.set_terrain(dest_x, dest_y, tmap.get(src_x, src_y))
                dest_x += 1
                src_x += 1
            dest_y += 1
            src_y += 1

    @check_index
    def get_terrain(self, x, y):
        """ Return terrain at x, y. """
        return self.terrain_map[x][y]

    @check_index
    def set_terrain(self, x, y, terrain):
        """ Set terrain at x, y. """
        self.terrain_map[x][y] = terrain

    @check_index
    def get_items(self, x, y):
        """ Return a list of items at x, y. """
        return self.items[(x, y)]

    @check_index
    def add_item(self, x, y, item):
        """ Add an item at x, y. """
        if item in self.items[(x, y)]:
            raise AlreadyThereError(self, x, y, item)
        self.items[(x, y)].append(item)

    @check_index
    def remove_item(self, x, y, item):
        """ Remove an item at x, y. """
        try:
            self.items[(x, y)].remove(item)
        except ValueError:
            raise NotThereError(self, x, y, item)

    @check_index
    def get_occupant(self, x, y):
        """ Get the occupant at x,y, or None. """
        return self.occupants.get((x, y))

    @check_index
    def set_occupant(self, x, y, occupant):
        """ Set the occupant at x, y. """
        self.occupants[(x, y)] = occupant

    @check_index
    def remove_occupant(self, x, y):
        """ Remove the occupant at x, y. """
        try:
            del self.occupants[(x, y)]
        except KeyError:
            raise NotThereError(self, x, y, None)

    @check_index
    def remove_all(self, x, y):
        """ Remove all items and any occupant at x, y. """
        if (x, y) in self.items:
            del self.items[(x, y)]
        if (x, y) in self.occupants:
            del self.occupants[(x, y)]

    @check_index
    def get_explored(self, x, y):
        """ Return if the tile has been seen (for FOW). """
        return self.explored[x][y]

    @check_index
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


class Sector(Place):
    """ Fixed-size chunk of map, meant to be stitched together with other
    sectors to form a whole map. """

    def __init__(self, **kwargs):
        # XXX: move 31 to config.py
        super(Sector, self).__init__(width=31, height=31, **kwargs)



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
        """ Return the sector at x, y (in sector, not cell, coordinates). If
        there is no sector create one.""" 
        sector = self.sectors[x][y]
        if sector is None:
            sector = Sector(name='auto-%d-%d'%(x, y), 
                            default_terrain=self.default_terrain)
            self.set_sector(x, y, sector)
        return sector

    @check_index
    def set_sector(self, x, y, sector):
        """ Set the sector at x, y (in sector coordinates). """
        self.sectors[x][y] = sector
