import cPickle
import rules
import transactor

class Session(object):
    def __init__(self):
        self.rules = rules.Ruleset()
        self.hax2 = transactor.Transactor(self.rules)
        self.player = None
        self.world = None
        self.rules.set_passability('walk', 'wall', rules.PASS_NONE)

    def dump(self, _file):
        cPickle.dump(self, _file)


def load(_file):
    return cPickle.load(_file)
