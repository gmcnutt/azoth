#!/usr/bin/python

import cPickle
import colors
import curses
import gui
import hax2
from hax2 import being, rules, session, terrain, weapon
import hax2.plane
import sys

#
# Initialize color pairs
#


DEFAULT_GLYPH = ('?', curses.A_REVERSE|curses.A_BOLD)

def setup(scr):
    """ Finish custom init of curses. Must be called after normal init done by
    curses.wrapper(). """

    try: curses.curs_set(0) # disable blinking cursor
    except curses.error: stdscr.leaveok(0)

    # initialize all color pairs
    _colors = (curses.COLOR_BLACK, curses.COLOR_BLUE,
              curses.COLOR_CYAN, curses.COLOR_GREEN,
              curses.COLOR_MAGENTA, curses.COLOR_RED,
              curses.COLOR_WHITE, curses.COLOR_YELLOW)
    pair = 1
    for fg in _colors:
        for bg in _colors:
            if fg != curses.COLOR_WHITE or bg != curses.COLOR_BLACK:
                curses.init_pair(pair, fg, bg)
                pair += 1

    # XXX: experiments show I must call scr.refresh() at least once before
    # window.refresh() will work. I don't know why.
    scr.refresh()

    # Most Window descendants are going to want access to the glyph map, so
    # I'll make it an attribute of the Window class. I can't declare it until
    # after curses has been initialized.
    gui.Window.glyphs = {
        terrain.HeavyForest:('T', curses.A_BOLD|curses.color_pair(colors.GREEN)),
        terrain.Forest:('t', curses.A_BOLD|curses.color_pair(colors.GREEN)),
        terrain.Grass:('.', curses.A_BOLD|curses.color_pair(colors.GREEN)),
        terrain.Trail:('_', curses.color_pair(colors.YELLOW)),
        terrain.RockWall:('#', curses.A_BOLD|curses.color_pair(colors.GRAY)),
        terrain.CounterTop:('[', curses.A_BOLD|curses.color_pair(colors.GRAY)),
        terrain.Water:('~', curses.A_BOLD|curses.color_pair(colors.BLUE)),
        terrain.Boulder:('o', curses.A_BOLD|curses.color_pair(colors.WHITE)),
        terrain.CobbleStone:(',', curses.A_BOLD|curses.color_pair(colors.YELLOW)),
        terrain.Bog:('.', curses.A_BOLD|curses.color_pair(colors.MAGENTA)),
        terrain.FirePlace:('^', curses.A_BOLD|curses.color_pair(colors.RED)),
        terrain.Window:('=', curses.A_BOLD|curses.color_pair(colors.GRAY)),
        weapon.Sword:('|', curses.color_pair(colors.WHITE)),
        being.Player:('@', curses.A_BOLD|curses.color_pair(colors.WHITE))
        }


class TileViewer(gui.Window):
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
            row = self.top_margin
            col = self.left_margin
            terrain = self.place.get_terrain(self.mapx, self.mapy)
            self.addglyph(row, col, self.glyphs.get(terrain, DEFAULT_GLYPH))
            self.win.addstr(row, col + 2, '%s' % terrain.name)
            row += 1
            items = self.place.get(self.mapx, self.mapy)
            for item in items:
                self.addglyph(row, col, self.glyphs.get(type(item),
                                                              DEFAULT_GLYPH))
                self.win.addstr(row, col + 2, '%s' % item)
                row += 1

class MessageConsole(gui.Window):
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


class MapViewer(gui.Window):
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

class Term(gui.Window):
    """ Divide the screen into widgets.  """

    def __init__(self, scr):
        super(Term, self).__init__(win=scr)
        # 
        # Make the map as big as possible on the left side. Put a tile viewer
        # on the top right next to it. Put the console on the bottom right
        # below that.
        #
        self.mview = MapViewer(width=self.width / 2, height=self.height - 1, 
                               boxed=True)
        tv_width = self.width / 4
        tv_height = self.height / 2
        self.tview = TileViewer(x=self.mview.right,
                                y=self.top, 
                                width=self.width - self.mview.width,
                                height = self.height / 2)
        self.console = MessageConsole(x=self.mview.right,
                                      y=self.tview.bottom,
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
