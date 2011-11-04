""" Pragmas that move around and do things.  """

import pragma

class Player(pragma.Pragma):
    def __init__(self):
        super(Player, self).__init__()
        self.mmode = 'walk'
        self.name = 'player'
        self.inventory = pragma.Bag()
