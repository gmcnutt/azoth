import cPickle
import curses
import hax2.terrain as terrain
import hax2.plane

#
# Initialize color pairs
#

# On-black colors
GREEN = (25)
YELLOW = (56)
GRAY = (1)
WHITE = (0)
RED = (41)
MAGENTA = (33)
BLUE = 9

def setup():
    """ Finish custom init of curses. Must be called after normal init done by
    curses.wrapper(). """

    try: curses.curs_set(0) # disable blinking cursor
    except curses.error: stdscr.leaveok(0)

    # initialize all color pairs
    colors = (curses.COLOR_BLACK, curses.COLOR_BLUE,
              curses.COLOR_CYAN, curses.COLOR_GREEN,
              curses.COLOR_MAGENTA, curses.COLOR_RED,
              curses.COLOR_WHITE, curses.COLOR_YELLOW)
    pair = 1
    for fg in colors:
        for bg in colors:
            if fg != curses.COLOR_WHITE or bg != curses.COLOR_BLACK:
                curses.init_pair(pair, fg, bg)
                pair += 1


class MessageConsole(object):

    def __init__(self, x, y, w, h):
        self.win = curses.newwin(h, w, y, x)

    def write(self, msg):
        self.win.addstr(0, 0, msg)
        self.win.refresh()

class MapViewer(object):

    def __init__(self, x=0, y=0, w=16, h=16, plane=None):
        # ???: if I don't make the width +1 extra, than addch() raises an error
        # on the last column
        self.win = curses.newwin(h, w+1, y, x)
        self.x = 0
        self.y = 0
        self.w = w
        self.h = h
        self.plane = plane
        self.glyphs = {
            terrain.HeavyForest:('T', curses.A_BOLD|curses.color_pair(GREEN)),
            terrain.Forest:('t', curses.A_BOLD|curses.color_pair(GREEN)),
            terrain.Grass:('.', curses.A_BOLD|curses.color_pair(GREEN)),
            terrain.Trail:('_', curses.color_pair(YELLOW)),
            terrain.RockWall:('#', curses.A_BOLD|curses.color_pair(GRAY)),
            terrain.CounterTop:('[', curses.A_BOLD|curses.color_pair(GRAY)),
            terrain.Water:('~', curses.A_BOLD|curses.color_pair(BLUE)),
            terrain.Boulder:('o', curses.A_BOLD|curses.color_pair(WHITE)),
            terrain.CobbleStone:(',', curses.A_BOLD|curses.color_pair(YELLOW)),
            terrain.Bog:('%', curses.A_BOLD|curses.color_pair(MAGENTA)),
            terrain.FirePlace:('^', curses.A_BOLD|curses.color_pair(RED)),
            terrain.Window:('=', curses.A_BOLD|curses.color_pair(GRAY))
            }

    def scroll(self, direction):
        dx, dy = {'north'    :( 0, -1),
                  'northeast':( 1, -1),
                  'east'     :( 1,  0),
                  'southeast':( 1,  1),
                  'south'    :( 0,  1),
                  'southwest':(-1,  1),
                  'west'     :(-1,  0),
                  'northwest':(-1, -1)}[direction]
        self.x += dx
        self.y += dy

    def paint(self):
        self.win.erase()
        for y in range(self.h):
            for x in range(self.w):
                mx = self.x + x
                my = self.y + y
                occ = self.plane.get(mx, my)
                if occ:
                    self.win.addch(y, x, ord(occ[0].glyph))
                else:
                    terrain = self.plane.get_terrain(mx, my)
                    glyph = self.glyphs.get(terrain, ('?', curses.A_REVERSE|\
                                                          curses.A_BOLD))
                    self.win.addch(y, x, ord(glyph[0]), glyph[1])
        self.win.refresh()

class Term(object):

    def __init__(self, scr):
        self.scr = scr
        self.height, self.width = scr.getmaxyx()
        self.mview = MapViewer(0, 0, self.width, self.height - 1)
        self.console = MessageConsole(0, self.height - 1, self.width, 1)
        scr.refresh() # must do this once before newwin refresh works?

    def clear(self):
        self.scr.erase()

def main(stdscr):

    setup()

    term = Term(stdscr)

    term.mview.plane = cPickle.load(open('test.p'))
    term.mview.paint()
    stdscr.getch()

if __name__ == "__main__":
    curses.wrapper(main)
