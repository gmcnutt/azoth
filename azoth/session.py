import cPickle
import executor

class Session(object):
    def __init__(self):
        self.rules = executor.Ruleset()
        self.hax2 = executor.Executor(self.rules)
        self.player = None
        self.world = None
        self.rules.set_passability('walk', 'wall', executor.PASS_NONE)

    def dump(self, _file):
        cPickle.dump(self, _file)


def load(_file):
    return cPickle.load(_file)
