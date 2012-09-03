class AzothObject(object):
    name = "azoth object"  # placeholder


class Reagent(object):
    """ Mix-in to identify classes as reagents. """
    pass


class SulphorousAsh(Reagent, AzothObject):
    name = "sulphorous ash"


class Ginseng(Reagent, AzothObject):
    name = "ginseng"


class Garlic(Reagent, AzothObject):
    name = "garlic"


class SpiderSilk(Reagent, AzothObject):
    name = "spider silk"


class BloodMoss(Reagent, AzothObject):
    name = "blood moss"


class BlackPearl(Reagent, AzothObject):
    name = "black pearl"


class Nightshade(Reagent, AzothObject):
    name = "nightshade"


class Mandrake(Reagent, AzothObject):
    name = "mandrake"


class RoyalCape(Reagent, AzothObject):
    name = "royal cape"
