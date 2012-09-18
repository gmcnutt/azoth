""" Weapons. """
import item

class Sword(item.HandItem):
    """ Your basic sword. """
    slots = 1
    def __str__(self):
        return "a sword"

class Sword2H(Sword):
    """ Your basic two-handed sword. """
    slots = 2
    def __str__(self):
        return "a 2H sword"
    
