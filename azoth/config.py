"""
Azoth configuration.
"""

import logging
import os

BASE_DIRECTORY = os.path.join(os.path.dirname(__file__), '..')

# The directory to hold saved games
SAVE_DIRECTORY = os.path.join(BASE_DIRECTORY, 'save')

# The base directory for non-sprite images
IMAGE_DIRECTORY = os.path.join(BASE_DIRECTORY, 'data', 'images')

# The base directory for sprite-related data and images
SPRITE_DIRECTORY = os.path.join(BASE_DIRECTORY, 'data', 'sprites')

# The base directory for object-related data
OBJECT_DIRECTORY = os.path.join(BASE_DIRECTORY, 'data', 'objects')

# The base directory for terrain-related data
TERRAIN_DIRECTORY = os.path.join(BASE_DIRECTORY, 'data', 'terrain')

# The file containing all the sprite sheet descriptors
SHEET_DATA_FILE = os.path.join(SPRITE_DIRECTORY, 'sheets.json')

# The file containing all the sprite descriptors
SPRITE_DATA_FILE = os.path.join(SPRITE_DIRECTORY, 'sprites.json')

# The file containing all the terrain descriptors
TERRAIN_DATA_FILE = os.path.join(TERRAIN_DIRECTORY, 'terrain.json')

# The file containing all the reagent descriptors
REAGENT_DATA_FILE = os.path.join(OBJECT_DIRECTORY, 'reagents.json')

# The file for libtcod dll's
DLL_DIRECTORY = os.path.join(BASE_DIRECTORY, 'dll')

# The max frames per second
FRAMES_PER_SECOND = 40

# The seconds to delay between scripted animation frames
PATHFIND_SECONDS_PER_FRAME = 0.01

# The log file
LOG_FILE = os.path.join(BASE_DIRECTORY, 'azoth.log')

# Log verbosity
LOG_LEVEL = logging.DEBUG
