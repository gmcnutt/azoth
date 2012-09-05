import pygame


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

    def run(self):
        """ Loop until the event handler returns True. """
        self.on_loop_entry()
        while True:
            self.on_loop_start()
            for event in pygame.event.get():
                if self.on_event(event):
                    return self.on_loop_exit()
            self.on_loop_finish()
