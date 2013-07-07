#!/usr/bin/python

import argparse
from azoth import baseobject, being, config, gui, session, sprite, \
    terrain, weapon
import build
import inspect
import json
import logging
import pygame
import os


class AzothObject(object):
    name = "azoth object"  # placeholder

    
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Play Azoth')
    parser.add_argument('--start', metavar='file', help='Saved game')
    cmdargs = parser.parse_args()

    # Initialize the log file.
    try:
        os.unlink('azoth.log')
    except OSError:
        pass
    logging.basicConfig(
        level=config.LOG_LEVEL,
        filename=config.LOG_FILE,
        format='%(asctime)s|%(threadName)s|%(levelname)s|%(filename)s:'\
            '%(funcName)s:%(lineno)d|%(message)s')

    # Initialize pygame.
    pygame.init()
    pygame.display.set_caption('Azoth')
    screen = pygame.display.set_mode((640, 480), 0)
    pygame.key.set_repeat(500, 10) # XXX: put in config.py

    # Show the splash screen.
    path = os.path.join(config.IMAGE_DIRECTORY, 'engine', 'splash.png')
    splash = gui.SplashScreen(path)
    splash.run()

    # Load the sprites.
    sheets = {}
    sheet_table = json.loads(open(config.SHEET_DATA_FILE).read())
    for k, v in sheet_table.items():
        sheets[k] = sprite.Sheet(*v)

    all_sprites = {}
    sprite_table = json.loads(open(config.SPRITE_DATA_FILE).read())
    for k, v in sprite_table.items():
        sheet = sheets[v[0]]
        frames = v[1]
        start = v[2]
        wave = v[3]
        facings = v[4]
        if not wave:
            spr = sprite.AnimatedSprite(sheet, frames, start, facings=facings)
        else:
            spr = sprite.WaveSprite(sheet, start)
        all_sprites[k] = spr

    # viewer = gui.TableViewer(title='Sprites', columns=('Name', 'Sprite'),
    #                          rows=all_sprites.items())
    # viewer.run()

    # Assign terrain sprites
    for name, o in inspect.getmembers(terrain):
        if inspect.isclass(o) and issubclass(o, terrain.Terrain):
            try:
                o.sprite = all_sprites[o.__name__]
            except KeyError:
                logging.warn('{} has no sprite'.format(o.__name__))

    # Assign sprites based on class name
    for module in (weapon, being):
        for name, o in inspect.getmembers(module):	  	
            if inspect.isclass(o) and issubclass(o, baseobject.BaseObject):
                try:
                    o.sprite = all_sprites[o.__name__]
                except KeyError:
                    logging.warn('{} has no sprite'.format(o.__name__))

    # Load the session.
    if cmdargs.start is not None:
        session = session.load(cmdargs.start)
        session_viewer = gui.SessionViewer(session)
        session_viewer.run()
    else:
        # Show main menu
        menu = gui.MainMenu(generator=build.generate)
        menu.run()
    

