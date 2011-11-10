#!/usr/bin/python

import argparse
import cPickle
import colors
import gui
from hax2 import being, place, rules, session, terrain, weapon
import hax2.plane
import logging
import pygame
import os
import sys
from pgu import html

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Play or edit hax2 games')
    parser.add_argument('--start', dest='start', metavar='s', 
                        help='Saved game to start')
    args = parser.parse_args()

    os.unlink('azoth.log')
    logging.basicConfig(filename='azoth.log',level=logging.DEBUG)

    pygame.init()
    pygame.display.set_caption('Azoth')
    screen = pygame.display.set_mode((320, 240), 0)

    # image = pygame.image.load('data/images/u4/shapes.png').convert_alpha()
    # screen.blit(image, (0, 0))
    # pygame.display.flip()

    # font = pygame.font.Font(pygame.font.get_default_font(), 16)

    # rect = pygame.Rect(0, 0, 320, 240)
    # #html.write(screen, font, rect, 'hi', color=colors.white)
    # textsurf = html.rendertrim(font, rect, 'hi', 0, color=colors.white)
    # screen.blit(textsurf, (0, 0))
    # pygame.display.flip()

    # event = pygame.event.wait()
    # while event.type != pygame.QUIT:
    #     event = pygame.event.wait()

    gui.Alert('Hi!').run()
