#!/usr/bin/python

import cPickle
import curses
import hax2
from hax2 import being, rules, session, terrain, weapon
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

DEFAULT_GLYPH = ('?', curses.A_REVERSE|curses.A_BOLD)

def setup(scr):
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

    # XXX: experiments show I must call scr.refresh() at least once before
    # window.refresh() will work. I don't know why.
    scr.refresh()

    # Most Window descendants are going to want access to the glyph map, so
    # I'll make it an attribute of the Window class. I can't declare it until
    # after curses has been initialized.
    Window.glyphs = {
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
        terrain.Window:('=', curses.A_BOLD|curses.color_pair(GRAY)),
        weapon.Sword:('|', curses.color_pair(WHITE)),
        being.Player:('@', curses.A_BOLD|curses.color_pair(WHITE))
        }


class Window(object):
    """ Base class for terminal windows. """

    def __init__(self, x=0, y=0, width=0, height=0, boxed=False, title=None,
                 win=None, style=None):
        self.win = win or curses.newwin(height, width, y, x)
        self.boxed = boxed
        self.title = title
        self.top = 0 if not boxed else 1
        self.left = 0 if not boxed else 1
        self.style = style or {}

    @property
    def x(self):
        """ Screen x-coordinate of upper left corner. """
        return self.win.getyx()[1]

    @property
    def y(self):
        """ Screen y-coordinate of upper left corner. """
        return self.win.getyx()[0]

    @property
    def width(self):
        """ Number of columns. """
        return self.win.getmaxyx()[1]

    @property
    def height(self):
        """ Number of rows. """
        return self.win.getmaxyx()[0]

    def addglyph(self, row, col, glyph):
        """ Like addch() but uses a tuple for (char, attr). """
        self.win.addch(row, col, glyph[0], glyph[1])

    def on_paint(self):
        """ Hook for subclasses. """
        raise NotImplemented()

    def paint(self):
        """ Paint the window. Subclasses should implement on_paint(). """
        self.win.erase()
        self.on_paint()
        if self.boxed:
            attr = 0
            color = self.style.get('border-color')
            if color == 'blue':
                attr = curses.color_pair(BLUE)
            self.win.attron(attr)
            self.win.box()
            self.win.attroff(attr)
        if self.title:
            attr = 0
            color = self.style.get('title-color')
            if color == 'yellow':
                attr = curses.color_pair(YELLOW)
            self.win.attron(attr)
            n = self.width - 2
            self.win.addnstr(0, 1, '%s' % self.title, n)
            self.win.attroff(attr)
        self.win.refresh()


class TileViewer(Window):
    """ Describe contents of current tile  """

    def __init__(self, **kwargs):
        super(TileViewer, self).__init__(boxed=True, title='Tile', **kwargs)
        self.original_title = self.title
        self.place = None
        self.mapx = 0
        self.mapy = 0

    def focus(self, place, x, y):
        self.title = self.original_title + ':%d,%d' % (x, y)
        self.place = place
        self.mapx = x
        self.mapy = y

    def on_paint(self):
        if self.place:
            row = self.top
            terrain = self.place.get_terrain(self.mapx, self.mapy)
            self.addglyph(row, self.left, self.glyphs.get(terrain, 
                                                               DEFAULT_GLYPH))
            self.win.addstr(row, self.left + 2, '%s' % terrain.name)
            row += 1
            items = self.place.get(self.mapx, self.mapy)
            for item in items:
                self.addglyph(row, self.left, self.glyphs.get(type(item),
                                                              DEFAULT_GLYPH))
                self.win.addstr(row, self.left + 2, '%s' % item)
                row += 1

class MessageConsole(Window):
    """ Print messages.  """

    def __init__(self, **kwargs):
        super(MessageConsole, self).__init__(**kwargs)

    def on_paint(self):
        """ Do nothing -- write() paints directly. """
        pass

    def write(self, msg):
        """ Write a message and paint now. """
        self.win.erase()
        self.win.addstr(0, 0, msg)
        if self.boxed:
            self.win.box()
        self.win.refresh()


class MapViewer(Window):
    """ Show the map. """

    def __init__(self, **kwargs):
        super(MapViewer, self).__init__(**kwargs)
        self.mapx = 0
        self.mapy = 0
        self.place = None
        
    def focus(self, obj):
        """ Center the viewer on an object.  """
        # XXX: just keep the obj and have paint recompute the rest every time?
        self.place = obj.place
        self.mapx = obj.x - self.width / 2
        self.mapy = obj.y - self.height / 2
        self.title = self.place.name

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

    def on_paint(self):
        """ Show the region under the view. """
        for y in range(self.height):
            # addch(y, width) raises an error, so cut back by 1
            for x in range(self.width-1):
                mx = self.mapx + x
                my = self.mapy + y
                occ = self.place.get(mx, my)
                if occ:
                    glyph = self.glyphs.get(type(occ[0]), DEFAULT_GLYPH)
                    self.win.addch(y, x, ord(glyph[0]), glyph[1])
                else:
                    terrain = self.place.get_terrain(mx, my)
                    glyph = self.glyphs.get(terrain, DEFAULT_GLYPH)
                    self.win.addch(y, x, ord(glyph[0]), glyph[1])
        #self.win.box()

class Term(Window):
    """ Divide the screen into widgets.  """

    def __init__(self, scr):
        super(Term, self).__init__(win=scr)
        # 
        # Make the map as big as possible on the left side. Put a tile viewer
        # on the top right next to it. Put the console on the bottom right
        # below that.
        #
        self.mview = MapViewer(width=self.height, height=self.height, 
                               boxed=False)
        self.tview = TileViewer(x=self.mview.width, y=0, 
                                width=self.width - self.mview.width, 
                                height=self.height / 2)
        self.console = MessageConsole(x=self.mview.width, 
                                      y=self.tview.height, 
                                      width=self.width - self.mview.width, 
                                      height=self.height - self.tview.height,
                                      boxed=True)

    def clear(self):
        self.scr.erase()


class Game(object):
    """ Run a session in a terminal. """

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
        self.term.tview.focus(*self.session.player.loc)
        self.term.tview.paint()
        self.term.console.write('%s'%type(self.session.player))

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
                except rules.RuleError:
                    pass
                else:
                    self.term.mview.scroll(direction)
                    self.term.mview.paint()
                    self.term.tview.focus(*self.session.player.loc)
                    self.term.tview.paint()
            elif ch == ord('s'):
                savefile = open('save.p', 'w')
                self.session.dump(savefile)
                savefile.close()
            elif ch == ord('l'):
                self.load('save.p')
            ch = self.scr.getch()

def main(stdscr, fname):
    setup(stdscr)
    game = Game(stdscr)
    game.load(fname)
    game.run()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit('Usage: %s <file>'%sys.argv[0])
    curses.wrapper(main, sys.argv[1])
