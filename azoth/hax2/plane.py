""" Stuff to organize space.  """

import collections

class PlaneError(Exception):
    """ Base class for all Plane exceptions. """
    def __init__(self, place):
        super(PlaneError, self).__init__()
        self.place = place
        

class AlreadyThereError(PlaneError):
    """ Can't put an object that is already there. """
    def __init__(self, place, x, y, item):
        super(AlreadyThereError, self).__init__(place)
        self.item = item
        self.x = x
        self.y = y
    def __str__(self):
        return '{} already in {} at ({}, {})'.format(self.item, self.place,
                                                     self.x, self.y)

class NotThereError(PlaneError):
    """ Can't remove an object that is not there. """
    def __init__(self, place, x, y, item):
        super(NotThereError, self).__init__(place)
        self.item = item
        self.x = x
        self.y = y
    def __str__(self):
        return '{} not in {} at ({}, {})'.format(self.item, self.place,
                                                 self.x, self.y)

class Plane(object):
    """ A plane is a limitless grid of terrain and object cells, each of which
    may hold an unlimited number of objects. The terrain is mutable. """

    def __init__(self, name='unknown place', terrain=None):
        self.name = name
        self.terrain = terrain
        self.tmaps = []
        self.scratch_terrain = {}
        self.items = collections.defaultdict(list)
        self.explored = {}

    def __iter__(self):
        """ Iterator for items on the map. """
        return iter(self.items.values())

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name or 'place'

    def put(self, x, y, item):
        """ Put an item on the place at x, y. """
        if item in self.items[(x, y)]:
            raise AlreadyThereError(self, x, y, item)
        self.items[(x, y)].insert(0, item)

    def get(self, x, y):
        """ Return the list of items at x, y. """
        return list(self.items[(x, y)])

    def remove(self, x, y, item):
        """ Remove an item from x, y. """
        try:
            self.items[(x, y)].remove(item)
        except ValueError:
            raise NotThereError(self, x, y, item)

    def remove_all(self, x, y):
        """ Remove all items from x, y. """
        del self.items[(x, y)]

    def get_explored(self, x, y):
        """ Return if the tile has been seen (for FOW). """
        return self.explored.get((x, y), False)

    def set_explored(self, x, y, val):
        """ Set the tile as explored (for FOW). """
        self.explored[(x, y)] = val

    def get_terrain(self, x, y):
        """ Return the terrain at x, y. """
        ter = self.scratch_terrain.get((x, y), None)
        if ter:
            return ter
        for offx, offy, tmap in self.tmaps:
            mapx = x - offx
            mapy = y - offy
            if mapx >= 0 and mapx < tmap.width and \
                    mapy >= 0 and mapy < tmap.height and \
                    tmap.get(mapx, mapy) is not None:
                return tmap.get(mapx, mapy)
        return self.terrain

    def set_terrain(self, x, y, val):
        """ Set the terrain at x, y. """
        self.scratch_terrain[(x, y)] = val

    def push_terrain_map(self, x, y, tmap):
        """ Push a map and anchor the upper left corner at x, y. The last map
        pushed will be the first one checked by get_terrain(). """
        self.tmaps.insert(0, (x, y, tmap))

    def pop_terrain_map(self):
        """ Pop the top map off the stack. Raises IndexError is stack is
        empty. """
        return self.tmaps.pop(0)

    # def append_terrain_map(self, x, y, tmap):
    #     self.tmaps.append((x, y, tmap))
        
    # def insert_terrain_map(self, i, x, y, tmap):
    #     self.tmaps.insert(i, (x, y, tmap))

    # def remove_terrain_map(self, x, y, tmap):
    #     self.tmaps.remove((x, y, tmap))
