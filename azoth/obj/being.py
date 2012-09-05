""" Beings are objects with movement modes and bodies. """

import baseobject
import body


class Human(baseobject.BaseObject):
    """ A being with a humanoid body. """

    def __init__(self, name='obj'):
        super(Human, self).__init__()
        self.mmode = 'walk'
        self.name = name
        self.body = body.Humanoid()

class Troll(baseobject.BaseObject):

    def __init__(self, name='troll'):
        super(Troll, self).__init__()
        self.mmode = 'walk'
        self.name = name
        self.body = body.Humanoid()
