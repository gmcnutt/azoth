#!/usr/bin/python

import argparse
import classes
import cPickle
import colors
import config
import gui
import hax2.terrain
import json
import logging
import pygame
import os
import session
import sprites
import sys
import terrain


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Play Azoth')
    parser.add_argument('--start', dest='start', metavar='s', help='Saved game')
    cmdargs = parser.parse_args()

    try:
        os.unlink('azoth.log')
    except OSError:
        pass
    logging.basicConfig(filename='azoth.log',level=logging.DEBUG)

    pygame.init()
    pygame.display.set_caption('Azoth')
    screen = pygame.display.set_mode((640, 480), 0)
    pygame.key.set_repeat(500, 10) # XXX: put in config.py

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

    #gui.SpriteListViewer(sorted(all_sprites.items())).run()

    all_terrains = {}
    terrain_table = json.loads(open(config.TERRAIN_DATA_FILE).read())
    for k, v in terrain_table.items():
        args = v[0:4]
        if type(args[2]) == list:
            args[2] = sprites.CompositeSprite([all_sprites[x] for x in args[2]])
        else:
            args[2] = all_sprites[args[2]] # lookup sprite
        kwargs = v[4] if len(v) > 4 else {}
        all_terrains[k] = terrain.Terrain(*args, **kwargs)

    print('{} terrains loaded'.format(len(all_terrains.keys())))
    #gui.TerrainGridViewer(sorted(all_terrains.items())).run()

    all_reagents = {}
    reagent_table = json.loads(open(config.REAGENT_DATA_FILE).read())
    for k, v in reagent_table.items():
        all_reagents[k] = classes.Reagent(v[0], all_sprites[v[1]])

    #gui.ObjectListViewer(sorted(all_reagents.items())).run()

    hax2.terrain.HeavyForest.sprite = all_sprites['forest']
    hax2.terrain.Forest.sprite = all_sprites['trees']
    hax2.terrain.Grass.sprite = all_sprites['grass']
    hax2.terrain.Trail.sprite = all_sprites['trail_0']
    hax2.terrain.RockWall.sprite = all_sprites['wall_stone']
    hax2.terrain.CobbleStone.sprite = all_sprites['cobblestone']
    hax2.terrain.Window.sprite = all_sprites['window_in_stone']
    hax2.terrain.CounterTop.sprite = all_sprites['counter_1x1']

    session = session.load(open(cmdargs.start))
    sector = session.world
    place_view = gui.PlaceViewer(sector)
    place_view.run()

