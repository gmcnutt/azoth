""" Slots arranged into body types.  """

import armor
import item
import slot
import weapon

class BodyError(Exception):
    """ Base class for all body errors. """
    pass

class AlreadyError(BodyError):
    """ Put failed because the required slot(s) are already occupied. """
    def __init__(self, _slot, item):
        super(AlreadyError, self).__init__()
        self.slot = _slot
        self.item = item
    def __str__(self):
        return "{} already occupied by {}".format(self.slot, self.item)


class Head(slot.Slot):
    """ Basic head slot. """
    content_type = armor.Helm
    desc = "head"
    preposition = "on"
    def __init__(self):
        super(Head, self).__init__()

class Hand(slot.Slot):
    """ Basic hand slot. """
    content_type = item.HandItem
    desc = "hand"
    def __init__(self):
        super(Hand, self).__init__()

class Hands(object):

    def __init__(self):
        self.right = Hand()
        self.left = Hand()

    def __contains__(self, thing):
        return thing in self.right or thing in self.left

    def __nonzero__(self):
        return any((self.left, self.right))

    def canput(self, item):
        if item.slots == 1:
            return self.right.canput(item) or self.left.canput(item)
        elif item.slots == 2:
            return self.right.canput(item) and self.left.canput(item)
        else:
            return False

    def get(self):
        return iter(set([self.right.get(), self.left.get()]))

    def put(self, item):
        if item.slots == 1:
            try:
                self.right.put(item)
            except slot.SlotError:
                self.left.put(item)
        elif item.slots == 2:
            self.left.put_as_group(item)
            try:
                self.right.put_as_group(item)
            except slot.SlotError:
                self.left.remove_as_group(item)
                raise
        else:
            raise slot.MultiSlotError(item, 2)

    def remove(self, item):
        self.left.remove_as_group(item)
        self.right.remove_as_group(item)


class Humanoid(object):
    """ A body with a head and two hands. """
    def __init__(self):
        self.head = Head()
        self.hands = Hands()
        self.slots = (self.head, self.hands)

    def __contains__(self, thing):
        if isinstance(thing, type):
            for s in self.slots:
                if isinstance(s, thing):
                    return True
        for s in self.slots:
            if thing in s:
                return True
        return False

    def __nonzero__(self):
        return any(self.slots)

    def __str__(self):
        return "humanoid body"

    def canput(self, item):
        avail = [s for s in self.slots if s.canput(item)]
        return item.slots <= len(avail)

    def get(self):
        """ Get all the items that are held. Returns an iteraror. """
        return [s.get() for s in self.slots if s]

    def has(self, something):
        """ Syntactic sugar for 'something in body' """
        return something in self

    def put(self, item):
        try:
            self.head.put(item)
        except slot.SlotError:
            self.hands.put(item)

    def remove(self, item):
        """ Remove an item. """
        for s in self.slots:
            if item in s:
                s.remove(item)

        
