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
    
    # Show [Press any key to continue] over the splash
    font_size = 16
    font = pygame.font.Font(pygame.font.get_default_font(), font_size)
    color = (191, 191, 191)
    prompt = font.render("[Press any key to continue]", True, color)
    rect = prompt.get_rect()
    main_rect = main_surface.get_rect()
    rect.centerx = main_rect.centerx
    rect.bottom = main_rect.bottom
    main_surface.blit(prompt, rect)

    # Wait for quit
    pygame.display.flip()
    doquit = False
    while not doquit:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                doquit = True
            elif event.type == pygame.KEYDOWN:
                doquit = True
