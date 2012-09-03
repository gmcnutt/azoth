class Pragma(object):
    """ A pragma is a physical thing with dimensions and a location. """

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

    def __str__(self):
        if hasattr(self, 'name'):
            return self.name
        else:
            return 'pragma'


class Human(Pragma):
    mmode = 'walk'
    def __init__(self, name):
        super(Human, self).__init__()
        self.name = name
