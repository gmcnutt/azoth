""" Transactions: hooked functions that modify more than one object. """

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
        occupant = pla.get_occupant(x, y)
        if occupant is not None:
            raise Occupied(occupant, pla, x, y)

    def assert_put_in_bag_ok(self, item, bag):
        if not bag.will_fit(item):
            raise WontFitError(item, bag)

    def assert_remove_ok(self, obj):
        """ Checks that removal is not forbidden.  """
        pass

    def on_put_occupant(self, obj):
        """ Apply any effects that are triggered by putting an occupant on the
        map. For example, terrain effects are applied here.  """        
        terrain = obj.place.get_terrain(obj.x, obj.y)
        # XXX: get rid of hasattr
        if hasattr(terrain, 'effect') and terrain.effect is not None:
            terrain.effect(obj)


class Executor(object):
    """ Runs transactions, invoking hooks. """

    def __init__(self, rules):
        self.rules = rules

    def move_item_from_map_to_bag(self, item, bag):
        """ Remove item from map, put it in the bag. """
        self.rules.assert_put_in_bag_ok(item, bag)
        self.remove_item_from_map(item)
        bag.put(item)
            
    def put_item_on_map(self, obj, pla, x, y):
        """ Put object in place at (xloc, yloc). """
        self.rules.assert_passable(obj, pla, x, y)
        loc = (pla, x, y)
        pla.add_item(x, y, obj)
        obj.loc = loc

    def put_being_on_map(self, obj, pla, x, y):
        """ Put object in place at (xloc, yloc). """
        # checks
        self.rules.assert_unoccupied(pla, x, y)
        self.rules.assert_passable(obj, pla, x, y)
        # commit
        loc = (pla, x, y)
        pla.set_occupant(x, y, obj)
        obj.loc = loc
        # hooks
        self.rules.on_put_occupant(obj)

    def remove_being_from_map(self, obj):
        """ Remove the object from its current place.  """
        self.rules.assert_remove_ok(obj)
        obj.place.remove_occupant(obj.x, obj.y)
        obj.loc = (None, None, None)

    def remove_item_from_map(self, obj):
        """ Remove the object from its current place.  """
        self.rules.assert_remove_ok(obj)
        obj.place.remove_item(obj.x, obj.y, obj)
        obj.loc = (None, None, None)

    def move_being_on_map(self, obj, dx, dy):
        """ Move the object in its current place one space in the given
        direction. If it raises an exception nothing will be changed. """
        newx = obj.x + dx
        newy = obj.y + dy
        # checks
        self.rules.assert_remove_ok(obj)
        self.rules.assert_unoccupied(obj.place, newx, newy)
        self.rules.assert_passable(obj, obj.place, newx, newy)
        # commit
        obj.place.remove_occupant(obj.x, obj.y)
        obj.place.set_occupant(newx, newy, obj)
        obj.loc = (obj.place, newx, newy)
        # hooks
        self.rules.on_put_occupant(obj)
        
    def rotate_beings_on_map(self, *objs):
        """ Rotate locations. """
        # checks
        for i, cur in enumerate(objs):
            prev = objs[i - 1]
            self.rules.assert_remove_ok(cur)
            self.rules.assert_passable(prev, *cur.loc)
        # commit
        lastloc = objs[-1].loc
        for i, cur in enumerate(objs):
            prev = objs[i - 1]
            cur.place.remove_occupant(cur.x, cur.y)
            cur.place.set_occupant(cur.x, cur.y, prev)
            tmploc = cur.loc
            cur.loc = lastloc
            lastloc = tmploc
        # hooks
        for obj in objs:
            self.rules.on_put_occupant(obj)
