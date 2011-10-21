import curses
import sys
import hax2
from hax2 import being, plane, rules, terrain
sys.path.append('../azoth')
import azoth

class TileViewerDemo(object):

    def __init__(self, scr):
        self.scr = scr
        self.place = plane.Plane(terrain=terrain.Grass)
        self.x = 0
        self.y = 0
        self.obj = being.Player()
        self.rules = rules.Ruleset()
        self.hax2 = hax2.Transactor(self.rules)
        self.hax2.put(self.obj, self.place, 0, 0)
        self.tview = azoth.TileViewer(width=20, height=20,
                                      style={'border-color':'blue',
                                             'title-color':'yellow'})

    def run(self):
        self.tview.focus(self.place, self.x, self.y)
        self.tview.paint()
        self.scr.getch()
        self.tview.focus(self.place, 1234, -5678)
        self.tview.focus(self.place, 1234, -567891011)
        self.tview.paint()
        self.scr.getch()

def main(scr):
    azoth.setup(scr)
    demo = TileViewerDemo(scr)
    demo.run()

curses.wrapper(main)
