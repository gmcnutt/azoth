import cPickle
import transactor

class Session(object):
    def __init__(self):
        self.rules = transactor.Ruleset()
        self.hax2 = transactor.Transactor(self.rules)
        self.player = None
        self.world = None
        self.rules.set_passability('walk', 'wall', transactor.PASS_NONE)

    def dump(self, _file):
        cPickle.dump(self, _file)


def load(_file):
    return cPickle.load(_file)
