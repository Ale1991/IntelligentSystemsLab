""""
    Simulatore della griglia in caselle

    "W": PARETE
    " ": SPAZIO LIBERO
    "E": ENERGIA
    "R": Robot

"""

from enum import Enum

class MapElement(Enum):
    WALL = "W"
    FREE = " "
    ENERGY = "E"
    ROBOT = "R"