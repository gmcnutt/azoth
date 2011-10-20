import curses
from tools import *
from azoth import azoth
from hax2 import plane, terrain

class TileViewerTest(unittest.TestCase):

    def setUp(self):
        self.place = plane.Plane(terrain=terrain.Grass)
        self.x = 0
        self.y = 0

    def _init(self, scr):
        azoth.setup(scr)
        self.tview = azoth.TileViewer(width=20, height=20, boxed=True, 
                                      title='Test', 
                                      style={'border-color':'blue',
                                             'title-color':'yellow'})
        self.tview.paint()
        scr.getch()
        self.tview.focus(self.place, self.x, self.y)
        self.tview.paint()
        scr.getch()

    def test_init(self):
        curses.wrapper(self._init)
