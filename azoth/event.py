import pygame


class Quit(Exception):
    """ Raised by the event handler when it wants to indicate that the player
    is quitting. """
    pass


class Handled(Exception):
    """ Raised by the event handler when it has handled the event and wants to
    break out of the loop."""
    pass


class EventLoop(object):
    """ Provide a common framework to drive the event loop. """

    def on_loop_entry(self):
        """ Hook for subclasses to override. """
        pass

    def on_loop_exit(self):
        """ Hook for subclasses to override. """
        pass

    def on_loop_start(self):
        """ Hook for subclasses to override. """
        pass

    def on_loop_finish(self):
        """ Hook for subclasses to override. """
        pass
    
    def on_event(self, event):
        """ Hook for subclasses to override. """
        pass

    def run_one_iteration(self):
        """ Run one iteration. Return True to break out of the main loop. """
        self.on_loop_start()
        for event in pygame.event.get():
            self.on_event(event)
        self.on_loop_finish()

    def handle_events(self):
        """ Loop until the event handler raises an exception. """
        self.on_loop_entry()
        try:
            while True:
                self.run_one_iteration()
        except Handled:
            pass
        finally:
            self.on_loop_exit()
