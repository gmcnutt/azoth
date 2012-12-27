class Terrain(object):
    name = None
    pclass = None
    blocks_sight = False

    def __str__(self):
        return self.name

class Ankh(Terrain):
    name = 'ankh'
    pclass = 'wall'

class HeavyForest(Terrain):
    name = 'heavy forest'
    pclass = 'forest'
    blocks_sight = True


class Forest(Terrain):
    name = 'forest'
    pclass = 'trees'


class Grass(Terrain):
    name = 'grass'
    pclass = 'grass'


class Trail(Terrain):
    name = 'trail'
    pclass = 'road'


class RockWall(Terrain):
    name = 'rock wall'
    pclass = 'wall'
    blocks_sight = True


class CounterTop(Terrain):
    name = 'countertop'
    pclass = 'wall'


class Water(Terrain):
    name = 'water'
    pclass = 'water'


class Boulder(Terrain):
    name = 'boulder'
    pclass = 'boulder'


class CobbleStone(Terrain):
    name = 'floor'
    pclass = 'road'


class Bog(Terrain):
    name = 'bog'
    pclass = 'sludge'


class FirePlace(Terrain):
    name = 'fireplace'
    pclass = 'road'
    blocks_sight = True


class Window(Terrain):
    name = 'window'
    pclass = 'wall'


class Unmapped(Terrain):
    name = '?'
    pclass = '?'
