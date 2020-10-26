""""
    Simulatore della griglia in caselle

    "W": PARETE
    " ": SPAZIO LIBERO
    "E": ENERGIA
    "R": Robot

"""

from enum import Enum

# Quantita' di batteria fornita da una fonte di energia
ENERGY_VALUE = 100

class MapElement(Enum):
    WALL = "W"
    FREE = " "
    ENERGY = "E"
    ROBOT = "R"

    def getEnergyValue():
        return ENERGY_VALUE