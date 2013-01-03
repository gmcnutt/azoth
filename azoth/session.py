import config
import cPickle
import executor

class Session(object):
    def __init__(self):
        self.rules = executor.Ruleset()
        self.hax2 = executor.Executor(self.rules)
        self.player = None
        self.world = None
        self.rules.set_passability('walk', 'wall', executor.PASS_NONE)
        self.rules.set_passability('walk', 'boulder', executor.PASS_NONE)

    def save(self, filename):
        cPickle.dump(self, open(filename, 'w'))


def load(filename):
    return cPickle.load(open(filename, 'r'))
