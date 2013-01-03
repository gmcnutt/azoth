""" Beings are objects with movement modes and bodies. """

import baseobject
import body


class Being(baseobject.BaseObject):
    """ Abstract base class for all beings. """
    order = 0
    def __init__(self):
        super(Being, self).__init__()
        self.controller = None

    def __lt__(self, other):
        return self.controller < other.controller


class Human(Being):
    """ A being with a humanoid body. """

    def __init__(self, name='obj'):
        super(Human, self).__init__()
        self.mmode = 'walk'
        self.name = name
        self.body = body.Humanoid()


class Troll(Being):

    def __init__(self, name='troll'):
        super(Troll, self).__init__()
        self.mmode = 'walk'
        self.name = name
        self.body = body.Humanoid()
