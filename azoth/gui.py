"""
gui classes for azoth
"""

import colors
import controller
import config
import event
import logging
import os
import pygame
import session
import sprite
#import textwrap
import time

FOV_LIGHT_WALLS = True
FOV_ALGO = 0  # default


class Window(object):
    """ Base class for terminal windows. """
    background_color = colors.black

    # XXX: use pygame.rect for dims
    def __init__(self, x=0, y=0, width=None, height=None, title=None, 
                 font=None):
        self.x = x
        self.y = y
        self.log = logging.getLogger(self.__class__.__name__)
        self.title = title
        size = pygame.display.get_surface().get_size()
        self.width = width or size[0]
        self.height = height or size[1]
        self.surface = pygame.Surface((self.width, self.height), 
                                      flags=pygame.SRCALPHA).convert_alpha()
        self.font = font or pygame.font.Font(pygame.font.get_default_font(),
                                             16)  # XXX: config.py
        # XXX: assumes monospace
        self.font_width, self.font_height = self.font.size('x')
        self.rect = self.surface.get_rect()

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
    
    def on_mouse_event(self, evt):
        """ Hook for subclasses. """
        pass

class ScrollingWindow(Window):
    """ Abstract base class for scrolling windows. """

    def scroll_up(self):
        """ Scroll up one row. """
        pass

    def scroll_down(self):
        """ Scroll down one row. """
        pass

    def home(self):
        """ Scroll to top. """
        pass

    def end(self):
        """ Scroll to bottom. """
        pass

    def pagedown(self):
        """ Scroll down one page. """
        pass

    def pageup(self):
        """ Scroll up one page. """
        pass


class Menu(ScrollingWindow):
    """ Simple menu. 'options' should be a list of strings. """

    def __init__(self, options=(), align='center', **kwargs):
        super(Menu, self).__init__(**kwargs)
        self.options = options
        self.align = align
        self.current_option = 0
        self.top_visible_option = 0
        self.num_visible_rows = min(self.height - 2, len(options))
        self.last_option = len(options) - 1
        self.current_option = 0
        self.top_trigger = self.num_visible_rows / 2
        self.bottom_trigger = self.last_option - self.top_trigger
        rows_per_screen = self.height / self.font.get_linesize()
        self.top_margin = (rows_per_screen - self.num_visible_rows) // 2
        self.y_offset = self.top_margin * self.font.get_linesize()

    def get_selection(self):
        return self.options[self.current_option]

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
        self.surface.fill(color=colors.black)
        for row, option in enumerate(range(self.top_visible_option,
                                           self.top_visible_option + \
                                               self.num_visible_rows)):
            if option == self.current_option:
                color = colors.yellow
            else:
                color = colors.grey
            self._print(row + self.top_margin, self.options[option], 
                        color=color, align=self.align)

    def on_mouse_event(self, evt):
        relative_y = evt.pos[1] - self.y_offset
        row = relative_y // self.font.get_linesize()
        row = min(row, len(self.options) - 1)
        self.current_option = max(row, 0)


class Viewer(event.EventLoop):
    """ A stand-alone UI and keyhandler.  """

    background_color = colors.black
    fps = config.FRAMES_PER_SECOND

    def __init__(self):
        self.windows = []
        self.clock = pygame.time.Clock()
        self.log = logging.getLogger(self.__class__.__name__)

    def add_window(self, window):
        self.windows.append(window)

    def quit(self):
        raise event.Handled()

    def render(self):
        pygame.display.get_surface().fill(self.background_color)
        self.on_render()
        pygame.display.flip()

    def on_mouse_event(self, evt):
        for window in self.windows:
            if window.rect.collidepoint(evt.pos):
                window.on_mouse_event(evt)

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
        elif evt.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION,
                          pygame.MOUSEBUTTONUP):
            self.on_mouse_event(evt)

    def on_loop_start(self):
        """ Render at start of loop. """
        self.render()

    def on_loop_finish(self):
        """ Delay at end of loop to synch FPS. """
        self.clock.tick(self.fps)

    def run(self):
        try:
            super(Viewer, self).handle_events()
        except event.Quit:
            print("Caught quit")
            pass


class FileSelector(Viewer):

    def __init__(self, path=None, re_filter=None):
        super(FileSelector, self).__init__()
        self.selection = None
        files = ['.'] + sorted(os.listdir(path))
        self.menu = Menu(options=files, align='left')

    def handle_enter(self):
        self.selection = self.menu.options[self.menu.current_option]
        raise event.Quit()

    def on_render(self):
        self.menu.paint()

    def on_keypress(self, key):
        handler = {
            pygame.K_DOWN: self.menu.scroll_down,
            pygame.K_UP: self.menu.scroll_up,
            pygame.K_q: self.quit,
            pygame.K_RETURN: self.handle_enter
            }.get(key)
        if handler:
            handler()

    def run(self):
        super(FileSelector, self).run()
        return self.selection


class TableColumn(object):
    """ A column in a TableRow. """

    def __init__(self):
        self._width = None
        self._height = None
    
    def _compute_size(self):
        """ Internal helper to compute _width and _height in pixels. """
        self._width, self._height = self.render().get_size()

    @property
    def height(self):
        """ Return height in pixels. """
        if self._height is not None:
            return self._height
        self._compute_size()
        return self._height

    @property
    def width(self):
        """ Return width in pixels. """
        if self._width is not None:
            return self._width
        self._compute_size()
        return self._width


class TextColumn(TableColumn):
    """ A column of text. """

    def __init__(self, text, font):
        super(TextColumn, self).__init__()
        self.text = text
        self.font = font

    def render(self):
        """ Return the a rendered surface. """
        return self.font.render(self.text, True, colors.white)


class SpriteColumn(TableColumn):
    """ A column with a single sprite. """

    def __init__(self, sprite, frame=0):
        super(SpriteColumn, self).__init__()
        self.sprite = sprite
        self.frame = frame

    def render(self):
        """ Return the a rendered surface. """
        surf = self.sprite.get_image(self.frame)
        self.frame += 1
        return surf


class NoneColumn(TableColumn):
    """ A column for None. """

    def __init__(self):
        super(NoneColumn, self).__init__()
        self._height = 0
        self._width = 0

    def render(self):
        return None

class TableRow(object):
    """ A row in a TableWindow. """

    def __init__(self, row, font):
        self.columns = []
        self._height = None
        for x in row:
            if isinstance(x, basestring):
                self.columns.append(TextColumn(x, font))
            elif isinstance(x, sprite.Sprite):
                self.columns.append(SpriteColumn(x))
            elif x is None:
                self.columns.append(NoneColumn())
            else:
                raise TypeError('{} is unsupported type {}'.format(x, type(x)))

    def _compute_size(self):
        """ Internal helper to compute _width and _height in pixels. """
        self._height = 0
        self._width = 0
        for column in self.columns:
            if column.height > self._height:
                self._height = column.height
            self._width += column.width

    @property
    def height(self):
        """ Return height in pixels. """
        if self._height is not None:
            return self._height
        self._compute_size()
        return self._height

    @property
    def width(self):
        """ Return width in pixels. """
        if self._width is not None:
            return self._width
        self._compute_size()
        return self._width


class TableWindow(Window):
    """ Window for displaying a list of rows. """

    def __init__(self, title=None, columns=None, rows=None, row_height=0, *args,
                 **kwargs):
        super(TableWindow, self).__init__(*args, **kwargs)
        self._row_height = None
        self.title = title
        self.headers = [TextColumn(column, self.font) for column in columns]
        self.num_columns = len(self.headers)
        self.rows = [TableRow(row, self.font) for row in rows]
        self.column_widths = []
        # Find the width of each column using the max of any row:
        for idx in xrange(self.num_columns):
            mcw = max([r.columns[idx].width for r in self.rows])
            mcw = max(mcw, self.headers[idx].width)
            self.column_widths.append(mcw)
        self.top_index = 0
        self.rows_per_page = self.height / self.row_height
        self.max_top_index = len(self.rows) - self.rows_per_page
        if self.max_top_index < 0:
            self.max_top_index = 0

    @property
    def row_height(self):
        """ Return the height of each row in pixels (assumes all rows are the
        same height). """
        # Lazy eval, cache result
        if self._row_height is None:
            self._row_height = self.rows[0].height
        return self._row_height

    def scroll_up(self):
        """ Scroll up one row. """
        if self.top_index > 0:
            self.top_index -= 1

    def scroll_down(self):
        """ Scroll down one row. """
        if self.top_index < self.max_top_index:
            self.top_index += 1

    def home(self):
        """ Scroll to top. """
        self.top_index = 0

    def end(self):
        """ Scroll to bottom. """
        self.top_index = self.max_top_index

    def pagedown(self):
        """ Scroll down one page. """
        self.top_index += self.rows_per_page
        if self.top_index > self.max_top_index:
            self.top_index = self.max_top_index

    def pageup(self):
        """ Scroll up one page. """
        self.top_index -= self.rows_per_page
        if self.top_index < 0:
            self.top_index = 0

    def on_paint(self):
        """ Blit the header and visible rows. """
        self.surface.fill(self.background_color)
        # Print the column headers:
        rect = pygame.Rect(0, 0, self.width, self.row_height)
        for idx, header in enumerate(self.headers):
            surf = header.render()
            rect.width = self.column_widths[idx]
            self.surface.blit(surf, rect.topleft)
            rect.left += rect.width
        rect.top += rect.height
        rect.left = 0
        # Compute the visible rows:
        last_index = self.top_index + self.rows_per_page
        max_index = len(self.rows)
        if last_index > max_index:
            last_index = max_index
        rows = self.rows[self.top_index:last_index]
        # Print the visible rows:
        for row in rows:
            for idx, column in enumerate(row.columns):
                rect.width = self.column_widths[idx]
                surf = column.render()
                if surf is not None:
                    self.surface.blit(surf, rect.topleft)
                rect.left += rect.width
            rect.top += rect.height
            rect.left = 0


class TableViewer(Viewer):
    """ Controller to scroll around a table window. """

    def __init__(self, title=None, columns=None, rows=None):
        super(TableViewer, self).__init__()
        self.lister = TableWindow(title=title, columns=columns, rows=rows)
        self.windows.append(self.lister)

    def on_keypress(self, key):
        handler = {
            pygame.K_DOWN: self.lister.scroll_down,
            pygame.K_UP: self.lister.scroll_up,
            pygame.K_q: self.quit,
            pygame.K_HOME: self.lister.home,
            pygame.K_END: self.lister.end,
            pygame.K_PAGEUP: self.lister.pageup,
            pygame.K_PAGEDOWN: self.lister.pagedown
            }.get(key)
        if handler:
            handler()
        

class ScrollingViewer(Viewer):
    """ Generic viewer of a scrolling window. """

    def __init__(self, subject=None):
        super(ScrollingViewer, self).__init__()
        self.subject = subject
        self.windows.append(self.subject)

    def on_keypress(self, key):
        handler = {
            pygame.K_DOWN: self.subject.scroll_down,
            pygame.K_UP: self.subject.scroll_up,
            pygame.K_q: self.quit,
            pygame.K_HOME: self.subject.home,
            pygame.K_END: self.subject.end,
            pygame.K_PAGEUP: self.subject.pageup,
            pygame.K_PAGEDOWN: self.subject.pagedown
            }.get(key)
        if handler:
            handler()


class MenuViewer(ScrollingViewer):
    def on_keypress(self, key):
        handler = {
            pygame.K_RETURN: self.quit
            }.get(key)
        if handler:
            handler()
        else:
            super(MenuViewer, self).on_keypress(key)


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
        self.lister = SpriteListWindow(sprite_list)
        self.windows.append(self.lister)

    def on_keypress(self, key):
        handler = {
            pygame.K_DOWN: self.lister.scroll_down,
            pygame.K_UP: self.lister.scroll_up,
            pygame.K_q: self.quit,
            pygame.K_HOME: self.lister.home,
            pygame.K_END: self.lister.end,
            pygame.K_PAGEUP: self.lister.pageup,
            pygame.K_PAGEDOWN: self.lister.pagedown
            }.get(key)
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
        self.lister = ObjectListWindow(_list)
        self.windows.append(self.lister)

    def on_keypress(self, key):
        handler = {
            pygame.K_DOWN: self.lister.scroll_down,
            pygame.K_UP: self.lister.scroll_up,
            pygame.K_q: self.quit,
            pygame.K_HOME: self.lister.home,
            pygame.K_END: self.lister.end,
            pygame.K_PAGEUP: self.lister.pageup,
            pygame.K_PAGEDOWN: self.lister.pagedown
            }.get(key)
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
        self.lister = TerrainGridWindow(terrain_list)
        self.windows.append(self.lister)

    def on_keypress(self, key):
        handler = {
            pygame.K_DOWN: self.lister.scroll_down,
            pygame.K_UP: self.lister.scroll_up,
            pygame.K_q: self.quit,
            pygame.K_HOME: self.lister.home,
            pygame.K_END: self.lister.end,
            pygame.K_PAGEUP: self.lister.pageup,
            pygame.K_PAGEDOWN: self.lister.pagedown
            }.get(key)
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
        #self.fov_map = libtcod.map_new(self.place.width, self.place.height)
        for y in range(self.place.height):
            for x in range(self.place.width):
                ter = self.place.get_terrain(x, y)
                #libtcod.map_set_properties(self.fov_map, x, y, 
                #                           not ter.blocks_sight, False)

    def on_paint(self):
        self.surface.fill(self.background_color)
        tile = pygame.Rect(0, 0, self.cell_width, self.cell_height)
        for map_y in xrange(self.view.top, self.view.bottom):
            tile.left = 0
            for map_x in xrange(self.view.left, self.view.right):
                visible = True #libtcod.map_is_in_fov(self.fov_map, map_x, map_y)
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
        #libtcod.map_compute_fov(self.fov_map, x, y, radius, FOV_LIGHT_WALLS,
        #                        FOV_ALGO)
        pass

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

    def in_fov(self, map_x, map_y):
        #return libtcod.map_is_in_fov(self.fov_map, map_x, map_y)
        return True

    def explored(self, map_x, map_y):
        return self.place.get_explored(map_x, map_y)

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
    """ Main screen to run a session. """

    def __init__(self, session):
        super(SessionViewer, self).__init__()
        self.session = session
        self.map = PlaceWindow(self.session.world)
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

    def quit(self):
        raise event.Quit()

    def show_inventory(self):
        """ Pop up the modal inventory viewer. """
        x = BodyViewer(self.subject.body)
        x.run()
        raise event.Handled()

    def save(self):
        """ Save the session. """
        path = config.SAVE_DIRECTORY + 'save.p'
        self.session.save(path)

    def on_keypress(self, key):
        """ Handle a key to control the subject during its turn. Raises Handled
        when done. """
        # Cancel pathfinding on any keystroke
        self.controller.path = None
        handler = {
            pygame.K_DOWN: lambda: self.controller.move(0, 1),
            pygame.K_UP: lambda: self.controller.move(0, -1),
            pygame.K_LEFT: lambda: self.controller.move(-1, 0),
            pygame.K_RIGHT: lambda: self.controller.move(1, 0),
            pygame.K_d: self.controller.drop,
            pygame.K_g: self.controller.get,
            pygame.K_i: self.show_inventory,
            pygame.K_q: self.quit,
            pygame.K_s: self.save,
            }.get(key)
        if handler:
            handler()

    def on_mouse(self, button, x, y):
        """ Dispatch mouse-clicks. """
        dst = self.map.screen_to_map(x, y)
        if self.map.explored(*dst):
            if self.controller.pathfind_to(*dst):
                if self.session.world.get_items(*dst):
                    self.controller.path.append(self.controller.get)
                self.controller.follow_path()

    def on_event(self, evt):
        """ Run the top of the event handler stack. If it does not handle the
        event then fall back on the default handler. """
        if evt.type == pygame.KEYDOWN:
            self.on_keypress(evt.key)
        if evt.type == pygame.MOUSEBUTTONDOWN:
            self.on_mouse(evt.button, evt.pos[0], evt.pos[1])
        # The handler would have raised event.Handled if it had handled the
        # event.
        super(SessionViewer, self).on_event(evt)

    def on_subject_moved(self):
        """ Update our view of the subject. """
        self.map.center = self.subject.x, self.subject.y
        self.map.compute_fov(self.subject.x, self.subject.y, 11)
        self.render()

    def run(self):
        """ Run the main loop. """
        self.subject.on('move', self.on_subject_moved)
        try:
            while True:
                for actor in sorted(self.session.world.actors):
                    if not isinstance(actor, controller.Player):
                        actor.do_turn(self)
                    else:
                        self.controller = actor
                        # Run one check of the event queue to allow the player
                        # to cancel or redirect pathfinding.
                        try:
                            self.run_one_iteration()
                        except event.Handled:
                            continue
                        if actor.path:
                            try:
                                actor.follow_path()
                            except event.Handled:
                                time.sleep(config.ANIMATION_SECONDS_PER_FRAME)
                                continue
                        self.handle_events()
        except event.Quit:
            pass
        finally:
            self.subject.un('move', self.on_subject_moved)


class BodyViewer(Viewer):
    """ Show a body and its slots.  """
    
    def __init__(self, body):
        super(BodyViewer, self).__init__()
        title = body.name
        columns = ('Slot', 'Contents')
        rows = []
        for slot, content in body.items():
            if content is None:
                spr = "<empty>"
            else:
                spr = content.sprite
            rows.append((slot, spr))
        self.lister = TableWindow(title=title, columns=columns, rows=rows)
        self.windows.append(self.lister)

    def on_keypress(self, key):
        handler = {
            pygame.K_DOWN: self.lister.scroll_down,
            pygame.K_UP: self.lister.scroll_up,
            pygame.K_q: self.quit,
            pygame.K_HOME: self.lister.home,
            pygame.K_END: self.lister.end,
            pygame.K_PAGEUP: self.lister.pageup,
            pygame.K_PAGEDOWN: self.lister.pagedown
            }.get(key)
        if handler:
            handler()
        
class SplashScreen(object):

    def __init__(self, image_fname):
        splash = pygame.image.load(image_fname)
        main_surface = pygame.display.get_surface()
        main_surface.blit(splash, (0, 0))

        # Show [Press any key to continue] over the splash
        font_size = 16
        font = pygame.font.Font(pygame.font.get_default_font(), font_size)
        color = colors.light_grey
        prompt = font.render("[Press any key to continue]", True, color)
        rect = prompt.get_rect()
        main_rect = main_surface.get_rect()
        rect.centerx = main_rect.centerx
        rect.bottom = main_rect.bottom
        main_surface.blit(prompt, rect)

    def run(self):
        # Wait for quit
        pygame.display.flip()
        doquit = False
        while not doquit:
            for evt in pygame.event.get():
                if evt.type in (pygame.QUIT, pygame.KEYDOWN,
                                pygame.MOUSEBUTTONDOWN):
                    doquit = True

class MainMenu(Viewer):

    def __init__(self, generator=None):
        super(MainMenu, self).__init__()
        self.generator = generator
        self.menu = Menu(options=('Start New Game', 'Load Saved Game', 'Quit'))
        self.windows.append(self.menu)

    def select(self):
        selection = self.menu.get_selection()
        if selection == 'Quit':
            raise event.Quit()
        elif selection == 'Start New Game':
            session_viewer = SessionViewer(self.generator())
            session_viewer.run()
        elif selection == 'Load Saved Game':
            selector = FileSelector(config.SAVE_DIRECTORY)
            fname = selector.run()
            print(fname)
            if fname:
                try:
                    path = config.SAVE_DIRECTORY + fname
                    s = session.load(path)
                except IOError, e:
                    self.log.exception('{}'.format(e))
                    return
                session_viewer = SessionViewer(s)
                session_viewer.run()

    def on_keypress(self, key):
        handler = {
            pygame.K_DOWN: self.menu.scroll_down,
            pygame.K_UP: self.menu.scroll_up,
            pygame.K_q: self.quit,
            pygame.K_RETURN: self.select
            }.get(key)
        if handler:
            handler()

    def on_mouse_event(self, evt):
        super(MainMenu, self).on_mouse_event(evt)
        if evt.type == pygame.MOUSEBUTTONDOWN:
            self.select()
