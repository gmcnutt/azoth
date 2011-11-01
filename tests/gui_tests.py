import libtcodpy as tcod
import unittest
from tools import *
from azoth import gui

SCREEN_COLUMNS = 80
SCREEN_ROWS = 40

class GuiTest(unittest.TestCase):

    def setUp(self):
        tcod.console_init_root(SCREEN_COLUMNS, SCREEN_ROWS, "Test", False)
        self.message = 'In spring of youth it was my lot to haunt of '\
            'the wide world a spot the which I could not love the less '\
            'so lovely was its loneliness'

    def show(self, prompt=False):
        self.target.paint()
        tcod.console_flush()
        if prompt:
            self.prompt()

    def prompt(self):
        tcod.console_wait_for_keypress(True)        


class TextAreaTest(GuiTest):

    def test_default_args(self):
        self.target = gui.TextArea()
        self.show()

    def test_one_letter_message(self):
        self.target = gui.TextArea(message=self.message[0])
        self.show()

    def test_two_letter_message(self):
        self.target = gui.TextArea(message=self.message[:2])
        self.show()

    def test_single_line_default(self):
        self.target = gui.TextArea(message=self.message[:20])
        self.show()

    def test_single_line_custom(self):
        self.target = gui.TextArea(message=self.message[:50], max_width=100)
        self.show()

    def test_two_lines_default(self):
        self.target = gui.TextArea(message=self.message[:60], max_width=32)
        self.show()

    def test_two_lines_custom(self):
        self.target = gui.TextArea(message=self.message[:60], max_width=32,
                                   max_height=4)
        self.show()

    def test_one_line_overflow(self):
        self.target = gui.TextArea(message=self.message[:60], max_width=32,
                                   max_height=3)
        self.show()

    def test_two_line_overflow(self):
        self.target = gui.TextArea(message=self.message[:60], max_width=12,
                                   max_height=4)
        self.show()

    def test_max_width_too_small(self):
        raises_(ValueError, gui.TextArea, message=self.message, max_width=2)

    def test_max_height_too_small(self):
        raises_(ValueError, gui.TextArea, message=self.message, max_height=1)


class PromptDialogTest(GuiTest):

    def test_default_args(self):
        self.target = gui.PromptDialog()
        self.show()

    def test_empty_message(self):
        self.target = gui.PromptDialog(message='')
        self.show()

    def test_one_letter_message(self):
        self.target = gui.PromptDialog(message='x')
        self.show()

    def test_two_letter_message(self):
        self.target = gui.PromptDialog(message='xy')
        self.show()

    def test_overflow_default_width(self):
        self.target = gui.PromptDialog(message=self.message)
        self.show()

    def test_underflow_custom_width(self):
        self.target = gui.PromptDialog(message=self.message[0:5], max_width=20)
        self.show()

    def test_overflow_default_height(self):
        self.target = gui.PromptDialog(message=self.message, max_width=5)
        self.show()
        
    def test_overflow_custom_height(self):
        self.target = gui.PromptDialog(message=self.message, max_width=20, 
                                       max_height=10)
        self.show()
