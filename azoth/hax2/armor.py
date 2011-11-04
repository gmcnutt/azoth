""" Armor types. """

import item

class Shield(item.HandItem):
    """ Basic shield. """
    def __str__(self):
        return "a shield"

class Helm(item.Item):
    """ Basic helm. """
    def __str__(self):
        return "a helm"


class Coif(Helm):
    """ A coif. """
    def __str__(self):
        return "a coif"
