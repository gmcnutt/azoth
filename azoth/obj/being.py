""" Beings are objects with movement modes and bodies. """

import obj
import body


class Human(obj.Obj):
    """ A being with a humanoid body. """

    def __init__(self, name='obj'):
        super(Human, self).__init__()
        self.mmode = 'walk'
        self.name = name
        self.body = body.Humanoid()

class Troll(obj.Obj):

    def __init__(self, name='troll'):
        super(Troll, self).__init__()
        self.mmode = 'walk'
        self.name = name
        self.body = body.Humanoid()
