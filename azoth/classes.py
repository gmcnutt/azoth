"""
In-game object classes. Every object in the game world will have a class which
defines the things which are common to every instance of that object: name,
sprite, and so on.
"""

class GameClass(object):
    """ Every in-game object has a name and a sprite. """
    def __init__(self, name, sprite):
        self.name = name
        self.sprite = sprite

class Reagent(GameClass):
    pass
