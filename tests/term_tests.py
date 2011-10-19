import cPickle
import curses
from tools import *
import hax2
from hax2 import plane, pragma, rules, term, terrain, terrainmap

class Default(unittest.TestCase):
    def setUp(self):
        self.rules = rules.Ruleset()
        self.hax2 = hax2.Transactor(self.rules)
        self.tmap = terrainmap.load_from_nazghul_scm('gregors-hut.scm')
        self.obj = pragma.Pragma()
        self.obj.glyph = '@'
        self.obj.name = 'player'
        self.plane = plane.Plane(name='gh', 
                                 terrain=terrain.Grass)

    def runviewer(self, scr):
        term.setup()
        self.plane.push_terrain_map(0, 0, self.tmap)

        self.obj.mmode = 'walk'
        self.rules.set_passability('walk', 'wall', rules.PASS_NONE)

        self.hax2.put(self.obj, self.plane, 10, 10)
        mview = term.MapViewer(x=0, y=0, w=21, h=21, plane=self.plane)
        scr.refresh()
        mview.paint()

        ch = scr.getch()
        while ch != ord('q'):
            direction = {
                curses.KEY_DOWN:'south',
                curses.KEY_UP:'north',
                curses.KEY_RIGHT:'east',
                curses.KEY_LEFT:'west'
                }.get(ch, None)
            if direction:
                try:
                    self.hax2.move(self.obj, direction)
                    mview.scroll(direction)
                except rules.RuleError:
                    pass
                mview.paint()
            ch = scr.getch()

        save = open('test.p', 'w')
        cPickle.dump(self.plane, save)
        save.close()

    def test_init(self):
        curses.wrapper(self.runviewer)
