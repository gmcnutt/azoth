""" Beings are objects with movement modes and bodies. """

from animation import Frame, Loop, Sequence
import baseobject
import body
import logging
import time


logger = logging.getLogger('being')

DIRECTIONS = {
    (-1, -1): "northwest", (0, -1): "north", (1, -1): "northeast",
    (-1, 0):  "west",      (0, 0):  "here",  (1, 0):  "east",
    (-1, 1):  "southwest", (0, 1):  "south", (1, 1):  "southeast",
    }


class Being(baseobject.BaseObject):
    """ Abstract base class for all beings. Subclasses should specify an
    animations table. """
    order = 0
    default_animation_key = "standing"

    def __init__(self):
        super(Being, self).__init__()
        self.controller = None
        self.frameno = 0
        self.time_last_frame = time.time()
        # Animations cannot be pickled, so I can't refer to them directly in my
        # instance fields, so I keep track of the current animation via its key
        self.animation_key = self.default_animation_key

    def __lt__(self, other):
        return self.controller < other.controller

    @property
    def animation(self):
        return self.animations[self.animation_key]

    @animation.setter
    def animation(self, val):
        self.animation_key = val

    def get_current_frame(self):
        """ Return the current animation frame. """
        now = time.time()
        ticks = int(now - self.time_last_frame)
        if ticks:
            for x in xrange(ticks):
                self.tick()
            self.time_last_frame = now
        return self.animation[self.frameno]

    def step(self, x, y, dx, dy):
        """ Move to (x, y) by stepping. """
        direction = DIRECTIONS[(dx, dy)]
        self.frameno = 0
        self.animation = 'walking-%s' % direction
        self.xy = (x, y)

    def tick(self):
        """ Called by the animation loop to advance to the next frame. """
        current_animation = self.animation
        self.frameno = self.frameno + 1
        if self.frameno >= len(current_animation):
            if not isinstance(current_animation, Loop):
                self.animation = self.default_animation_key
            self.frameno = 0


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
                Frame(("player", "standing-0.png"), 0.01, offset=(-16, 0)),
                Frame(("player", "standing-1.png"), 1)]),
        "walking-north": Sequence(frames=[
                Frame(("player", "standing-0.png"), 0.1, offset=(0, 16)),
                Frame(("player", "standing-1.png"), 1)]),
        "walking-south": Sequence(frames=[
                Frame(("player", "standing-0.png"), 0.1, offset=(0, -16)),
                Frame(("player", "standing-1.png"), 1)])
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
