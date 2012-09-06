import event
import executor
import place
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
        raise event.Handled()

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
            raise event.Handled()

    def drop(self):
        """ Have the subject drop something from inventory to the ground. """
        being = self.subject
        items = being.body.get()
        if items is not None:
            item = items[0]
            self.session.hax2.move_item_from_being_to_map(item, being)
            raise event.Handled()

    def quit(self):
        """ Raise the Quit exception to signal the player is done. """
        raise event.Quit()
    
    def do_turn(self, event_loop):
        """ Let the player control the subject during the turn. """
        event_loop.resume()


class Beeline(Controller):

    def do_turn(self, session):
        try:
            self.session.hax2.move_being_on_map(self.subject, 1, 0)
        except:
            pass
