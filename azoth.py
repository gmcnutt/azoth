#!/usr/bin/python

import argparse
import logging
import pygame
import os


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

    # Show the splash screen.
    splash = pygame.image.load('resources/splash.png')
    
    main_surface = pygame.display.get_surface()
    main_surface.blit(splash, (0, 0))
    pygame.display.flip()

    doquit = False
    while not doquit:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                doquit = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    doquit = True
