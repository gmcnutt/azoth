""" Items. """

import pragma

class Item(pragma.Pragma):
    """ Base class for anything that can be put into inventory. An item
    specifies the number of inventory slots it requires. """
    slots = 1

class HandItem(Item):
    """ Base class for any item that can be put into a hand slot. """
    pass
