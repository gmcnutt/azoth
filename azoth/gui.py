"""
gui classes for azoth
"""

import colors
import config
import event
import executor
import libtcodpy as libtcod
import logging
import os
import path
import place
import pygame
import sprite
import textwrap

DEFAULT_MAX_WIDTH = 320
DEFAULT_MAX_HEIGHT = 240
DEFAULT_FONT_SIZE = 16  # XXX: move to config.py
FOV_LIGHT_WALLS = True
FOV_ALGO = 0  # default

# XXX: move to config.py
#DEFAULT_FONT = pygame.font.Font(pygame.font.get_default_font(),
#                                DEFAULT_FONT_SIZE)


class Window(object):
    """ Base class for terminal windows. """
    background_color = colors.black

    # XXX: use pygame.rect for dims
    def __init__(self, x=0, y=0, width=0, height=0, title=None, font=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.log = logging.getLogger(self.__class__.__name__)
        self.title = title
        self.top_margin = 0
        self.left_margin = 0
        # Some windows may dynamically allocate their surface later
        if width > 0 and height > 0:
            self.surface = pygame.Surface((width, height), 
                                          flags=pygame.SRCALPHA).convert_alpha()
        else:
            self.surface = None
        self.font = font or pygame.font.Font(pygame.font.get_default_font(),
                                             16)  # XXX: config.py
        # XXX: assumes monospace
        self.font_width, self.font_height = self.font.size('x')

    @property
    def left(self):
        """ Screen x-coordinate of left edge. """
        return self.x

    @property
    def top(self):
        """ Screen y-coordinate of top edge. """
        return self.y

    @property
    def right(self):
        """ Screen x-coordinate of right edge. """
        return self.x + self.width

    @property
    def bottom(self):
        """ Screen y-coordinate of bottom edge. """
        return self.y + self.height

    def contains_point(self, x, y):
        """ Check if window contains x, y (in root console coordinates). """
        return (x >= self.x and y >= self.y and x < self.right and
                y < self.bottom)

    def draw_frame(self):
        """ XXX: Placeholder """
        pass

    def resize(self, delta_width=0, delta_height=0):
        """ Expand (or shrink) the window. """
        new_width = self.width + delta_width
        new_height = self.height + delta_height
        if new_width < 2 or new_height < 2:
            return
        self.width = new_width
        self.height = new_height

    def move(self, dx=0, dy=0):
        """ Move the window around within the screen. """
        self.x += dx
        self.y += dy

    def on_paint(self):
        """ Hook for subclasses."""
        pass

    def paint(self, to_surface=None):
        """ Paint the window to the destination surface or the currently set
        display surface if none is given. Subclasses should implement
        on_paint()."""
        self.on_paint()
        if to_surface is None:
            to_surface = pygame.display.get_surface()
        self.log.debug('paint:{}@({},{})'.format(to_surface, self.x, self.y))
        to_surface.blit(self.surface, (self.x, self.y))

    def _print(self, row, fmt, color=colors.white, align='left'):
        """ Convenience wrapper for most common print call. """
        # NOTE: if I need performance check out the docs on Font.render
        rendered_text = self.font.render(fmt, True, color)
        if align == 'left':
            x = 0
        elif align == 'center':
            x = (self.surface.get_width() - rendered_text.get_width()) / 2
        y = row * self.font.get_linesize()
        self.surface.blit(rendered_text, (x, y))


class Menu(Window):
    """ Simple menu. """

    def __init__(self, options=(), max_width=DEFAULT_MAX_WIDTH,
                 max_height=DEFAULT_MAX_HEIGHT, **kwargs):
        width = min(max_width, max([len(option) for option in options]) + 2)
        height = min(max_height, len(options) + 2)
        super(Menu, self).__init__(width=width, height=height, **kwargs)
        self.options = options
        self.current_option = 0
        self.top_visible_option = 0
        self.num_visible_rows = min(self.height - 2, len(options))
        self.last_option = len(options) - 1
        self.current_option = 0
        self.top_trigger = self.num_visible_rows / 2
        self.bottom_trigger = self.last_option - self.top_trigger

    def scroll_up(self):
        """ Scroll selector up. """
        if self.current_option == 0:
            return
        self.current_option -= 1
        if self.current_option < self.bottom_trigger:
            if self.top_visible_option > 0:
                self.top_visible_option -= 1

    def scroll_down(self):
        """ Scroll selector down. """
        if self.current_option == self.last_option:
            return
        self.current_option += 1
        if self.current_option <= self.bottom_trigger and \
                self.current_option > self.top_trigger:
            self.top_visible_option += 1

    def on_paint(self):
        for row, option in enumerate(range(self.top_visible_option,
                                           self.top_visible_option + \
                                               self.num_visible_rows)):
            if option == self.current_option:
                color = colors.yellow
            else:
                color = colors.gray
            self._print(row, self.options[option], color=color)


class TextLabel(Window):
    """ A box of read-only text. The text will be wrapped to fill the width. If
    it exceeds the height it will be truncated. """

    def __init__(self, message=None, max_width=DEFAULT_MAX_WIDTH,
                 max_height=DEFAULT_MAX_HEIGHT, **kwargs):
        super(TextLabel, self).__init__(width=max_width, height=max_height,
                                       **kwargs)
        self.width = 0
        self.height = 0
        if message is not None:
            max_columns = max_width / self.font_width
            if max_columns == 0:
                return
            self.lines = textwrap.wrap(message, max_columns)
            for row, line in enumerate(self.lines):
                self._print(row, line)
                line_width, line_height = self.font.size(line)
                self.width = max(self.width, line_width)
                self.height += line_height

    def on_paint(self):
        """ Paint the text. """
        pass


class PromptDialog(Window):
    """ Show a message and a prompt to continue. """

    prompt = '(Ok)'

    def __init__(self, message=None, max_width=DEFAULT_MAX_WIDTH,
                 max_height=DEFAULT_MAX_HEIGHT, **kwargs):
        super(PromptDialog, self). __init__(width=max_width, height=max_height,
                                            **kwargs)
        self.message_area = TextLabel(message=message, max_width=self.width,
                                      max_height=self.height, **kwargs)
        self.prompt_area = TextLabel(message=self.prompt,
                                     y=(self.message_area.height +
                                        self.font_height),
                                     max_width=self.width,
                                     max_height=self.height, **kwargs)

    def on_paint(self):
        """ Paint the text area then the prompt. """
        self.message_area.paint(to_surface=self.surface)
        self.prompt_area.paint(to_surface=self.surface)


class Viewer(event.EventLoop):
    """ A stand-alone UI and keyhandler.  """

    background_color = colors.black
    fps = config.FRAMES_PER_SECOND

    def __init__(self):
        self.done = False
        self.windows = []
        self.clock = pygame.time.Clock()

    def add_window(self, window):
        self.windows.append(window)

    def quit(self):
        return True

    def render(self):
        pygame.display.get_surface().fill(self.background_color)
        self.on_render()
        pygame.display.flip()

    def on_mouse_left_click(self, x, y):
        for window in self.windows:
            if window.contains_point(x, y):
                window.on_mouse_left_click(x - window.x, y - window.y)
                return

    def on_render(self):
        for window in self.windows:
            window.paint()

    def on_keypress(self, key):
        """ Hook for subclasses to handle key events. """
        pass

    def on_event(self, evt):
        """ Handle an event. """
        if evt.type == pygame.QUIT:
            raise event.Quit()
        elif evt.type == pygame.KEYDOWN:
            self.on_keypress(evt.key)

    def on_loop_start(self):
        """ Render at start of loop. """
        self.render()

    def on_loop_finish(self):
        """ Delay at end of loop to synch FPS. """
        self.clock.tick(self.fps)


class FileSelector(Viewer):

    def __init__(self, path=None, re_filter=None):
        super(FileSelector, self).__init__()
        self.selection = None
        files = ['.'] + sorted(os.listdir(path))
        self.menu = Menu(options=files)

    def handle_enter(self):
        self.selection = self.menu.options[self.menu.current_option]
        self.done = True

    def on_render(self):
        self.menu.paint()

    def on_keypress(self, event):
        handler = {
            pygame.K_DOWN: self.menu.scroll_down,
            pygame.K_UP: self.menu.scroll_up,
            pygame.K_q: self.quit,
            pygame.K_RETURN: self.handle_enter
            }.get(event.key)
        if handler:
            handler()

    def run(self):
        super(FileSelector, self).run()
        return self.selection


class Alert(Viewer):

    def __init__(self, message, **kwargs):
        super(Alert, self).__init__()
        self.window = PromptDialog(message, **kwargs)

    def on_render(self):
        self.window.paint()

    def on_keypress(self, key):
        if key.c == ord('\r'):
            self.done = True


class SpriteListWindow(Window):

    def __init__(self, sprite_list, **kwargs):
        super(SpriteListWindow, self).__init__(**kwargs)
        self.list = sprite_list
        self.frame = 0
        self.top_index = 0
        # find max_index by walking backward from end of list
        self.max_index = len(self.list) - 1
        top = self.height
        while self.max_index > 0 and top > 0:
            top -= self.list[self.max_index][1].height
            self.max_index -= 1

    def scroll_up(self):
        if self.top_index > 0:
            self.top_index -= 1

    def scroll_down(self):
        if self.top_index < self.max_index:
            self.top_index += 1

    def home(self):
        self.top_index = 0

    def end(self):
        self.top_index = self.max_index

    def pagedown(self):
        height = self.height - self.list[self.top_index][1].height
        while height > 0 and self.top_index < self.max_index:
            height -= self.list[self.top_index][1].height
            self.top_index += 1
        if height < 0:
            self.top_index -= 1

    def pageup(self):
        height = self.height - self.list[self.top_index][1].height
        while height > 0 and self.top_index > 0:
            height -= self.list[self.top_index][1].height
            self.top_index -= 1
        if height < 0:
            self.top_index += 1

    def on_paint(self):
        self.surface.fill(self.background_color)
        rect = pygame.Rect(0, 0, self.width, 0)
        index = self.top_index
        while rect.bottom < self.height and index < len(self.list):
            name = self.list[index][0]
            sprite = self.list[index][1]
            rect.height = sprite.height
            self.surface.blit(self.font.render(name, True, colors.white),
                              rect.topleft)
            self.surface.blit(sprite.get_image(self.frame), rect.midtop)
            rect.top += rect.height
            index += 1
        self.frame += 1


class SpriteListViewer(Viewer):

    def __init__(self, sprite_list):
        super(SpriteListViewer, self).__init__()
        width, height = pygame.display.get_surface().get_size()
        self.lister = SpriteListWindow(sprite_list, width=width, height=height)
        self.windows.append(self.lister)

    def on_keypress(self, event):
        handler = {
            pygame.K_DOWN: self.lister.scroll_down,
            pygame.K_UP: self.lister.scroll_up,
            pygame.K_q: self.quit,
            pygame.K_HOME: self.lister.home,
            pygame.K_END: self.lister.end,
            pygame.K_PAGEUP: self.lister.pageup,
            pygame.K_PAGEDOWN: self.lister.pagedown
            }.get(event.key)
        if handler:
            handler()


class ObjectListWindow(Window):

    def __init__(self, _list, **kwargs):
        super(ObjectListWindow, self).__init__(**kwargs)
        self.list = _list
        self.frame = 0
        self.top_index = 0
        # find max_index by walking backward from end of list
        self.max_index = len(self.list) - 1
        top = self.height
        while self.max_index > 0 and top > 0:
            top -= self.list[self.max_index][1].sprite.height
            self.max_index -= 1

    def scroll_up(self):
        if self.top_index > 0:
            self.top_index -= 1

    def scroll_down(self):
        if self.top_index < self.max_index:
            self.top_index += 1

    def home(self):
        self.top_index = 0

    def end(self):
        self.top_index = self.max_index

    def pagedown(self):
        height = self.height - self.list[self.top_index][1].height
        while height > 0 and self.top_index < self.max_index:
            height -= self.list[self.top_index][1].height
            self.top_index += 1
        if height < 0:
            self.top_index -= 1

    def pageup(self):
        height = self.height - self.list[self.top_index][1].height
        while height > 0 and self.top_index > 0:
            height -= self.list[self.top_index][1].height
            self.top_index -= 1
        if height < 0:
            self.top_index += 1

    def on_paint(self):
        self.surface.fill(self.background_color)
        rect = pygame.Rect(0, 0, self.width, 0)
        index = self.top_index
        while rect.bottom < self.height and index < len(self.list):
            name = self.list[index][0]
            sprite = self.list[index][1].sprite
            rect.height = sprite.height
            self.surface.blit(self.font.render(name, True, colors.white),
                              rect.topleft)
            self.surface.blit(sprite.get_image(self.frame), rect.midtop)
            rect.top += rect.height
            index += 1
        self.frame += 1


class ObjectListViewer(Viewer):

    def __init__(self, _list):
        super(ObjectListViewer, self).__init__()
        width, height = pygame.display.get_surface().get_size()
        self.lister = ObjectListWindow(_list, width=width, height=height)
        self.windows.append(self.lister)

    def on_keypress(self, event):
        handler = {
            pygame.K_DOWN: self.lister.scroll_down,
            pygame.K_UP: self.lister.scroll_up,
            pygame.K_q: self.quit,
            pygame.K_HOME: self.lister.home,
            pygame.K_END: self.lister.end,
            pygame.K_PAGEUP: self.lister.pageup,
            pygame.K_PAGEDOWN: self.lister.pagedown
            }.get(event.key)
        if handler:
            handler()


class TerrainGridWindow(Window):
    """ Displays a list of terrains as a grid. """

    def __init__(self, terrain_list, **kwargs):
        super(TerrainGridWindow, self).__init__(**kwargs)
        sprite = terrain_list[0][1].sprite
        self.cell_width = sprite.width
        self.cell_height = sprite.height
        self.columns = self.width / self.cell_width
        self.rows = (len(terrain_list) + self.columns - 1) / self.columns
        self.grid = []
        start_index = 0
        last_index = start_index + self.columns
        for row in range(self.rows):
            self.grid.append(terrain_list[start_index:last_index])
            start_index = last_index
            last_index += self.columns
        self.frame = 0  # sprite frame
        self.top_index = 0
        # find max_index by walking backward from end of list
        self.max_index = self.rows - 1
        top = self.height
        while self.max_index > 0 and top > 0:
            top -= self.cell_height
            self.max_index -= 1

    def scroll_up(self):
        if self.top_index > 0:
            self.top_index -= 1

    def scroll_down(self):
        if self.top_index < self.max_index:
            self.top_index += 1

    def home(self):
        self.top_index = 0

    def end(self):
        self.top_index = self.max_index

    def pagedown(self):
        height = self.height - self.cell_height
        while height > 0 and self.top_index < self.max_index:
            height -= self.cell_height
            self.top_index += 1
        if height < 0:
            self.top_index -= 1

    def pageup(self):
        height = self.height - self.cell_height
        while height > 0 and self.top_index > 0:
            height -= self.cell_height
            self.top_index -= 1
        if height < 0:
            self.top_index += 1

    def on_paint(self):
        self.surface.fill(self.background_color)
        rect = pygame.Rect(0, 0, self.cell_width, self.cell_height)
        row = self.top_index
        while rect.bottom < self.height and row < self.rows:
            column = 0
            rect.x = 0
            while rect.right <= self.width and column < len(self.grid[row]):
                name, terrain = self.grid[row][column]
                sprite = terrain.sprite
                self.surface.blit(sprite.get_image(self.frame), rect.topleft)
                rect.left += rect.width
                column += 1
            rect.bottom += rect.height
            row += 1
        self.frame += 1


class TerrainGridViewer(Viewer):
    """ Scrolling viewer for a list of terrains. """

    def __init__(self, terrain_list):
        super(TerrainGridViewer, self).__init__()
        width, height = pygame.display.get_surface().get_size()
        self.lister = TerrainGridWindow(terrain_list, width=width,
                                        height=height)
        self.windows.append(self.lister)

    def on_keypress(self, event):
        handler = {
            pygame.K_DOWN: self.lister.scroll_down,
            pygame.K_UP: self.lister.scroll_up,
            pygame.K_q: self.quit,
            pygame.K_HOME: self.lister.home,
            pygame.K_END: self.lister.end,
            pygame.K_PAGEUP: self.lister.pageup,
            pygame.K_PAGEDOWN: self.lister.pagedown
            }.get(event.key)
        if handler:
            handler()


class PlaceWindow(Window):

    def __init__(self, place, radius=10, **kwargs):
        super(PlaceWindow, self).__init__(**kwargs)
        self.place = place
        self.radius = radius
        self.animation_frame = 0
        spr = self.place.get_terrain(0, 0).sprite
        self.cell_width = spr.width
        self.cell_height = spr.height
        self.columns = int(self.width / self.cell_width)
        self.rows = int(self.height / self.cell_height)
        self.view = pygame.Rect(0, 0, self.columns, self.rows)
        self.place_rect = pygame.Rect(0, 0, self.place.width, self.place.height)
        # experiment with a fov (aka los) map
        self.fade = sprite.Fade(spr.width, spr.height).surf
        self.fov_map = libtcod.map_new(self.place.width, self.place.height)
        for y in range(self.place.height):
            for x in range(self.place.width):
                ter = self.place.get_terrain(x, y)
                libtcod.map_set_properties(self.fov_map, x, y, 
                                           not ter.blocks_sight, False)

    def on_paint(self):
        self.surface.fill(self.background_color)
        tile = pygame.Rect(0, 0, self.cell_width, self.cell_height)
        for map_y in xrange(self.view.top, self.view.bottom):
            tile.left = 0
            for map_x in xrange(self.view.left, self.view.right):
                visible = libtcod.map_is_in_fov(self.fov_map, map_x, map_y)
                explored = self.place.get_explored(map_x, map_y)
                if visible or explored:
                    # terrain
                    terrain = self.place.get_terrain(map_x, map_y)
                    spr = terrain.sprite
                    self.surface.blit(spr.get_image(self.animation_frame),
                                      tile.topleft)
                    if not visible:
                        self.surface.blit(self.fade, tile.topleft)  # haze
                    else:
                        self.place.set_explored(map_x, map_y, True)
                        items = self.place.get_items(map_x, map_y)
                        for item in items:
                            spr = item.sprite
                            image = spr.get_image(self.animation_frame)
                            self.surface.blit(image, tile.topleft)
                        occupant = self.place.get_occupant(map_x, map_y)
                        if occupant and visible:
                            spr = occupant.sprite
                            image = spr.get_image(self.animation_frame)
                            self.surface.blit(image, tile.topleft)
                tile.left += tile.width
            tile.top += tile.height
        self.animation_frame += 1

    def compute_fov(self, x, y, radius):
        libtcod.map_compute_fov(self.fov_map, x, y, radius, FOV_LIGHT_WALLS,
                                FOV_ALGO)

    def scroll_up(self):
        if self.view.top > 0:
            self.view.top -= 1

    def scroll_down(self):
        if self.view.bottom < self.place.height:
            self.view.bottom += 1

    def scroll_left(self):
        if self.view.left > 0:
            self.view.left -= 1

    def scroll_right(self):
        if self.view.right < self.place.width:
            self.view.right += 1

    def screen_to_map(self, scr_x, scr_y):
        """ Convert screen coords in pixels to map coords in tiles. """
        map_x = self.view.left + int((self.x + scr_x) / self.cell_width)
        map_y = self.view.top + int((self.y + scr_y) / self.cell_height)
        return map_x, map_y

    @property
    def center(self):
        return self.view.center

    @center.setter
    def center(self, xypair):
        self.view.center = xypair
        self.view = self.view.clamp(self.place_rect)


class FpsViewer(Window):
    """ Show the FPS """

    def __init__(self, **kwargs):
        super(FpsViewer, self).__init__()
        self.fps = 0

    @property
    def fps(self):
        return self._fps

    @fps.setter
    def fps(self, val):
        self._fps = val
        self.surface = self.font.render('%d' % val, True, colors.white)
        self.width, self.height = self.surface.get_size()

class SessionViewer(Viewer):

    def __init__(self, session):
        super(SessionViewer, self).__init__()
        self.session = session
        width, height = pygame.display.get_surface().get_size()
        self.map = PlaceWindow(self.session.world, width=width, height=height)
        self.windows.append(self.map)
        self.subject = self.session.player
        self.map.center = self.subject.x, self.subject.y
        self.map.compute_fov(self.subject.x, self.subject.y, 11)
        self.fps_label = FpsViewer()
        self.windows.append(self.fps_label)
        self.controller = None

    def on_loop_finish(self):
        """ Do custom updates at the bottom of every event loop. """
        super(SessionViewer, self).on_loop_finish()
        self.fps_label.fps = self.clock.get_fps()

    def resume(self):
        """ Continue running the main loop. """
        # This is called from within actor.do_turn() in order to run the event
        # handlers. It returns when the actor's turn is over or the player
        # wants to quit.
        super(SessionViewer, self).run()

    def on_keypress(self, key):
        """ Handle a key to control the subject during its turn. Returns True
        when done with turn."""        
        handler = {
            pygame.K_DOWN: lambda: self.controller.move(0, 1),
            pygame.K_UP: lambda: self.controller.move(0, -1),
            pygame.K_LEFT: lambda: self.controller.move(-1, 0),
            pygame.K_RIGHT: lambda: self.controller.move(1, 0),
            pygame.K_d: self.controller.drop,
            pygame.K_g: self.controller.get,
            pygame.K_q: self.controller.quit,
            pygame.K_s: self.controller.save,
            }.get(key)
        if handler:
            handler()

    def on_mouse(self, button, x, y):
        """ Dispatch mouse-clicks. """
        to_x, to_y = self.map.screen_to_map(x, y)
        from_x, from_y = self.controller.subject.xy
        path = path.find(from_x, from_y, to_x, to_y)
        for step in path:
            self.controller.move(step.dx, step.dy)
            self.render()

    def on_event(self, event):
        """ Run the top of the event handler stack. If it does not handle the
        event then fall back on the default handler. """
        if event.type == pygame.KEYDOWN:
            self.on_keypress(event.key)
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.on_mouse(event.button, event.pos[0], event.pos[1])
        # The handler would have raised event.Handled if it had handled the
        # event.
        super(SessionViewer, self).on_event(event)

    def run(self):
        """ Run the main loop. """
        self.on_loop_entry()
        try:
            while not self.done:
                for actor in sorted(self.session.world.actors):
                    self.controller = actor
                    actor.do_turn(self)
                self.map.center = self.subject.x, self.subject.y
                self.map.compute_fov(self.subject.x, self.subject.y, 11)
                self.run_one_iteration()
        except event.Quit:
            pass
        finally:
            self.on_loop_exit()
