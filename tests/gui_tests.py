import unittest
from tools import *
from azoth import gui
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

class TextLabelTest(GuiTest):

    def test_default_args(self):
        self.target = gui.TextLabel()
        self.show()

    def test_one_letter_message(self):
        self.target = gui.TextLabel(message=self.message[0])
        self.show()

    def test_two_letter_message(self):
        self.target = gui.TextLabel(message=self.message[:2])
        self.show()

    def test_single_line_default(self):
        self.target = gui.TextLabel(message=self.message[:20])
        self.show()

    def test_single_line_custom(self):
        self.target = gui.TextLabel(message=self.message[:50], max_width=100)
        self.show()

    def test_two_lines_default(self):
        self.target = gui.TextLabel(message=self.message[:60], max_width=32)
        self.show()

    def test_two_lines_custom(self):
        self.target = gui.TextLabel(message=self.message[:60], max_width=32,
                                   max_height=4)
        self.show()

    def test_one_line_overflow(self):
        self.target = gui.TextLabel(message=self.message[:60], max_width=32,
                                   max_height=3)
        self.show()

    def test_two_line_overflow(self):
        self.target = gui.TextLabel(message=self.message[:60], max_width=12,
                                   max_height=4)
        self.show()

    def test_max_width_too_small(self):
        self.target = gui.TextLabel(message=self.message, max_width=2)
        self.show()

    def test_max_height_too_small(self):
        self.target = gui.TextLabel(message=self.message, max_height=1)
        self.show()


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

class FpsViewerTest(GuiTest):
    
    def test_default(self):
        self.target = gui.FpsViewer()
        self.target.fps = 632
        self.show()
