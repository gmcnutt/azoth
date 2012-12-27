"""
Azoth configuration.
"""

# The base directory for sprite-related data and images
SPRITE_DIRECTORY = '../data/sprites/'

# The base directory for object-related data
OBJECT_DIRECTORY = '../data/objects/'

# The base directory for terrain-related data
TERRAIN_DIRECTORY = '../data/terrain/'

# The file containing all the sprite sheet descriptors
SHEET_DATA_FILE = SPRITE_DIRECTORY + 'sheets.json'

# The file containing all the sprite descriptors
SPRITE_DATA_FILE = SPRITE_DIRECTORY + 'sprites.json'

# The file containing all the terrain descriptors
TERRAIN_DATA_FILE = TERRAIN_DIRECTORY + 'terrain.json'

# The file containing all the reagent descriptors
REAGENT_DATA_FILE = OBJECT_DIRECTORY + 'reagents.json'

# The max frames per second
FRAMES_PER_SECOND = 40

# The seconds to delay between scripted animation frames
ANIMATION_SECONDS_PER_FRAME = 0.1

# The base directory for DLL's, should I actually need to distribute them
DLL_DIRECTORY = '../dll/'
