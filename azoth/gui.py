"""
gui classes for azoth

Public Domain.
"""

import colors
import logging
import os
import pygame
import textwrap

DEFAULT_MAX_WIDTH = 320
DEFAULT_MAX_HEIGHT = 240
DEFAULT_FONT_SIZE = 16 # XXX: move to config.py

# XXX: move to config.py
#DEFAULT_FONT = pygame.font.Font(pygame.font.get_default_font(), 
#                                DEFAULT_FONT_SIZE)

class Window(object):
    """ Base class for terminal windows. """
    background_color = colors.black

    # XXX: use pygame.rect for dims
    def __init__(self, x=0, y=0, width=0, height=0, title=None):
        if width <= 0:
            raise ValueError('width must be >= 1')
        if height <= 0:
            raise ValueError('height must be >= 1')
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.log = logging.getLogger(self.__class__.__name__)
        self.title = title
        self.top_margin = 0
        self.left_margin = 0
        self.surface = pygame.Surface((width, height)).convert_alpha()
        self.font = pygame.font.Font(pygame.font.get_default_font(), 
                                     16) # XXX: config.py
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
#        self._print(self.height - 3, self.prompt, color=colors.cyan, 
#                    align='center')

class Applet(object):
    """ A stand-alone UI and keyhandler.  """

    background_color = colors.black
    fps = 10 # XXX: move to config.py

    def __init__(self):
        self.done = False
        self.windows = []
        self.clock = pygame.time.Clock()

    def add_window(self, window):
        self.windows.append(window)

    def quit(self):
        self.done = True

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

    def run(self):
        self.render()
        while not self.done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        return
                    else:
                        self.on_keypress(event)
            self.render()
            self.clock.tick(self.fps)


class FileSelector(Applet):

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


class Alert(Applet):

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


class SpriteListViewer(Applet):

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


class ObjectListViewer(Applet):

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

    def __init__(self, terrain_list, **kwargs):
        super(TerrainGridWindow, self).__init__(**kwargs)
        sprite = terrain_list[0][1].sprite
        self.cell_width = sprite.width
        self.cell_height = sprite.height
        self.columns = self.width / self.cell_width
        print(self.columns)
        self.rows = (len(terrain_list) + self.columns - 1) / self.columns
        self.grid = []
        start_index = 0
        last_index = start_index + self.columns
        for row in range(self.rows):
            self.grid.append(terrain_list[start_index:last_index])
            start_index = last_index
            last_index += self.columns
        self.frame = 0 # sprite frame
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

class TerrainGridViewer(Applet):

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
