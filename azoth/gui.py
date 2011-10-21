import colors
import _curses # for exceptions
import curses
import logging

class Window(object):
    """ Base class for terminal windows. """

    def __init__(self, x=0, y=0, width=0, height=0, 
                 boxed=False, title=None,
                 win=None, style=None, hide=False):
        self.log = logging.getLogger(self.__class__.__name__)
        self.win = win or curses.newwin(height, width, y, x)
        self.boxed = boxed
        self.title = title
        self.top_margin = 0 if not boxed else 1
        self.left_margin = 0 if not boxed else 1
        self.style = style or {}
        self.hide = hide

    @property
    def x(self):
        """ Screen x-coordinate of upper left corner. """
        return self.win.getbegyx()[1]

    @property
    def y(self):
        """ Screen y-coordinate of upper left corner. """
        return self.win.getbegyx()[0]

    @property
    def left(self):
        """ Screen x-coordinate of left edge. """
        return self.win.getbegyx()[1]

    @property
    def top(self):
        """ Screen y-coordinate of top edge. """
        return self.win.getbegyx()[0]

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
    def width(self):
        """ Number of columns. """
        return self.win.getmaxyx()[1]

    @property
    def height(self):
        """ Number of rows. """
        return self.win.getmaxyx()[0]

    @property
    def rows(self):
        """ Return iterator over rows. """
        return range(self.height)

    @property
    def cols(self):
        """ Return iterator over columns. """
        # XXX: curses raises an error if I addch to the last column; don't know
        # why
        return range(self.width - 1)

    def addglyph(self, row, col, glyph):
        """ Like addch() but uses a tuple for (char, attr). """
        self.win.addch(row, col, glyph[0], glyph[1])

    def addstr(self, row, col, string):
        """ Safe version of curses.addstr that will catch the exception if row
        is not in the window.  """
        if row < self.height:
            self.win.addstr(row, col, string)

    def resize(self, dw=0, dh=0):
        """ Expand (or shrink) the window. """
        nw = self.width + dw
        nh = self.height + dh
        if nw < 2 or nh < 2:
            # XXX: else resize will raise an error
            return
        self.win.erase()
        self.win.refresh()
        self.win.resize(nh, nw)

    def move(self, dx=0, dy=0):
        """ Move the window around within the screen. """
        # XXX: is there a better way to do bounds checking on the right and
        # left other than catch the (privately named _curses) exception?
        self.win.erase()
        self.win.refresh()
        try:
            self.win.mvwin(self.y + dy, self.x + dx)
        except _curses.error:
            pass

    def on_paint(self):
        """ Hook for subclasses."""
        pass

    def paint(self):
        """ Paint the window. Subclasses should implement on_paint(). """
        if self.hide:
            return
        self.win.erase()
        self.on_paint()
        if self.boxed:
            attr = 0
            color = self.style.get('border-color')
            if color == 'blue':
                attr = curses.color_pair(colors.BLUE)
            self.win.attron(attr)
            self.win.box()
            self.win.attroff(attr)
        if self.title:
            attr = 0
            color = self.style.get('title-color')
            if color == 'yellow':
                attr = curses.color_pair(colors.YELLOW)
            self.win.attron(attr)
            n = self.width - 2
            self.win.addnstr(0, 1, '%s' % self.title, n)
            self.win.attroff(attr)
        self.win.refresh()
        self.log.debug('after paint:getbegyx={}'.format(self.win.getbegyx()))
