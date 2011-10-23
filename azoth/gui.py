import libtcodpy as tcod
import logging

class Window(object):
    """ Base class for terminal windows. """

    def __init__(self, x=0, y=0, width=0, height=0, 
                 boxed=False, title=None,
                 style=None, hide=False):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.log = logging.getLogger(self.__class__.__name__)
        self.boxed = boxed
        self.title = title
        self.top_margin = 0 if not boxed else 1
        self.left_margin = 0 if not boxed else 1
        self.style = style or {}
        self.hide = hide

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

    def addglyph(self, col, row, glyph):
        """ Like addch() but uses a tuple for (character, foreground color,
        background color). """
        tcod.console_put_char_ex(None, self.x + col, self.y + row, 
                                 glyph[0], glyph[1], glyph[2])

    def addstr(self, col, row, string):
        """ Safe version of curses.addstr that will catch the exception if row
        is not in the window.  """
        tcod.console_print_left(None, self.x + col, self.y + row, 
                                tcod.BKGND_NONE, string)

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

    def move(self, dx=0, dy=0):
        """ Move the window around within the screen. """
        self.x += dx
        self.y += dy

    def on_paint(self):
        """ Hook for subclasses."""
        pass

    def paint(self):
        """ Paint the window. Subclasses should implement on_paint(). """
        if self.hide:
            return
        self.on_paint()
        if self.boxed:
            attr = 0
            color = self.style.get('border-color')
            if color == 'blue':
                attr = tcod.blue
            old_fgcolor = tcod.console_get_foreground_color(None)
            tcod.console_set_foreground_color(None, attr)
            self.box()
            tcod.console_set_foreground_color(None, old_fgcolor)            
        if self.title:
            attr = 0
            color = self.style.get('title-color')
            if color == 'yellow':
                attr = tcod.yellow
            old_fgcolor = tcod.console_get_foreground_color(None)
            tcod.console_set_foreground_color(None, attr)
            self.addstr(1, 0, self.title)
            tcod.console_set_foreground_color(None, old_fgcolor)            
