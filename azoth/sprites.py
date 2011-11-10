import pygame

class Sheet(object):
    
    def __init__(self, width, height, rows, columns, filename):
        self.rows = rows
        self.columns = columns
        self.width = width
        self.height = height
        # XXX: put directory in config.py
        self.surface = pygame.image.load('../data/sprites/'+ filename)
        self.surface.convert_alpha()


class Sprite(object):
    
    def __init__(self, sheet, num_frames, start_frame, wave, facings):
        self.sheet = sheet
        self.wave = wave
        self.facings = facings
        rect = pygame.Rect(0, 0, sheet.width, sheet.height)
        self.frames = []
        for frame in range(num_frames):
            frame_index = start_frame + frame
            rect.x = (frame_index % sheet.columns) * sheet.width
            rect.y = (frame_index / sheet.columns) * sheet.height
            self.frames.append(sheet.surface.subsurface(rect))
            
    @property
    def height(self):
        return self.sheet.height

    @property
    def width(self):
        return self.sheet.width

