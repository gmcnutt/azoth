import event
import executor
import path
import place
import pygame


class Controller(object):

    def __init__(self, subject, session):
        self.subject = subject
        self.session = session
        self.path = None


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
    
    def follow_path(self):
        x, y = self.path.pop(0)
        dx = x - self.subject.x
        dy = y - self.subject.y
        self.session.hax2.move_being_on_map(self.subject, dx, dy)

    def do_turn(self, event_loop):
        """ Let the player control the subject during the turn. """
        if self.path:
            print(self.path)
            try:
                self.follow_path()
            except place.PlaceError:
                self.path = None
            except executor.RuleError:
                self.path = None
        else:
                event_loop.resume()

    def teleport(self, x, y):
        try:
            self.session.hax2.teleport_being_on_map(self.subject, x, y)
        except place.PlaceError:
            return
        except executor.RuleError:
            return
        raise event.Handled()
        


class Beeline(Controller):

    def do_turn(self, session):
        try:
            self.session.hax2.move_being_on_map(self.subject, 1, 0)
        except:
            pass


class Follow(Controller):

    def __init__(self, target, *args, **kwargs):
        """ 'target' is the object to follow. """
        super(Follow, self).__init__(*args, **kwargs)
        self.target = target

    def check_neighbor(self, pla, x, y):
        try:
            if x != self.target.x and y != self.target.y:
                self.session.rules.assert_unoccupied(pla, x, y)
            self.session.rules.assert_passable(self.subject, pla, x, y)
            return True
        except executor.RuleError:
            return False

    def neighbors(self, loc):
        return self.session.rules.get_neighbors(self.subject.place, *loc, 
                                                filter=self.check_neighbor)

    def heuristic(self, loc, dst):
        # use city-block distance; return cost, nearness
        x, y = loc
        dx = abs(dst[0] - x)
        dy = abs(dst[1] - y)
        nearness = dx + dy
        pla = self.subject.place
        cost = self.session.rules.get_movement_cost(self.subject.mmode, pla, x, y)
        cost += 1  # XXX: necessary?
        return nearness, cost

    def do_turn(self, session):
        p = path.find(self.subject.xy, self.target.xy, self.neighbors,
                      self.heuristic)
        if len(p) > 1:
            loc = p[0]
            dx = loc[0] - self.subject.x
            dy = loc[1] - self.subject.y
            self.session.hax2.move_being_on_map(self.subject, dx, dy)
