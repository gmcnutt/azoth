import libtcodpy as tcod
import unittest
from tools import *
from azoth import gui

SCREEN_COLUMNS = 80
SCREEN_ROWS = 40

class PromptDialogTest(unittest.TestCase):

    def setUp(self):
        tcod.console_init_root(SCREEN_COLUMNS, SCREEN_ROWS, "Test", False)

    def test_default_args(self):
        self.prompt = gui.PromptDialog()
        self.prompt.paint()
        tcod.console_flush()

    def test_empty_message(self):
        self.prompt = gui.PromptDialog(message='')
        self.prompt.paint()
        tcod.console_flush()

    def test_one_letter_message(self):
        self.prompt = gui.PromptDialog(message='x')
        self.prompt.paint()
        tcod.console_flush()

    def test_two_letter_message(self):
        self.prompt = gui.PromptDialog(message='xy')
        self.prompt.paint()
        tcod.console_flush()

    def test_overflow_default_width(self):
        self.prompt = gui.PromptDialog(message='12345')
        self.prompt.paint()
        tcod.console_flush()

    def test_underflow_width(self):
        self.prompt = gui.PromptDialog(message='12345', max_width=20)
        self.prompt.paint()
        tcod.console_flush()

    def test_overflow_default_height(self):
        self.prompt = gui.PromptDialog(message='123456789012', max_width=8)
        self.prompt.paint()
        tcod.console_flush()
        tcod.console_wait_for_keypress(True)
        
