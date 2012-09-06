import event
import pygame


class Controller(object):

    def __init__(self, subject, session):
        self.subject = subject
        self.session = session


class Player(Controller):

    """ A controller that lets the player control the subject. """

    def move(self, dx, dy):
        """ Move the subject. """
        try:
            self.session.hax2.move_being_on_map(self.subject, dx, dy)
        except place.PlaceError:
            return
        except executor.RuleError:
            return
        return True

    def save(self):
        """ Save the session. """
        self.session.save('save.p')

    def get(self):
        """ Have the subject pick up something on the ground at his feet. """
        items = self.session.world.get_items(self.subject.x,
                                             self.subject.y)
        if items is not None:
            item = items[0]
            being = self.subject
            self.session.hax2.move_item_from_map_to_being(item, being)
            return True

    def drop(self):
        """ Have the subject drop something from inventory to the ground. """
        being = self.subject
        items = being.body.get()
        if items is not None:
            item = items[0]
            self.session.hax2.move_item_from_being_to_map(item, being)
            return True

    def quit(self):
        """ Raise the Quit exception to signal the player is done. """
        raise event.Quit()

    def key_handler(self, key):
        """ Handle a key to control the subject during its turn. Returns True
        when done with turn."""
        handler = {
            pygame.K_DOWN: lambda: self.move(0, 1),
            pygame.K_UP: lambda: self.move(0, -1),
            pygame.K_LEFT: lambda: self.move(-1, 0),
            pygame.K_RIGHT: lambda: self.move(1, 0),
            pygame.K_d: self.drop,
            pygame.K_g: self.get,
            pygame.K_q: self.quit,
            pygame.K_s: self.save,
            }.get(key)
        if handler:
            return handler()
        return False

    def do_turn(self, event_loop):
        """ Let the player control the subject during the turn. """
        event_loop.push_key_handler(self.key_handler)
        event_loop.resume()
        event_loop.pop_key_handler()


class Beeline(Controller):

    def do_turn(self, session):
        try:
            self.session.hax2.move_being_on_map(self.subject, 1, 0)
        except:
            pass
