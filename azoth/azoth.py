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

MAX_FPS = 40
DEFAULT_GLYPH = ('?', tcod.black, tcod.white)

# (character, normal color, fog-of-war color)
GLYPHS = {
    terrain.HeavyForest:('T', tcod.darker_green, tcod.darker_green * 0.5),
    terrain.Forest:('t', tcod.dark_green, tcod.dark_green * 0.5),
    terrain.Grass:('.', tcod.light_green, tcod.light_green * 0.5),
    terrain.Trail:('_', tcod.dark_orange, tcod.dark_orange * 0.5),
    terrain.RockWall:('#', tcod.gray, tcod.gray * 0.5),
    terrain.CounterTop:('[', tcod.gray, tcod.gray * 0.5),
    terrain.Water:('~', tcod.blue, tcod.blue * 0.5),
    terrain.Boulder:('o', tcod.white, tcod.white * 0.5),
    terrain.CobbleStone:(',', tcod.light_yellow, tcod.light_yellow * 0.5),
    terrain.Bog:('.', tcod.dark_magenta, tcod.dark_magenta * 0.5),
    terrain.FirePlace:('^', tcod.red, tcod.red * 0.5),
    terrain.Window:('=', tcod.gray, tcod.gray * 0.5),
    weapon.Sword:('|', tcod.white, tcod.white * 0.5),
    being.Player:('@', tcod.white, tcod.white * 0.5)
    }

class TileViewer(gui.Window):
    """ Describe contents of current tile  """

    def __init__(self, **kwargs):
        super(TileViewer, self).__init__(title='Tile', **kwargs)
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
                self.addglyph(col, row, GLYPHS.get(type(item), DEFAULT_GLYPH))
                self.addstr(col + 2, row, '%s' % item)
                row += 1

class MessageConsole(gui.Window):
    """ Print messages.  """

    def __init__(self, **kwargs):
        super(MessageConsole, self).__init__(**kwargs)
        self.messages = []
        self.max_messages = 5
        self.debug_color = tcod.gray
        self.error_color = tcod.red
        self.info_color = tcod.white
        self.warning_color = tcod.yellow

    def add_message(self, message, color):
        if len(self.messages == self.max_messages):
            del self.messages[0]
        self.messages.append((message, color))

    def on_paint(self):
        """ Write the message. """
        for y, pair in enumerate(self.messages):
            self.addstr(self.left_margin, self.top_margin + y, pair[0])

    def debug(self, message):
        self.messages.append((message, self.debug_color))

    def error(self, message):
        self.messages.append((message, self.error_color))

    def info(self, message):
        self.messages.append((message, self.info_color))

    def warn(self, message):
        self.messages.append((message, self.warning_color))

class MapViewer(gui.Window):
    """ Show the map. """

    def __init__(self, **kwargs):
        super(MapViewer, self).__init__(**kwargs)
        self.mapx = 0
        self.mapy = 0
        self.place = None
        self.fov_map = tcod.map_new(self.width, self.height)
        self.scroll_time = 0
        self.render_time = 0
    
    def reset_fov_map(self):
        """ Recompute the FOV map. """
        for y in range(self.height):
            my = self.mapy + y
            for x in range(self.width):
                mx = self.mapx + x
                terrain = self.place.get_terrain(mx, my)
                tcod.map_set_properties(self.fov_map, x, y, 
                                        not terrain.blocks_sight, True)
        RADIUS = max(self.width, self.height)
        LIGHT_WALLS = True
        FOV_ALGO = 0
        tcod.map_compute_fov(self.fov_map, self.x + self.width / 2, 
                             self.y + self.height / 2, RADIUS, LIGHT_WALLS, 
                             FOV_ALGO)

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
        start_ms = tcod.sys_elapsed_milli()
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
        self.scroll_time = tcod.sys_elapsed_milli() - start_ms

    def on_paint(self):
        """ Show the region under the view. """
        start_ms = tcod.sys_elapsed_milli()
        for y in range(self.height):
            my = self.mapy + y
            for x in range(self.width):
                mx = self.mapx + x
                if not tcod.map_is_in_fov(self.fov_map, x, y):
                    if self.place.get_explored(mx, my):
                        terrain = self.place.get_terrain(mx, my)
                        glyph = GLYPHS.get(terrain, DEFAULT_GLYPH)
                        tcod.console_put_char_ex(self.console, x, y, glyph[0], 
                                                 glyph[2], None)
                else:
                    self.place.set_explored(mx, my, True)
                    occ = self.place.get(mx, my)
                    if occ:
                        glyph =  GLYPHS.get(type(occ[0]), DEFAULT_GLYPH)
                    else:
                        terrain = self.place.get_terrain(mx, my)
                        glyph = GLYPHS.get(terrain, DEFAULT_GLYPH)
                    tcod.console_put_char_ex(self.console, x, y, glyph[0], 
                                             glyph[1], None)
        self.render_time = tcod.sys_elapsed_milli() - start_ms

class Term(gui.Window):
    """ Divide the screen into widgets.  """

    def __init__(self, **kwargs):
        super(Term, self).__init__(**kwargs)
        # 
        # Make the map as big as possible on the left side. Put a tile viewer
        # on the top right next to it. Put the console on the bottom right
        # below that.
        #
        self.mview = MapViewer(width=self.width / 2, height=self.height)
        self.tview = TileViewer(x=self.mview.right,
                                y=self.top, 
                                width=self.width - self.mview.width,
                                height = self.height / 2)
        self.console = MessageConsole(x=self.mview.right,
                                      y=self.tview.bottom,
                                      width=self.width - self.mview.width,
                                      height=self.height - self.tview.height)



class Game(object):
    """ Run a session in a terminal. """

    DEFAULT_SAVE_FILE_NAME = 'save.p'

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
        self.term.tview.focus(*self.session.player.loc)
        self.term.console.info('Welcome back!')

    def handle_drop_on_map(self):
        """ Drop first item in inventory onto the ground. """
        if not self.session.player.inventory:
            self.term.console.warn('Nothing to drop!')
        else:
            try:
                self.session.hax2.move_from_bag_to_map(
                    self.session.player.inventory[0],
                    self.session.player.place, self.session.player.x, 
                    self.session.player.y)
            except rules.RuleError as e:
                self.term.console.warn('%s' % e)
            except Exception as e:
                self.term.console.error('%s' % e)

    def handle_get_from_map(self):
        """ Get the top item from the ground. """
        items = [i for i in self.session.world.get(self.session.player.x, 
                                                   self.session.player.y) \
                     if i != self.session.player]
        if items:
            # XXX: handle exceptions
            self.session.hax2.move_from_map_to_bag(
                items[0], 
                self.session.player.inventory)

    def handle_load_session(self):
        self.load(self.DEFAULT_SAVE_FILE_NAME)

    def handle_move_on_map(self, direction):
        """ Move the player and update viewers. """
        try:
            self.session.hax2.move_on_map(self.session.player, direction)
        except rules.RuleError:
            pass
        else:
            self.term.mview.scroll(direction)
            self.term.tview.focus(*self.session.player.loc)

    def handle_save_session(self):
        savefile = open(self.DEFAULT_SAVE_FILE_NAME, 'w')
        self.session.dump(savefile)
        savefile.close()

    def render(self):
        tcod.console_clear(None)
        self.term.mview.paint()
        self.term.tview.paint()
        self.term.console.paint()
        tcod.console_print_left(None, 0, 0, tcod.BKGND_NONE, 
                                "scroll: %d ms" % self.term.mview.scroll_time)
        tcod.console_print_left(None, 0, 1, tcod.BKGND_NONE, 
                                " paint: %d ms" % self.term.mview.render_time)
        tcod.console_flush()
        

    def run(self):
        """ Main loop. """
        keymap = {
            'd': self.handle_drop_on_map,
            'g': self.handle_get_from_map,
            'l': self.handle_load_session,
            's': self.handle_save_session,
            }
        self.render()
        key = tcod.console_check_for_keypress(tcod.KEY_PRESSED)
        while key.c != ord('q'):
            self.log.debug('key.c={} .vk={}'.format(key.c, key.vk))
            direction = {
                tcod.KEY_DOWN:'south',
                tcod.KEY_UP:'north',
                tcod.KEY_RIGHT:'east',
                tcod.KEY_LEFT:'west'
                }.get(key.vk, None)
            if direction:
                self.handle_move_on_map(direction)
            else:
                handler = keymap.get(chr(key.c))
                if handler:
                    handler()
            self.render()
            #key = tcod.console_check_for_keypress(tcod.KEY_PRESSED)
            key = tcod.console_wait_for_keypress(True)

class Applet(object):

    def __init__(self):
        self.done = False

    def quit(self):
        self.done = True

    def render(self):
        tcod.console_clear(None)
        self.on_render()
        tcod.console_flush()

    def run(self):
        self.render()
        while not self.done:
            key = tcod.console_check_for_keypress(tcod.KEY_PRESSED)
            self.on_keypress(key)
            self.render()


class FileSelector(Applet):
    def __init__(self, path=None, width=40, height=20):
        super(FileSelector, self).__init__()
        files = ['.'] + sorted(os.listdir(path))
        self.menu = gui.Menu(width=width, height=height,
                             options=files)

    def handle_enter(self):
        option = self.menu.options[self.menu.current_option]
        print('Selected', option)

    def on_render(self):
        self.menu.paint()

    def on_keypress(self, key):
        handler = {
            tcod.KEY_DOWN: self.menu.scroll_down,
            tcod.KEY_UP: self.menu.scroll_up
            }.get(key.vk)
        if handler:
            handler()
        elif key.c:
            handler = {
                'q': self.quit,
                '\r': self.handle_enter
                }.get(chr(key.c))
            if handler:
                handler()

class MainMenu(Applet):
    def __init__(self, width=0, height=5):
        self.options = {
            'Create new world' : self.handle_create,
            'Load saved game': self.handle_load,
            'Quit' : self.quit
            }
        super(MainMenu, self).__init__()
        self.menu = gui.Menu(width=width, height=height,
                             options=sorted(self.options.keys()))

    def handle_create(self):
        print('create')

    def handle_enter(self):
        option = self.menu.options[self.menu.current_option]
        self.options[option]()

    def handle_load(self):
        FileSelector(path='.').run()

    def on_render(self):
        self.menu.paint()

    def on_keypress(self, key):
        handler = {
            tcod.KEY_DOWN: self.menu.scroll_down,
            tcod.KEY_UP: self.menu.scroll_up
            }.get(key.vk)
        if handler:
            handler()
        elif key.c:
            handler = {
                'q': self.quit,
                'c': self.handle_create,
                'l': self.handle_load,
                '\r': self.handle_enter
                }.get(chr(key.c))
            if handler:
                handler()
        
if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit('Usage: %s <file>'%sys.argv[0])

    os.unlink('azoth.log')
    logging.basicConfig(filename='azoth.log',level=logging.DEBUG)
    tcod.console_set_custom_font('../data/fonts/arial10x10.png', 
                                 tcod.FONT_TYPE_GREYSCALE | 
                                 tcod.FONT_LAYOUT_TCOD)
    tcod.console_init_root(80, 40, "Haxima", False)
    tcod.sys_set_fps(MAX_FPS)
    
    MainMenu(width=40).run()

#    game = Game()
#    game.load(sys.argv[1])
#    game.run()
