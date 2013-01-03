import event
import executor
import logging
import path
import place

logger = logging.getLogger('controller')

class Controller(object):
    """ Base class for all controllers. """
    def __init__(self, subject, session):
        self.subject = subject
        self.session = session
        self.path = None
        self.on_end_of_path = None

class Player(Controller):
    """ A controller that lets the player direct the subject. """
    def move_or_swap(self, dx, dy):
        """ Try to move; if blocked by an occupant try to swap. """
        try:
            self.session.hax2.move_being_on_map(self.subject, dx, dy)
        except executor.Occupied, e:
            self.session.hax2.rotate_beings_on_map(self.subject, e.occupant)

    def move(self, dx, dy):
        """ Move the subject. """
        try:
            self.move_or_swap(dx, dy)
        except place.PlaceError:
            return
        except executor.RuleError:
            return
        import traceback
        for x in traceback.format_stack():
            logger.debug(x)
        logger.debug('moved {} {} {}'.format(self.subject, dx, dy))
        raise event.Handled()

    def get(self):
        """ Have the subject pick up something on the ground at his feet. """
        items = self.session.world.get_items(self.subject.x,
                                             self.subject.y)
        if items:
            item = items[0]
            being = self.subject
            self.session.hax2.move_item_from_map_to_being(item, being)
            raise event.Handled()

    def drop(self):
        """ Have the subject drop something from inventory to the ground. """
        being = self.subject
        items = being.body.get()
        if items:
            item = items[0]
            self.session.hax2.move_item_from_being_to_map(item, being)
            raise event.Handled()

    def follow_path(self):
        """ Take the next step along the saved path. """
        step = self.path.pop(0)
        if callable(step):
            return step()
        x, y = step
        dx = x - self.subject.x
        dy = y - self.subject.y
        try:
            self.move_or_swap(dx, dy)
        except place.PlaceError:
            self.path = None
        except executor.RuleError:
            self.path = None
        raise event.Handled()

    def teleport(self, x, y):
        """ Jump to a location. """
        try:
            self.session.hax2.teleport_being_on_map(self.subject, x, y)
        except place.PlaceError:
            return
        except executor.RuleError:
            return
        raise event.Handled()
        
    def filter_neighbor(self, pla, x, y):
        """ Return True iff this tile looks ok for pathfinding. """
        try:
            self.session.rules.assert_passable(self.subject, pla, x, y)
            return pla.get_explored(x, y)
        except executor.RuleError:
            return False

    def neighbors(self, loc):
        """ Enumerate neighbors for pathfinding. """
        return self.session.rules.get_neighbors(self.subject.place, *loc, 
                                                filter=self.filter_neighbor)

    def heuristic(self, loc, dst):
        """ Evaluate the tile for pathfinding. """
        # use city-block distance; return cost, nearness
        x, y = loc
        dx = abs(dst[0] - x)
        dy = abs(dst[1] - y)
        nearness = dx + dy
        pla = self.subject.place
        mmode = self.subject.mmode
        cost = self.session.rules.get_movement_cost(mmode, pla, x, y)
        cost += 1  # XXX: necessary?
        return nearness, cost

    def pathfind_to(self, x, y):
        """ Find and start following a path to (x, y). """
        src = self.subject.xy
        self.path = path.find(src, (x, y), self.neighbors, self.heuristic)
        return self.path


class Follow(Controller):
    """ AI that follows a target around. """
    def __init__(self, target, *args, **kwargs):
        """ 'target' is the object to follow. """
        super(Follow, self).__init__(*args, **kwargs)
        self.target = target
        self.subject.order = self.target.order + 1

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
        cost = self.session.rules.get_movement_cost(self.subject.mmode, pla, x,
                                                    y)
        cost += 1  # XXX: necessary?
        return nearness, cost

    def do_turn(self, session):
        p = path.find(self.subject.xy, self.target.xy, self.neighbors,
                      self.heuristic)
        logger.debug('xy={}'.format(self.subject.xy))
        logger.debug('path={}'.format(p))
        if len(p) > 1:
            loc = p[0]
            dx = loc[0] - self.subject.x
            dy = loc[1] - self.subject.y
            logger.debug('move {} {}'.format(dx, dy))
            try:
                self.session.hax2.move_being_on_map(self.subject, dx, dy)
            except executor.Occupied:
                pass
