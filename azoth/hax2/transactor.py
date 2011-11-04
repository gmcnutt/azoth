""" Transactions: hooked functions that modify more than one object. """

import collections


class Transactor(object):
    """ Runs transactions, invoking hooks. """

    def __init__(self, rules):
        self.rules = rules

    def move_from_map_to_bag(self, item, bag):
        """ Remove item from map, put it in the bag. """
        self.rules.assert_put_in_bag_ok(item, bag)
        self.remove_from_map(item)
        bag.put(item)
            

    def put_on_map(self, obj, pla, x, y):
        """ Put object in place at (xloc, yloc). """
        self.rules.assert_put_ok(obj, pla, x, y)
        loc = (pla, x, y)
        pla.put(x, y, obj)
        obj.loc = loc

    def remove_from_map(self, obj):
        """ Remove the object from its current place.  """
        self.rules.assert_remove_ok(obj)
        obj.place.remove(obj.x, obj.y, obj)
        obj.loc = (None, None, None)

    def move_on_map(self, obj, direction=None):
        """ Move the object in its current place one space in the given
        direction. If it raises an exception nothing will be changed. """
        dx, dy = {'north'    :( 0, -1),
                  'northeast':( 1, -1),
                  'east'     :( 1,  0),
                  'southeast':( 1,  1),
                  'south'    :( 0,  1),
                  'southwest':(-1,  1),
                  'west'     :(-1,  0),
                  'northwest':(-1, -1)}[direction]
        newx = obj.x + dx
        newy = obj.y + dy
        # pre-move checks
        self.rules.assert_remove_ok(obj)
        self.rules.assert_put_ok(obj, obj.place, newx, newy)
        # commit transaction
        obj.place.remove(obj.x, obj.y, obj)
        obj.place.put(newx, newy, obj)
        obj.loc = (obj.place, newx, newy)


    def rotate_on_map(self, *objs):
        """ Rotate locations. """
        # pre-checks
        for i, cur in enumerate(objs):
            prev = objs[i - 1]
            self.rules.assert_remove_ok(cur)
            self.rules.assert_rotate_ok(prev, *cur.loc)
        # commit
        lastloc = objs[-1].loc
        for i, cur in enumerate(objs):
            prev = objs[i - 1]
            cur.place.remove(cur.x, cur.y, cur)
            cur.place.put(cur.x, cur.y, prev)
            tmploc = cur.loc
            cur.loc = lastloc
            lastloc = tmploc

