""" Beings are objects with movement modes and bodies. """

import baseobject
import body


class Human(baseobject.BaseObject, baseobject.TakesTurns):
    """ A being with a humanoid body. """

    def __init__(self, name='obj'):
        super(Human, self).__init__()
        self.mmode = 'walk'
        self.name = name
        self.body = body.Humanoid()

    def do_turn(self):
        pass

class Troll(baseobject.BaseObject, baseobject.TakesTurns):

    def __init__(self, name='troll'):
        super(Troll, self).__init__()
        self.mmode = 'walk'
        self.name = name
        self.body = body.Humanoid()

    def do_turn(self, session):
        try:
            session.hax2.move_being_on_map(self, 1, 0)
        except:
            pass
        self.turn_is_done = True
