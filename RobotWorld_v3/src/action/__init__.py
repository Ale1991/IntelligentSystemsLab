import random
from enum import Enum

class Action(Enum):
    RD = 1
    RS = 2
    STEP = 3
    UPDATE_SONAR = 4

    def randomWithoutSonar(self):
        return Action(random.randrange(1, 4, 1))

    def randomWithoutSonarAndStep(self):
        return Action(random.randrange(1, 3, 1))

    def values():
        return [act.value for act in Action]