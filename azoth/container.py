import baseobject

class ObjError(Exception):
    """ Base class for all Obj errors. """
    pass


class Occupied(ObjError):
    """ Location is occupied. """
    def __init__(self, prag, cont, x, y):
        super(Occupied, self).__init__()
        self.prag = prag
        self.cont = cont
        self.x = x
        self.y = y

    def __str__(self):
        return '{} already in {} at ({}, {})'.\
            format(self.prag, self.cont, self.x, self.y)


class Bag(baseobject.BaseObject):
    """ A simple container for other pragmas. """

    def __init__(self, limit=None):
        super(Bag, self).__init__()
        self.limit = limit
        self.contents = set()

    def put(self, prag):
        """ Add something to the contents. Raises IndexError if it won't
        fit. """
        if not self.will_fit(prag):
            raise IndexError()
        self.contents.add(prag)

    def remove(self, prag):
        """ Remove something from the contents. """
        self.contents.remove(prag)

    def will_fit(self, item):
        return len(self.contents) != self.limit

    def __iter__(self):
        """ Iterator to support 'for' and 'in', etc. """
        return iter(self.contents)

    def __len__(self):
        """ Number of items in the bag. """
        return len(self.contents)

    def __eq__(self, other):
        """ True iff both bags have the same contents. """
        return self.contents == other.contents

    def __ne__(self, other):
        """ True iff both bags have different contents. """
        return not self.__eq__(other)

def assert_xy_gte_0(func):
    """ Decorator to assert that x, y args to func are >= 0 """
    def wrapf(instance, x, y, *args):
        """ Wrapped function. """
        if x < 0 or y < 0:
            raise IndexError(x, y)
        return func(instance, x, y, *args)
    return wrapf

class Tray(baseobject.BaseObject):
    """ A grid of holes, each of which can hold one pragma."""

    def __init__(self, width=1, height=1):
        super(Tray, self).__init__()
        self.contents = []
        for i in range(height):
            self.contents.append([None,] * width)
        self.width = width
        self.height = height

    def available(self):
        """ Return x, y of first available empty slot. Raises IndexError if
        there aren't any. """
        try:
            return self.index(None)
        except ValueError:
            raise IndexError()

    def put(self, prag):
        """ Put into first available empty slot. Raises IndexError if it won't
        fit. """
        for row in self.contents:
            for x, col in enumerate(row):
                if col is None:
                    row[x] = prag
                    return
        raise IndexError()

    @assert_xy_gte_0
    def insert(self, x, y, prag):
        """ Put something into a tray at x, y. Raises IndexError if x, y not in
        tray dimensions or Occupied if x, y already occupied. """
        if self.contents[y][x]:
            raise Occupied(self, x, y, self.contents[y][x])
        self.contents[y][x] = prag

    def remove(self, prag):
        """ Remove something from a tray. Raises ValueError if not found. """
        x, y = self.index(prag)
        self.contents[y][x] = None

    def index(self, prag):
        """ Get the x, y location of something in the tray. Raises ValueError
        if not found. """
        for y, row in enumerate(self.contents):
            for x, col in enumerate(row):
                if col == prag:
                    return x, y
        raise ValueError(prag)

    @assert_xy_gte_0
    def access(self, x, y):
        """ Return whatever is at x, y. Raises IndexError. """
        return self.contents[y][x]

    @assert_xy_gte_0
    def delete(self, x, y):
        """ Empty x, y. Raises IndexError. """
        self.contents[y][x] = None

    def clear(self):
        """ Empty the whole tray. """
        self.contents = [[None,] * self.width] * self.height

    def __eq__(self, other):
        """ True iff both trays have the same contents. """
        return self.contents == other.contents

    def __iter__(self):
        """ Iterator to support 'for' and 'in', etc. """
        s = set()
        for row in self.contents:
            for col in row:
                if col is not None:
                    s.add(col)
        return iter(s)

    def __len__(self):
        """ Number of items in the bag. """
        count = 0
        for row in self.contents:
            for col in row:
                if col:
                    count += 1
        return count

    @property
    def full(self):
        """ True iff nothing else will fit. """
        return len(self) == self.width * self.height
