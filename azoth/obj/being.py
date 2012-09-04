""" Beings are objects with movement modes and bodies. """

from . import Obj
import body


class Human(Obj):
    """ A being with a humanoid body. """

    def __init__(self, name='obj'):
        super(Human, self).__init__()
        self.mmode = 'walk'
        self.name = name
        self.body = body.Humanoid()
