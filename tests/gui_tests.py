import unittest
from tools import eq_, raises
from azoth import event, gui
import pygame

SCREEN_COLUMNS = 80
SCREEN_ROWS = 40

class GuiTest(unittest.TestCase):

    def setUp(self):
        pygame.init()
        pygame.display.set_mode((320, 240), 0)
        self.message = 'In spring of youth it was my lot to haunt of '\
            'the wide world a spot the which I could not love the less '\
            'so lovely was its loneliness'
        self.prompt_all=False

    def show(self, prompt=False):
        self.target.paint()
        pygame.display.flip()
        if prompt or self.prompt_all:
            self.prompt()

    def prompt(self):
        event = pygame.event.wait()
        while event.type != pygame.KEYDOWN:
            event = pygame.event.wait()

class FpsViewerTest(GuiTest):
    
    def test_default(self):
        self.target = gui.FpsViewer()
        self.target.fps = 632
        self.show()


class TableViewerTest(GuiTest):

    def test_default(self):
        columns = ('First Name', 'Last Name')
        rows = (('Bilbo', 'Baggins'),
                ('Samwise', 'Gamgee'))
        self.target = gui.TableWindow(title='Test', columns=columns, rows=rows)
        self.show()


class MenuTest(GuiTest):

    def test_default(self):
        self.target = gui.Menu(options=('Create Game', 'Quit'))
        self.show()

    def test_scroll(self):
        self.target = gui.Menu(options=('Create Game', 'Quit'))
        self.show()
        self.target.scroll_down()
        self.show()
        self.target.scroll_up()
        self.show()

    @raises(event.Handled)
    def test_viewer(self):
        options = ('Create Game', 'Quit')
        menu = gui.Menu(options=options)
        self.viewer = gui.MenuViewer(menu)
        self.viewer.on_keypress(pygame.K_DOWN)
        eq_(menu.get_selection(), 'Quit')
        self.viewer.on_keypress(pygame.K_UP)
        eq_(menu.get_selection(), 'Create Game')
        self.viewer.on_keypress(pygame.K_RETURN)
