import body
import obj



class Human(obj.Obj):
    """ A being with a humanoid body. """

    def __init__(self, name='obj'):
        super(Human, self).__init__()
        self.mmode = 'walk'
        self.name = name
        self.body = body.Humanoid()
