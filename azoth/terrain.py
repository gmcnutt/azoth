"""
Terrains.
"""

class Terrain(object):
    """ A terrain can impede movement, block vision, emit light or apply
    effects to objects that rest on it.  """

    def __init__(self, name, pclass, sprite, transparent, light=0, effect=None,
                 flags=()):
        self.name = name
        self.pclass = pclass
        self.sprite = sprite
        self.transparent = transparent
        self.light = light
        self.effect = effect
        self.bad = "bad" in flags
        self.inflammable = "inflammable" in flags
        self.deck = "deck" in flags
