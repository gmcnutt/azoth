import colors
import os
import pygame
import settings

class SplashScreen(object):

    def __init__(self, image_fname):
        splash = pygame.image.load('resources/splash.png')
        main_surface = pygame.display.get_surface()
        main_surface.blit(splash, (0, 0))

        # Show [Press any key to continue] over the splash
        font_size = 16
        font = pygame.font.Font(pygame.font.get_default_font(), font_size)
        color = colors.light_grey
        prompt = font.render("[Press any key to continue]", True, color)
        rect = prompt.get_rect()
        main_rect = main_surface.get_rect()
        rect.centerx = main_rect.centerx
        rect.bottom = main_rect.bottom
        main_surface.blit(prompt, rect)

    def run(self):
        # Wait for quit
        pygame.display.flip()
        doquit = False
        while not doquit:
            for event in pygame.event.get():
                if event.type in (pygame.QUIT, pygame.KEYDOWN,
                                  pygame.MOUSEBUTTONDOWN):
                    doquit = True


class Window(object):
    """ Base class for windows. """

    background_color = colors.black

    def __init__(self):
        size = pygame.display.get_surface().get_size()
        self.surface = pygame.Surface(size).convert_alpha()
        self.rect = self.surface.get_rect()

    def on_paint(self):
        """ Hook for subclasses."""
        pass

    def paint(self, to_surface=None):
        """ Paint the window to the destination surface or the currently set
        display surface if none is given. Subclasses should implement
        on_paint()."""
        self.surface.fill(self.background_color)
        self.on_paint()
        if to_surface is None:
            to_surface = pygame.display.get_surface()
        to_surface.blit(self.surface, self.rect.topleft)


class Menu(Window):
    """ Simple menu. """

    def __init__(self, options=None, **kwargs):
        super(Menu, self).__init__(**kwargs)
        self.options = options or ()
        self.current_option = 0
        self.top_visible_option = 0
        self.num_visible_rows = min(self.rect.height - 2, len(options))
        self.last_option = len(options) - 1
        self.current_option = 0
        self.top_trigger = self.num_visible_rows / 2
        self.bottom_trigger = self.last_option - self.top_trigger
        self.font = pygame.font.Font(pygame.font.get_default_font(), 16)

    def _print(self, row, fmt, color=colors.white, align='left'):
        """ Convenience wrapper for most common print call. """
        # NOTE: if I need performance check out the docs on Font.render
        rendered_text = self.font.render(fmt, True, color)
        if align == 'left':
            x = 0
        elif align == 'center':
            x = (self.rect.width - rendered_text.get_width()) / 2
        y = row * self.font.get_linesize()
        self.surface.blit(rendered_text, (x, y))

    def get_selection(self):
        return self.options[self.current_option]

    def scroll_up(self):
        """ Scroll selector up. """
        if self.current_option == 0:
            return
        self.current_option -= 1
        if self.current_option < self.bottom_trigger:
            if self.top_visible_option > 0:
                self.top_visible_option -= 1

    def scroll_down(self):
        """ Scroll selector down. """
        if self.current_option == self.last_option:
            return
        self.current_option += 1
        if self.current_option <= self.bottom_trigger and \
                self.current_option > self.top_trigger:
            self.top_visible_option += 1

    def on_paint(self):
        for row, option in enumerate(range(self.top_visible_option,
                                           self.top_visible_option + \
                                               self.num_visible_rows)):
            if option == self.current_option:
                color = colors.yellow
            else:
                color = colors.grey
            self._print(row, self.options[option], color=color, align='center')

    def on_mouse_event(self, event):
        row = event.pos[1] // self.font.get_linesize()
        self.current_option = min(row, len(self.options) - 1)


class Viewer(object):
    """ A stand-alone UI and keyhandler.  """

    fps = settings.FRAMES_PER_SECOND

    def __init__(self):
        self.done = False
        self.windows = []
        self.clock = pygame.time.Clock()

    def quit(self):
        self.done = True

    def render(self):
        #pygame.display.get_surface().fill(self.background_color)
        self.on_render()
        pygame.display.flip()

    def on_render(self):
        for window in self.windows:
            window.paint()

    def on_mouse_event(self, event):
        for window in self.windows:
            if window.rect.collidepoint(event.pos):
                window.on_mouse_event(event)

    def run(self):
        self.render()
        while not self.done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        return
                    else:
                        self.on_keypress(event)
                elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION,
                                    pygame.MOUSEBUTTONUP):
                    self.on_mouse_event(event)

            self.render()
            self.clock.tick(self.fps)


class FileSelector(Viewer):

    def __init__(self, path=None, re_filter=None):
        super(FileSelector, self).__init__()
        self.selection = None
        files = ['.'] + sorted(os.listdir(path))
        self.menu = Menu(options=files)

    def handle_enter(self):
        self.selection = self.menu.options[self.menu.current_option]
        self.done = True

    def on_render(self):
        self.menu.paint()

    def on_keypress(self, event):
        handler = {
            pygame.K_DOWN: self.menu.scroll_down,
            pygame.K_UP: self.menu.scroll_up,
            pygame.K_q: self.quit,
            pygame.K_RETURN: self.handle_enter
            }.get(event.key)
        if handler:
            handler()

    def run(self):
        super(FileSelector, self).run()
        return self.selection


class MainMenu(Viewer):

    def __init__(self):
        super(MainMenu, self).__init__()
        self.menu = Menu(options=('Start New Game', 'Load Saved Game', 'Quit'))
        self.windows.append(self.menu)

    def select(self):
        selection = self.menu.get_selection()
        print('Selected {}'.format(selection))
        if selection == 'Quit':
            self.done = True

    def on_keypress(self, event):
        handler = {
            pygame.K_DOWN: self.menu.scroll_down,
            pygame.K_UP: self.menu.scroll_up,
            pygame.K_q: self.quit,
            pygame.K_RETURN: self.select
            }.get(event.key)
        if handler:
            handler()

    def on_mouse_event(self, event):
        super(MainMenu, self).on_mouse_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.select()
