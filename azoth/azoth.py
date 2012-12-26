#!/usr/bin/python

import argparse
import config
import gui
import inspect
import json
import logging
import pygame
import reagents
import os
import session
import sprites
import terrain


class AzothObject(object):
    name = "azoth object"  # placeholder

    
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Play Azoth')
    parser.add_argument('--start', dest='start', metavar='s', help='Saved game')
    cmdargs = parser.parse_args()

    # Initialize the log file.
    try:
        os.unlink('azoth.log')
    except OSError:
        pass
    logging.basicConfig(filename='azoth.log',level=logging.DEBUG)

    # Initialize pygame.
    pygame.init()
    pygame.display.set_caption('Azoth')
    screen = pygame.display.set_mode((640, 480), 0)
    pygame.key.set_repeat(500, 10) # XXX: put in config.py

    # Run the main menu.
    

    # Load the sprites.
    sheets = {}
    sheet_table = json.loads(open(config.SHEET_DATA_FILE).read())
    for k, v in sheet_table.items():
        sheets[k] = sprites.Sheet(*v)

    all_sprites = {}
    sprite_table = json.loads(open(config.SPRITE_DATA_FILE).read())
    for k, v in sprite_table.items():
        sheet = sheets[v[0]]
        frames = v[1]
        start = v[2]
        wave = v[3]
        facings = v[4]
        if not wave:
            sprite = sprites.AnimatedSprite(sheet, frames, start, facings=facings)
        else:
            sprite = sprites.WaveSprite(sheet, start)
        all_sprites[k] = sprite

    # Initialize terrains
    all_terrains = {}
    terrain.HeavyForest.sprite = all_sprites['forest']
    terrain.Forest.sprite = all_sprites['trees']
    terrain.Grass.sprite = all_sprites['grass']
    terrain.Trail.sprite = all_sprites['trail_f']
    terrain.RockWall.sprite = all_sprites['wall_stone']
    terrain.CobbleStone.sprite = all_sprites['cobblestone']
    terrain.Window.sprite = all_sprites['window_in_stone']
    terrain.CounterTop.sprite = all_sprites['counter_1x1']
    terrain.FirePlace.sprite = all_sprites['fireplace']
    terrain.Boulder.sprite = all_sprites['boulder']
    terrain.Bog.sprite = all_sprites['bog']
    terrain.Water.sprite = all_sprites['shoals']

    # Show them in a window for dev.
    for name, obj in inspect.getmembers(terrain):
        if inspect.isclass(obj):
            if hasattr(obj, 'sprite'):
                all_terrains[obj.name] = obj
    #gui.TerrainGridViewer(sorted(all_terrains.items())).run()

    # Initialize reagents.
    all_reagents = {}
    for name, obj in inspect.getmembers(reagents):
        if (inspect.isclass(obj) and issubclass(obj, reagents.AzothObject) 
            and (obj != reagents.AzothObject)):
            obj.sprite = all_sprites[obj.__name__]
            all_reagents[obj.name] = obj
    gui.ObjectListViewer(sorted(all_reagents.items())).run()

    # Load the session.
    session = session.load(open(cmdargs.start))
    sector = session.world
    place_view = gui.PlaceViewer(sector)
    place_view.run()


