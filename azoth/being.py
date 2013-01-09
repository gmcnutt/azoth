""" Beings are objects with movement modes and bodies. """

from animation import Frame, Loop, Sequence
import baseobject
import body


class Being(baseobject.BaseObject):
    """ Abstract base class for all beings. Subclasses should specify an
    animations table. """
    order = 0
    def __init__(self):
        super(Being, self).__init__()
        self.controller = None
        self.frameno = 0
        self.animation_key = "standing"

    def __lt__(self, other):
        return self.controller < other.controller

    def get_current_frame(self):
        self.frameno += 1
        return self.animations[self.animation_key][self.frameno]


class Player(Being):
    """ A being with a humanoid body. """

    animations = {
        "standing": Loop(frames=[
                Frame(("player", "standing-0.png"), 1),
                Frame(("player", "standing-1.png"), 1)]),
        "walking-west": Sequence(frames=[
                Frame(("player", "standing-0.png"), 0.1, offset=(16, 0)),
                Frame(("player", "standing-1.png"), 1)]),
        "walking-east": Sequence(frames=[
                Frame(("player", "standing-0.png"), 0.1, offset=(-16, 0)),
                Frame(("player", "standing-1.png"), 1)]),
        "walking-north": Sequence(frames=[
                Frame(("player", "standing-0.png"), 0.1, offset=(0, 16)),
                Frame(("player", "standing-1.png"), 1)]),
        "walking-south": Sequence(frames=[
                Frame(("player", "standing-0.png"), 0.1, offset=(0, -16)),
                Frame(("player", "standing-1.png"), 1)]),
        }

    def __init__(self, name='obj'):
        super(Player, self).__init__()
        self.mmode = 'walk'
        self.name = name
        self.body = body.Humanoid()


class Troll(Being):

    animations = {
        "standing": Loop(frames=[
                Frame(("troll", "standing-0.png"), 1),
                Frame(("troll", "standing-1.png"), 1)]),
        "walking-west": Sequence(frames=[
                Frame(("troll", "standing-0.png"), 0.1, offset=(16, 0)),
                Frame(("troll", "standing-1.png"), 1)]),
        "walking-east": Sequence(frames=[
                Frame(("troll", "standing-0.png"), 0.1, offset=(-16, 0)),
                Frame(("troll", "standing-1.png"), 1)]),
        "walking-north": Sequence(frames=[
                Frame(("troll", "standing-0.png"), 0.1, offset=(0, 16)),
                Frame(("troll", "standing-1.png"), 1)]),
        "walking-south": Sequence(frames=[
                Frame(("troll", "standing-0.png"), 0.1, offset=(0, -16)),
                Frame(("troll", "standing-1.png"), 1)]),
        }

    def __init__(self, name='troll'):
        super(Troll, self).__init__()
        self.mmode = 'walk'
        self.name = name
        self.body = body.Humanoid()


class Unicorn(Being):

    def __init__(self, name='unicorn'):
        super(Unicorn, self).__init__()
        self.mmode = 'walk'
        self.name = name
        self.body = None
