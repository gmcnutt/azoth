
class BaseObject(object):
    """ A physical thing with dimensions and a location. """

    def __init__(self):
        self.mmode = None
        self.place = None
        self.x = None
        self.y = None

    @property
    def loc(self):
        """ Return (place, x, y) as a tuple.  """
        return self.place, self.x, self.y

    @loc.setter
    def loc(self, val):
        """ Assign place, x, y from a tuple. """
        self.place, self.x, self.y = val

    @property
    def xy(self):
        """ Return (x, y) as a tuple. """
        return self.x, self.y

    @xy.setter
    def xy(self, val):
        """ Assign x, y from a tuple. """
        self.x, self.y = val
    

    def __str__(self):
        if hasattr(self, 'name'):
            return self.name
        else:
            return 'pragma'


class TakesTurns(object):
    """ Mixin class for objects that take actions every turn. """

    def do_turn(self, event_loop):
        pass

    def on_turn_start(self):
        self.turn_is_done = False

    def on_turn_end(self):
        pass


