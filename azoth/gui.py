import libtcodpy as tcod
import logging

class Window(object):
    """ Base class for terminal windows. """

    def __init__(self, x=0, y=0, width=0, height=0, title=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.log = logging.getLogger(self.__class__.__name__)
        self.title = title
        self.top_margin = 1
        self.left_margin = 1
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
        # XXX: need the -1?
        return self.left + self.width

    @property
    def bottom(self):
        """ Screen y-coordinate of bottom edge. """
        return self.top + self.height

    @property
    def rows(self):
        """ Return iterator over rows. """
        return range(self.height)

    @property
    def cols(self):
        """ Return iterator over columns. """
        return range(self.width)

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

    def box(self):
        pass

    def resize(self, dw=0, dh=0):
        """ Expand (or shrink) the window. """
        nw = self.width + dw
        nh = self.height + dh
        if nw < 2 or nh < 2:
            return
        self.width = nw
        self.height = nh

    def set_background_color(self, x, y, color):
        tcod.console_set_back(self.console, x, y, color, tcod.BKGND_SET)

    def move(self, dx=0, dy=0):
        """ Move the window around within the screen. """
        self.x += dx
        self.y += dy

    def on_paint(self):
        """ Hook for subclasses."""
        pass

    def paint(self):
        """ Paint the window. Subclasses should implement on_paint(). """
        tcod.console_set_foreground_color(self.console, tcod.white)
        tcod.console_clear(self.console)
        self.on_paint()
        tcod.console_set_foreground_color(self.console, tcod.light_blue)
        tcod.console_print_frame(self.console, 0, 0, self.width, self.height,
                                 False, 0, self.title)
        tcod.console_blit(self.console, 0, 0, self.width, self.height,
                          None, self.x, self.y)

    def invert_colors(self):
        fg = tcod.console_get_foreground_color(self.console)
        bg = tcod.console_get_background_color(self.console)
        tcod.console_set_foreground_color(self.console, bg)
        tcod.console_set_background_color(self.console, fg)

    def _print(self, row, fmt):
        """ Convenience wrapper for most common print call. """
        tcod.console_print_left(self.console, self.left_margin, 
                                self.top_margin + row, tcod.BKGND_NONE, fmt)

class Menu(Window):

    def __init__(self, options=None, **kwargs):
        super(Menu, self).__init__(**kwargs)
        self.options = options
        self.current_option = 0
        self.top_visible_option = 0
        self.num_visible_rows = min(self.height - 2, len(options))
        self.last_option = len(options) - 1
        self.current_option = 0
        self.top_trigger = self.num_visible_rows / 2
        self.bottom_trigger = self.last_option - self.top_trigger

    def scroll_up(self):
        if self.current_option == 0:
            return
        self.current_option -= 1
        if self.current_option < self.bottom_trigger:
            if self.top_visible_option > 0:
                self.top_visible_option -= 1

    def scroll_down(self):
        if self.current_option == self.last_option:
            return
        self.current_option += 1
        if self.current_option <= self.bottom_trigger and \
                self.current_option > self.top_trigger:
            self.top_visible_option += 1

    def on_paint(self):
        for row, option in enumerate(range(self.top_visible_option, 
                                           self.top_visible_option + self.num_visible_rows)):
            if option == self.current_option:
                tcod.console_set_foreground_color(self.console, tcod.yellow)
            else:
                tcod.console_set_foreground_color(self.console, tcod.gray)
            self._print(row, self.options[option])
