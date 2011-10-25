#!/usr/bin/python

import cPickle
import colors
import gui
import hax2
from hax2 import being, rules, session, terrain, weapon
import hax2.plane
import libtcodpy as tcod
import logging
import os
import sys

DEFAULT_GLYPH = ('?', tcod.black, tcod.white)

GLYPHS = {
    terrain.HeavyForest:('T', tcod.darker_green, tcod.black),
    terrain.Forest:('t', tcod.dark_green, tcod.black),
    terrain.Grass:('.', tcod.light_green, tcod.black),
    terrain.Trail:('_', tcod.dark_orange, tcod.black),
    terrain.RockWall:('#', tcod.gray, tcod.black),
    terrain.CounterTop:('[', tcod.gray, tcod.black),
    terrain.Water:('~', tcod.blue, tcod.black),
    terrain.Boulder:('o', tcod.white, tcod.black),
    terrain.CobbleStone:(',', tcod.light_yellow, tcod.black),
    terrain.Bog:('.', tcod.dark_magenta, tcod.black),
    terrain.FirePlace:('^', tcod.red, tcod.black),
    terrain.Window:('=', tcod.gray, tcod.black),
    weapon.Sword:('|', tcod.white, tcod.black),
    being.Player:('@', tcod.white, tcod.black)
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
            self.addglyph(col, row, GLYPHS.get(terrain, DEFAULT_GLYPH))
            self.addstr(col + 2, row, '%s' % terrain.name)
            row += 1
            items = self.place.get(self.mapx, self.mapy)
            for item in items:
                self.addglyph(col, row, GLYPHS.get(type(item),
                                                              DEFAULT_GLYPH))
                self.addstr(col + 2, row, '%s' % item)
                row += 1

class MessageConsole(gui.Window):
    """ Print messages.  """

    def __init__(self, **kwargs):
        super(MessageConsole, self).__init__(**kwargs)
        self.msg = None

    def on_paint(self):
        """ Write the message. """
        self.addstr(0, 0, self.msg)

    def write(self, msg):
        """ Save the message for painting. """
        self.msg = msg


class MapViewer(gui.Window):
    """ Show the map. """

    def __init__(self, **kwargs):
        super(MapViewer, self).__init__(**kwargs)
        self.mapx = 0
        self.mapy = 0
        self.place = None
        self.fov_map = tcod.map_new(self.width, self.height)
    
    def reset_fov_map(self):
        """ Recompute the FOV map. """
        for y in range(self.height):
            my = self.mapy + y
            for x in range(self.width):
                mx = self.mapx + x
                terrain = self.place.get_terrain(mx, my)
                tcod.map_set_properties(self.fov_map, x, y, not terrain.blocks_sight, True)
        RADIUS = max(self.width, self.height)
        LIGHT_WALLS = True
        FOV_ALGO = 0
        tcod.map_compute_fov(self.fov_map, self.x + self.width / 2, self.y + self.height / 2, RADIUS, LIGHT_WALLS, FOV_ALGO)

    def focus(self, obj):
        """ Center the viewer on an object.  """
        # XXX: just keep the obj and have paint recompute the rest every time?
        self.place = obj.place
        self.mapx = obj.x - self.width / 2
        self.mapy = obj.y - self.height / 2
        self.title = self.place.name
        self.reset_fov_map()

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
        self.reset_fov_map() # brute force for now

    def on_paint(self):
        """ Show the region under the view. """
        for y in range(self.height):
            my = self.mapy + y
            for x in range(self.width):
                mx = self.mapx + x
                if not tcod.map_is_in_fov(self.fov_map, x, y):
                    if self.place.get_explored(mx, my):
                        terrain = self.place.get_terrain(mx, my)
                        glyph = GLYPHS.get(terrain, DEFAULT_GLYPH)
                        self.addglyph(x, y, glyph, divisor=0.5)
                else:
                    self.place.set_explored(mx, my, True)
                    occ = self.place.get(mx, my)
                    if occ:
                        glyph =  GLYPHS.get(type(occ[0]), DEFAULT_GLYPH)
                    else:
                        terrain = self.place.get_terrain(mx, my)
                        glyph = GLYPHS.get(terrain, DEFAULT_GLYPH)
                    self.addglyph(x, y, glyph)

class Term(gui.Window):
    """ Divide the screen into widgets.  """

    def __init__(self, **kwargs):
        super(Term, self).__init__(**kwargs)
        # 
        # Make the map as big as possible on the left side. Put a tile viewer
        # on the top right next to it. Put the console on the bottom right
        # below that.
        #
        self.mview = MapViewer(width=self.width / 2, height=self.height - 1, 
                               boxed=False)
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
                                      boxed=False)



class Game(object):
    """ Run a session in a terminal. """

    def __init__(self):
        self.term = Term(width=tcod.console_get_width(None), 
                         height=tcod.console_get_height(None))
        self.session = None
        self.log = logging.getLogger('game')

    def load(self, fname):
        loadfile = open(fname)
        self.session = session.load(open(fname))
        loadfile.close()
        self.term.mview.focus(self.session.player)
        self.term.mview.paint()
        self.term.tview.focus(*self.session.player.loc)
        self.term.tview.paint()
        self.term.console.write('%s'%type(self.session.player))
        tcod.console_flush()

    def run(self):
        ch = tcod.console_wait_for_keypress(False)
        while ch.c != ord('q'):
            self.log.debug('ch.c={} .vk={}'.format(ch.c, ch.vk))
            direction = {
                tcod.KEY_DOWN:'south',
                tcod.KEY_UP:'north',
                tcod.KEY_RIGHT:'east',
                tcod.KEY_LEFT:'west'
                }.get(ch.vk, None)
            if direction:
                try:
                    self.session.hax2.move(self.session.player, direction)
                except rules.RuleError:
                    pass
                else:
                    tcod.console_clear(None)
                    self.term.mview.scroll(direction)
                    self.term.mview.paint()
                    self.term.tview.focus(*self.session.player.loc)
                    self.term.tview.paint()
                    tcod.console_flush()
            elif ch.c == ord('s'):
                savefile = open('save.p', 'w')
                self.session.dump(savefile)
                savefile.close()
            elif ch.c == ord('l'):
                self.load('save.p')
            ch =  tcod.console_wait_for_keypress(False)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit('Usage: %s <file>'%sys.argv[0])

    os.unlink('azoth.log')
    logging.basicConfig(filename='azoth.log',level=logging.DEBUG)
    tcod.console_set_custom_font("data/fonts/consolas12x12_gs_tc.png", tcod.FONT_LAYOUT_TCOD | tcod.FONT_TYPE_GREYSCALE)
    tcod.console_set_custom_font('data/fonts/arial10x10.png', 
                                 tcod.FONT_TYPE_GREYSCALE | 
                                 tcod.FONT_LAYOUT_TCOD)
    tcod.console_init_root(80, 40, "Haxima", False)
    game = Game()
    game.load(sys.argv[1])
    game.run()
