#!/usr/bin/python

import cPickle
import curses
import hax2
from hax2 import rules, session, terrain
import hax2.plane
import sys

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

    def __init__(self, scrx=0, scry=0, width=16, height=16):
        # ???: if I don't make the width +1 extra, than addch() raises an error
        # on the last column
        self.win = curses.newwin(height, width + 1, scry, scrx)
        self.width = width
        self.height = height
        self.mapx = 0
        self.mapy = 0
        self.plane = None
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
            terrain.Bog:('.', curses.A_BOLD|curses.color_pair(MAGENTA)),
            terrain.FirePlace:('^', curses.A_BOLD|curses.color_pair(RED)),
            terrain.Window:('=', curses.A_BOLD|curses.color_pair(GRAY))
            }

    def focus(self, obj):
        self.plane = obj.place
        self.mapx = obj.x - self.width / 2
        self.mapy = obj.y - self.height / 2

    def scroll(self, direction):
        """ Scroll the view over the current place. """
        dx, dy = {'north'    :( 0, -1),
                  'northeast':( 1, -1),
                  'east'     :( 1,  0),
                  'southeast':( 1,  1),
                  'south'    :( 0,  1),
                  'southwest':(-1,  1),
                  'west'     :(-1,  0),
                  'northwest':(-1, -1)}[direction]
        self.mapx += dx
        self.mapy += dy

    def paint(self):
        """ Show the region under the view. """
        self.win.erase()
        for y in range(self.height):
            for x in range(self.width):
                mx = self.mapx + x
                my = self.mapy + y
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

class Game(object):
    def __init__(self, scr):
        self.scr = scr
        self.term = Term(scr)
        self.session = None
    def load(self, fname):
        loadfile = open(fname)
        self.session = session.load(open(fname))
        loadfile.close()
        self.term.mview.focus(self.session.player)
        self.term.mview.paint()
    def run(self):
        ch = self.scr.getch()
        while ch != ord('q'):
            direction = {
                curses.KEY_DOWN:'south',
                curses.KEY_UP:'north',
                curses.KEY_RIGHT:'east',
                curses.KEY_LEFT:'west'
                }.get(ch, None)
            if direction:
                try:
                    self.session.hax2.move(self.session.player, direction)
                    self.term.mview.scroll(direction)
                except rules.RuleError:
                    pass
                self.term.mview.paint()
            elif ch == ord('s'):
                savefile = open('save.p', 'w')
                self.session.dump(savefile)
                savefile.close()
            elif ch == ord('l'):
                self.load('save.p')
            ch = self.scr.getch()

def main(stdscr, fname):
    setup()
    game = Game(stdscr)
    game.load(fname)
    game.run()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit('Usage: %s <file>'%sys.argv[0])
    curses.wrapper(main, sys.argv[1])
