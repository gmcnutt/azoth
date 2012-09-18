""" Inventory slots. """

class SlotError(Exception):
    pass

class OccupiedError(SlotError):
    def __init__(self, slot, item):
        self.slot = slot
        self.item = item
    def __str__(self):
        return "{} already has {}".format(self.slot, self.item)

class InsufficientSlotsError(SlotError):
    def __init__(self, body, item, avail):
        self.body = body
        self.item = item
        self.avail = avail
    def __str__(self):
        return "{} has {} empty slots but {} requires {}".\
            format(self.body, self.avail, self.item, self.item.slots)

class WrongContentError(SlotError):
    def __init__(self, slot, item):
        self.slot = slot
        self.item = item
    def __str__(self):
        return "{} wrong type for {}".format(self.item, self.slot)

class MultiSlotError(SlotError):
    def __init__(self, item, avail):
        self.item = item
        self.avail = avail
    def __str__(self):
        return "{} requires {} slots but only {} available".\
            format(self.item, self.item.slots, self.avail)

class Slot(object):
    """ A container that accepts only a certain type of content.  """

    content_type = object
    preposition = "in"
    desc = "slot"

    def __init__(self, content=None, sibling=None, desc=None):
        self.content = content
        self.siblings = sibling
        if desc is not None:
            self.desc = desc

    def __nonzero__(self):
        return not self.empty

    def __contains__(self, val):
        if isinstance(val, type):
            return isinstance(self.content, val)
        return self.content == val

    def __str__(self):
        return self.__class__.__name__.lower()

    @property
    def empty(self):
        return self.content is None

    def canput(self, item):
        """ Return True iff the item can be put in the slot right now. """
        return isinstance(item, self.content_type) and self.empty

    def clear(self):
        """ Remove whatever is in the slot.  """
        self.content = None

    def get(self):
        """ Return whatever is in the slot.  """
        return self.content

    def has(self, val):
        """ Syntactic sugar for 'val in self' """
        return val in self

    def items(self):
        """ Return a list of (desc, content) pairs. """
        return [(self.desc, self.content)]
    
    def put(self, item):
        """ Put item into the slot. Raises TypeError if item is of the wrong
        type for this slot. Raise OccupiedError if something is already in the
        slot. """
        if item.slots > 1:
            raise MultiSlotError(item, 1)
        self.put_as_group(item)

    def put_as_group(self, item):
        """ Just like put but ignore slot counts. """
        if not isinstance(item, self.content_type):
            raise WrongContentError(self, item)
        if not self.empty:
            raise OccupiedError(self, item)
        self.content = item        

    def remove(self, item):
        """ Remove the item. No effect if not contained. Raises MultiSlotError
        if the item requires more than one slot (caller must use group-level
        remove instead)."""
        if item.slots > 1:
            raise MultiSlotError(item, 1)                
        self.remove_as_group(item)

    def remove_as_group(self, item):
        if item == self.content:
            self.content = None

        
