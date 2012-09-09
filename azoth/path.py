import heapq

class Step(object):

    def __init__(self, loc, nearness=0, cost=0, depth=0, nextstep=None):
        self.loc = loc
        self.nearness = nearness
        self.cost = cost
        self.nextstep = nextstep
        if nextstep is not None:
            self.depth = nextstep.depth + 1
        else:
            self.depth = 0

    def __repr__(self):
        return "{} {}/{}:{}".format(self.loc, self.nearness, self.cost, 
                                    self.depth)

# (dx, dy) of 4 neighbors
directions = ((-1, 0), (1, 0), (0, -1), (0, 1))


def find(src, dst, is_valid, heuristic, max_depth=100):
    """
    'heuristic' expects the current location and destination and returns
    nearness and cost as a tuple. nearness evaluates how near the location is
    to the destination, so a lower number is better. (It could be generalized
    to mean desirability of a location and allowed to go negative.) Cost is the
    incremental cost of stepping here, and could also include risk factors for
    anything undesirable on the step. The nearness will be increased by the cost.
    """
    pq = []
    found = {}
    nearness, cost = heuristic(src, dst)
    step = Step(src, nearness)
    heapq.heappush(pq, (step.nearness, id(step), step))
    found[src] = step
    print("{} -> {}".format(src, dst))
    while pq:
        print(pq)
        priority, _id, step = heapq.heappop(pq)

        # Check if goal reached.
        if step.loc == dst:
            path = []
            path.append(step)
            print('final step:{}'.format(step))
            while step.nextstep is not None:
                step = step.nextstep
                path.append(step)
            return [x.loc for x in reversed(path)]

        # Check if path too long.
        if step.depth == max_depth:
            continue

        # Schedule the four neighbors, if valid
        for direction in directions:

            newloc = (step.loc[0] + direction[0], step.loc[1] + direction[1])

            if not is_valid(newloc):
                continue

            nearness, cost = heuristic(newloc, dst)
            print('{} cost={}+{}, nearness={}+{}'.format(newloc, cost, step.cost, nearness, cost + step.cost))
            cost += step.cost
            nearness += cost

            # Check if we already have a route here
            old = found.get(newloc, None)
            if old is not None:
                if nearness > old.nearness:
                    # The old one is better so ignore the new one.
                    continue
                else:
                    # The new one is better so discard the old one.
                    try:
                        index = pq.index((old.nearness, id(old), old) )
                        del pq[index]
                    except ValueError:
                        pass

            newstep = Step(newloc, nearness=nearness, cost=cost, nextstep=step)
            heapq.heappush(pq, (newstep.nearness, id(newstep), newstep))
            found[newloc] = newstep

    # No path found
    return []
            
