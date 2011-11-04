#!/usr/bin/python

import argparse
import cPickle
import colors
import gui
import hax2
from hax2 import being, place, rules, session, terrain, weapon
import hax2.plane
import libtcodpy as tcod
import logging
import os
import sys

SCREEN_COLUMNS = 80
SCREEN_ROWS = 40
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

class TerrainSelector(gui.Window):

    terrains = [
        terrain.HeavyForest,
        terrain.Forest,
        terrain.Grass,
        terrain.Trail,
        terrain.RockWall,
        terrain.CounterTop,
        terrain.Water,
        terrain.Boulder,
        terrain.CobbleStone,
        terrain.Bog,
        terrain.FirePlace,
        terrain.Window
        ]

    def __init__(self, **kwargs):
        title = 'Terrains'
        self.columns = len(title) + 2
        self.rows = (len(self.terrains) + self.columns - 1) / self.columns
        super(TerrainSelector, self).__init__(width=self.columns + 2,
                                              height=self.rows + 2,
                                              title=title, **kwargs)
        self.selected_terrain = None

    def on_mouse_left_click(self, x, y):
        """ Mouse left-button click over (x, y) in window coordinates. """
        palette_x = x - 1
        palette_y = y - 1
        palette_index = palette_y * self.columns + palette_x
        if palette_index < len(self.terrains):
            self.selected_terrain = self.terrains[palette_index]

    def on_paint(self):
        # Find mouse position.
        mouse = tcod.mouse_get_status()
        mouse_x, mouse_y = mouse.cx - self.x - 1, mouse.cy - self.y - 1
        for i, terrain in enumerate(self.terrains):
            y = i / self.columns
            x = i % self.columns
            glyph = GLYPHS.get(terrain, DEFAULT_GLYPH)
            invert = ((mouse_x == x and mouse_y == y) or 
                      terrain == self.selected_terrain)
            self.put_char(x, y, glyph[0], glyph[1], invert=invert)


class SectorViewer(gui.Window):
    def __init__(self, sector, **kwargs):
        super(SectorViewer, self).__init__(width=sector.width + 4, 
                                           height=sector.height + 4,
                                           title='Sector', **kwargs)
        self.sector = sector

    def on_paint(self):
        # Find mouse position.
        mouse = tcod.mouse_get_status()
        mouse_x, mouse_y = mouse.cx - self.x - 3, mouse.cy - self.y - 3
        # Print numbers on top.
        for x in range(self.sector.width):
            tens = int(x / 10) + ord('0')
            ones = (x % 10) + ord('0')
            color = tcod.yellow if mouse_x == x else None
            self.put_char(x + 2, 0, tens, color=color)
            self.put_char(x + 2, 1, ones, color=color)
        for y in range(self.sector.height):
            # Print numbers on side.
            tens = int(y / 10) + ord('0')
            ones = (y % 10) + ord('0')
            color = tcod.yellow if mouse_y == y else None
            self.put_char(0, y + 2, tens, color=color)
            self.put_char(1, y + 2, ones, color=color)
            # Print tile.
            for x in range(self.sector.width):
                occ = self.sector.get_occupant(x, y)
                if occ:
                    glyph =  GLYPHS.get(type(occ[0]), DEFAULT_GLYPH)
                else:
                    items = self.sector.get_items(x, y)
                    if items:
                        glyph = GLYPHS.get(items[0], DEFAULT_GLYPH)
                    else:
                        terrain = self.sector.get_terrain(x, y)
                        glyph = GLYPHS.get(terrain, DEFAULT_GLYPH)
                invert = (y == mouse_y and x == mouse_x)
                self.put_char(x + 2, y + 2, glyph[0], color=glyph[1], 
                              invert=invert)

    def xy_to_map_xy(self, x, y):
        """ Convert x, y in window coordinates to sector coordinates. """
        return x - 3, y - 3

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

    def focus(self, place, x, y):
        """ Center the viewer on an object.  """
        # XXX: just keep the obj and have paint recompute the rest every time?
        self.place = place
        self.mapx = x - self.width / 2
        self.mapy = y - self.height / 2
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
                    items = self.place.get(mx, my)
                    if items:
                        glyph = GLYPHS.get(type(items[0]), DEFAULT_GLYPH)
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
        self.term.mview.focus(*self.session.player.loc)
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


class Editor(gui.Applet):

    """ Game editor. """
    def __init__(self):
        super(Editor, self).__init__()
        self.sector = place.Sector(default_terrain=terrain.Grass)
        self.sector_viewer = SectorViewer(sector=self.sector)
        self.sector_viewer.on_mouse_left_click = self.catch_left_mouse_click
        self.terrain_selector = TerrainSelector(x=self.sector_viewer.width)
        self.add_window(self.sector_viewer)
        self.add_window(self.terrain_selector)

    def catch_left_mouse_click(self, x, y):
        """ Intercept the left mouse click intended for the sector viewer and
        use it to paint selected terrain. """
        terrain = self.terrain_selector.selected_terrain
        if terrain is None:
            return
        map_x, map_y = self.sector_viewer.xy_to_map_xy(x, y)
        if map_x < 0 or map_y < 0:
            return
        self.sector.set_terrain(map_x, map_y, terrain)

    def handle_load(self):
        filename = gui.FileSelector(path='.').run()
        with open(filename, 'r') as loadfile:
            self.sector = place.Sector.load(loadfile)
        self.sector_viewer.sector = self.sector

    def handle_save(self):
        filename = gui.FileSelector(path='.').run()
        with open(filename, 'w') as savefile:
            self.sector.save(savefile)

    def on_keypress(self, key):
        handler = {
            'q': self.quit,
            's': self.handle_save,
            'l': self.handle_load
            }.get(chr(key.c))
        if handler:
            handler()

            
class MainMenu(gui.Applet):
    def __init__(self):
        self.options = {
            'Create new world' : self.handle_create,
            'Load saved game': self.handle_load,
            'Quit' : self.quit
            }
        super(MainMenu, self).__init__()
        self.menu = gui.Menu(options=sorted(self.options.keys()), 
                             max_width=SCREEN_COLUMNS/2, 
                             max_height=SCREEN_ROWS)

    def handle_create(self):
        """ Launch the game editor. """
        Editor().run()

    def handle_enter(self):
        """ User pressed enter. Run the handler for the current option. """
        option = self.menu.options[self.menu.current_option]
        self.options[option]()

    def handle_load(self):
        """ Load and run a saved game. """
        filename = gui.FileSelector(path='.').run()
        if filename:
            game = Game()
            try:
                game.load(filename)
            except Exception as e:
                gui.Alert('%s'%e).run()
            else:
                game.run()

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

    parser = argparse.ArgumentParser(description='Play or edit hax2 games')
    parser.add_argument('--start', dest='start', metavar='s', 
                        help='Saved game to start')
    args = parser.parse_args()

    os.unlink('azoth.log')
    logging.basicConfig(filename='azoth.log',level=logging.DEBUG)

    # Note: if I don't set a custom font, libtcod will implicitly try to load a
    # font from a file called terminal.png which it expects to find in the
    # current directoy.
    tcod.console_set_custom_font('../tcod/data/fonts/arial10x10.png', 
                                 tcod.FONT_TYPE_GREYSCALE | 
                                 tcod.FONT_LAYOUT_TCOD)

    tcod.console_init_root(SCREEN_COLUMNS, SCREEN_ROWS, "Haxima", False)
    tcod.sys_set_fps(MAX_FPS)

    if args.start:
        game = Game()
        game.load(args.start)
        game.run()
    MainMenu().run()

