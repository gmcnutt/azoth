#!/usr/bin/python

import argparse
import executor
import classes
import cPickle
import colors
import config
import gui
import obj
import inspect
import json
import logging
from obj import Obj, being, weapon
import pygame
import os
import session
import sprite
import sys
import terrain


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Play Azoth')
    parser.add_argument('start', metavar='file', help='Saved game')
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

    # Load the sprite.
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

    # Assign sprites
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

    being.Human.sprite = all_sprites['townsman']

    # Assign sprites based on class name
    for module in (weapon,):
        for name, o in inspect.getmembers(module):	  	
            if inspect.isclass(o) and issubclass(o, Obj):
                o.sprite = all_sprites[o.__name__]

    # Load the session.
    session = session.load(cmdargs.start)

    # Update the session passability rules
    session.rules.set_passability('walk', 'wall', executor.PASS_NONE)
    session.rules.set_passability('walk', 'boulder', executor.PASS_NONE)
    session.rules.set_passability('walk', 'water', executor.PASS_NONE)

    session_viewer = gui.SessionViewer(session)
    session_viewer.run()

