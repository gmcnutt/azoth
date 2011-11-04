""" Rule evaluator for the game. """

import collections


PASS_NONE = -1
PASS_DEF = 0

class RuleError(Exception):
    """ Base class for Rule exceptions. """
    pass

class Impassable(RuleError):
    """ Location is impassable. """
    def __init__(self, obj, blocker, place, x, y):
        super(Impassable, self).__init__()
        self.obj = obj
        self.blocker = blocker
        self.place = place
        self.x = x
        self.y = y

    def __str__(self):
        return '{} blocked by {} in {} at ({}, {})'.\
            format(self.obj, self.blocker, self.place, self.x, self.y)

class Occupied(RuleError):
    """ Location is occupied. """
    def __init__(self, obj, place, x, y):
        super(Occupied, self).__init__()
        self.obj = obj
        self.place = place
        self.x = x
        self.y = y

    def __str__(self):
        return '{} already in {} at ({}, {})'.\
            format(self.obj, self.place, self.x, self.y)

class WontFitError(RuleError):

    """ Item won't fit in the container. """
    def __init__(self, item, container):
        super(WontFitError, self).__init__()
        self.item = item
        self.container = container

    def __str__(self):
        return "{} won't fit in {}".format(self.item, self.container)



class Ruleset(object):
    """ The ruleset registers transaction hooks that enforce the rules that
    affect the legality and outcomes of basic things like movement. """

    def __init__(self):
        self.pmap = collections.defaultdict(dict)

    def set_passability(self, mmode, pclass, val):
        """ Set passability for mmode over pclass. """
        self.pmap[mmode][pclass] = val

    def assert_passable(self, obj, pla, x, y):
        """ Raise Impassable if terrain at loc is impassable to obj. """
        ter = pla.get_terrain(x, y)
        penalty = self.pmap.get(obj.mmode, {}).get(ter.pclass, PASS_DEF)
        if penalty == PASS_NONE:
            raise Impassable(obj, ter.name, pla, x, y)

    @staticmethod
    def assert_unoccupied(pla, x, y):
        """ Raises Occupied if the location has an occupant.  """
        occs = [x for x in pla.get(x, y) if getattr(x, 'occupant', False)]
        if occs:
            raise Occupied(occs[0], pla, x, y)

    def assert_put_ok(self, obj, pla, x, y):
        """ Check passability and occupancy. """
        if getattr(obj, 'occupant', False):
            Ruleset.assert_unoccupied(pla, x, y)
        self.assert_passable(obj, pla, x, y)

    def assert_put_in_bag_ok(self, item, bag):
        if not bag.will_fit(item):
            raise WontFitError(item, bag)

    def assert_rotate_ok(self, obj, pla, x, y):
        """ Like assert_put_ok but ignore possibility on the assumption that
        occupants will be rotated around. """
        self.assert_passable(obj, pla, x, y)

    def assert_remove_ok(self, obj):
        """ Checks that removal is not forbidden.  """
        pass
