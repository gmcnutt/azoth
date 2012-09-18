""" Armor types. """

import item

class Shield(item.HandItem):
    """ Basic shield. """
    slots = 1
    def __str__(self):
        return "a shield"

class Helm(item.Item):
    """ Basic helm. """
    slots = 1
    def __str__(self):
        return "a helm"


class Coif(Helm):
    """ A coif. """
    slots = 1
    def __str__(self):
        return "a coif"
