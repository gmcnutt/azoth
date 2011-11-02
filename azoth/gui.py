"""
gui classes for azoth

Public Domain.
"""

import libtcodpy as tcod
import logging
import textwrap

DEFAULT_MAX_WIDTH = 40
DEFAULT_MAX_HEIGHT = 20


class Window(object):
    """ Base class for terminal windows. """

    def __init__(self, x=0, y=0, width=0, height=0, title=None, boxed=True):
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
        self.boxed = boxed
        self.top_margin = 1 if boxed else 0
        self.left_margin = 1 if boxed else 0
        self.console = tcod.console_new(width, height)

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

    # @property
    # def rows(self):
    #     """ Return iterator over rows. """
    #     return range(self.height)

    # @property
    # def cols(self):
    #     """ Return iterator over columns. """
    #     return range(self.width)

    def contains_point(self, x, y):
        """ Check if window contains x, y (in root console coordinates). """
        return (x >= self.x and y >= self.y and x < self.right and
                y < self.bottom)

    def addglyph(self, col, row, glyph, fade=False):
        """ Like addch() but uses a tuple for (character, foreground color,
        background color). """
        if fade:
            tcod.console_put_char_ex(self.console, col, row, 
                                     glyph[0], glyph[2], None)
        else:
            tcod.console_put_char_ex(self.console, col, row, 
                                     glyph[0], glyph[1], None)

    def addstr(self, col, row, string):
        """ Safe version of curses.addstr that will catch the exception if row
        is not in the window.  """
        tcod.console_print_left(self.console, col, row, tcod.BKGND_NONE, string)

    def resize(self, delta_width=0, delta_height=0):
        """ Expand (or shrink) the window. """
        new_width = self.width + delta_width
        new_height = self.height + delta_height
        if new_width < 2 or new_height < 2:
            return
        self.width = new_width
        self.height = new_height

    def set_background_color(self, x, y, color):
        """ Set the background color. """
        tcod.console_set_back(self.console, x, y, color, tcod.BKGND_SET)

    def move(self, dx=0, dy=0):
        """ Move the window around within the screen. """
        self.x += dx
        self.y += dy

    def on_paint(self):
        """ Hook for subclasses."""
        pass

    def paint(self, parent_console=None):
        """ Paint the window. Subclasses should implement on_paint(). """
        tcod.console_set_foreground_color(self.console, tcod.white)
        tcod.console_clear(self.console)
        self.on_paint()
        tcod.console_set_foreground_color(self.console, tcod.light_blue)
        if self.boxed:
            tcod.console_print_frame(self.console, 0, 0, self.width, 
                                     self.height, False, 0, self.title)
        tcod.console_blit(self.console, 0, 0, self.width, self.height,
                          parent_console, self.x, self.y)

    def put_char(self, x, y, char, color=None, invert=False):
        """ Wrapper to put the char at x, y on the console using the optional
        color. If invert is True then the foreground and background colors are
        swapped. """
        if invert:
            bg_color = tcod.console_get_background_color(self.console)
            fg_color = color or tcod.console_get_foreground_color(self.console)
            tcod.console_put_char_ex(self.console, self.left_margin + x, 
                                     self.top_margin + y, char, bg_color, 
                                     fg_color)
        elif color is None:
            tcod.console_put_char(self.console, self.left_margin + x, 
                                  self.top_margin + y, char)
        else:
            tcod.console_put_char_ex(self.console, self.left_margin + x, 
                                     self.top_margin + y, char, color, None)

    def invert_colors(self):
        """ Swap the console background and foreground colors. """
        fg_color = tcod.console_get_foreground_color(self.console)
        bg_color = tcod.console_get_background_color(self.console)
        tcod.console_set_foreground_color(self.console, bg_color)
        tcod.console_set_background_color(self.console, fg_color)

    def _print(self, row, fmt, color=None, align='left'):
        """ Convenience wrapper for most common print call. """
        if color:
            saved_color = tcod.console_get_foreground_color(self.console)
            tcod.console_set_foreground_color(self.console, color)
        if align == 'left':
            tcod.console_print_left(self.console, self.left_margin, 
                                    self.top_margin + row, tcod.BKGND_NONE, fmt)
        elif align == 'center':
            tcod.console_print_center(self.console, self.width / 2,
                                      self.top_margin + row, tcod.BKGND_NONE, 
                                      fmt)
        if color:
            tcod.console_set_foreground_color(self.console, saved_color)
            

class Menu(Window):
    """ Simple menu. """

    def __init__(self, options=(), max_width=0, max_height=0, **kwargs):
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
                tcod.console_set_foreground_color(self.console, tcod.yellow)
            else:
                tcod.console_set_foreground_color(self.console, tcod.gray)
            self._print(row, self.options[option])


class TextArea(Window):
    """ A box of read-only text. """

    def __init__(self, message=None, max_width=DEFAULT_MAX_WIDTH, 
                 max_height=DEFAULT_MAX_HEIGHT, boxed=True, **kwargs):
        margins = 2 if boxed else 0
        if max_height < margins:
            raise ValueError('max_height must be >= %d' % margins)
        if message is None:
            message = ''
        self.lines = textwrap.wrap(message, max_width - margins)
        if self.lines:
            inner_width = max([len(line) for line in self.lines])
            inner_height = min(len(self.lines), max_height - margins)
            self.lines = self.lines[:inner_height]
        else:
            inner_width = 1
            inner_height = 1
        super(TextArea, self).__init__(width=inner_width + margins, 
                                       height=inner_height + margins, 
                                       boxed=boxed, **kwargs)

    def on_paint(self):
        """ Paint the text. """
        for row, line in enumerate(self.lines):
            self._print(row, line, align='center')


class PromptDialog(Window):
    """ Show a message and a prompt to continue. """

    prompt = '(Ok)'

    def __init__(self, message=None, max_width=DEFAULT_MAX_WIDTH, 
                 max_height=DEFAULT_MAX_HEIGHT, **kwargs):
        self.text_area = TextArea(message=message, max_width=max_width - 2,
                                  max_height=max_height-2-2,
                                  x=1, y=1, boxed=False)
        inner_width = max(self.text_area.width + 2, len(self.prompt))
        inner_height = self.text_area.height + 2 + 2
        super(PromptDialog, self). __init__(width=inner_width, 
                                            height=inner_height, 
                                            **kwargs)

    def on_paint(self):
        """ Paint the text area then the prompt. """
        self.text_area.paint(parent_console=self.console)
        self._print(self.height - 3, self.prompt, color=tcod.cyan, 
                    align='center')
