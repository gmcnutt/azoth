import curses
import logging
import os
import sys
sys.path.append('../azoth')
import azoth
from azoth import gui

os.unlink('demo.log')
logging.basicConfig(filename='demo.log', level=logging.DEBUG)

class TransferWindow(gui.Window):
    
    def __init__(self, list1=None, list2=None, **kwargs):
        super(TransferWindow, self).__init__(title='Transfer', boxed=True, 
                                             **kwargs)
        self.list1 = list1
        self.list2 = list2

    def on_paint(self):
        pass

class WindowDemo(object):

    def __init__(self, scr):
        self.scr = scr
        height, width = self.scr.getmaxyx()
        self.window = TransferWindow(x=0, y=0, width=width, height=height,
                                     style={'border-color':'blue',
                                            'title-color':'yellow'})
    def run(self):
        self.window.paint()
        ch = self.scr.getch()
        while ch != ord('q'):
            logging.debug('ch={}'.format(ch))
            if ch == curses.KEY_DOWN:
                logging.debug('down')
                self.window.move(dy=1)
            elif ch == curses.KEY_UP:
                logging.debug('up')
                self.window.move(dy=-1)
            elif ch == curses.KEY_RIGHT:
                logging.debug('right')
                self.window.move(dx=1)
            elif ch == curses.KEY_LEFT:
                logging.debug('left')
                self.window.move(dx=-1)
            elif ch == ord('w'):
                logging.debug('wider')
                self.window.resize(dw=1)
            elif ch == ord('n'):
                logging.debug('narrower')
                self.window.resize(dw=-1)
            elif ch == ord('t'):
                logging.debug('taller')
                self.window.resize(dh=1)
            elif ch == ord('s'):
                logging.debug('shorter')
                self.window.resize(dh=-1)
            self.window.paint()
            ch = self.scr.getch()

def main(scr):
    azoth.setup(scr)
    demo = WindowDemo(scr)
    demo.run()

curses.wrapper(main)
