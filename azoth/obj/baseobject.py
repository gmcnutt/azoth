import collections


class BaseObject(object):
    """ A physical thing with dimensions and a location. """

    def __init__(self):
        self.mmode = None
        self.place = None
        self.x = None
        self.y = None
        self.hooks = collections.defaultdict(list)

    @property
    def loc(self):
        """ Return (place, x, y) as a tuple.  """
        return self.place, self.x, self.y

    @loc.setter
    def loc(self, val):
        """ Assign place, x, y from a tuple. """
        self.place, self.x, self.y = val
        self.fire('move')

    @property
    def xy(self):
        """ Return (x, y) as a tuple. """
        return self.x, self.y

    @xy.setter
    def xy(self, val):
        """ Assign x, y from a tuple. """
        self.x, self.y = val
        self.fire('move')
    
    def __str__(self):
        if hasattr(self, 'name'):
            return self.name
        else:
            return 'pragma'

    def on(self, event, callback):
        """ Add a callback on an event hook. """
        self.hooks[event].append(callback)

    def un(self, event, callback):
        """ Remove a callback from an event hook. """
        index = self.hooks[event].index(callback)
        del self.hooks[event][index]

    def fire(self, event):
        for callback in self.hooks[event]:
            callback()

    def __getstate__(self):
        """ Override to prevent pickling the hooks. """
        odict = self.__dict__.copy()
        del odict['hooks']
        return odict

    def __setstate__(self, odict):
        """ Override to prevent pickling the hooks. """
        self.__dict__.update(odict)
        self.hooks = collections.defaultdict(list)


class TakesTurns(object):
    """ Mixin class for objects that take actions every turn. """

    def do_turn(self, event_loop):
        pass

    def on_turn_start(self):
        self.turn_is_done = False

    def on_turn_end(self):
        pass


