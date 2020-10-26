"""
    Definizione del Robot 2D
    Può mouoversi soltanto d 1 step sulla griglia
    Per muoversi deve produrre un'azione:
    N: Nord
    S: Sud
    E: Est
    O: Ovest
    RS : rotazione a sinistra
    RD : rotazione a destra

    Ogni passo consuma il valore di step_drain_amt dalla max_battery
    Prima dell'azione misura i suoi sensori:
    sonar: [S, C, D]
    bussola: direzione della testa {N,S,E,O}
    Se la max_battery sta a zero non si può muovere

    GOAL: partendo da una qualsiasi posizione interna
    nel labirinto e qualsiasi angolo di rotazione inizale,
            ANDARE VERSO NORD

"""
from enum import Enum
import random
if __name__ != "__main__":
    from src.mapelement import MapElement

class Direction(Enum):
     NORD = 1
     EST = 2
     SUD = 3
     OVEST = 4
     

class Action(Enum):
    RD = 1
    RS = 2
    STEP = 3
    UPDATE_SONAR = 4

    def randomWithoutSonar(self):
        return Action(random.randrange(1, 4, 1))

    def randomWithoutSonarAndStep(self):
        return Action(random.randrange(1, 3, 1))

# Robot Settings
START_DIRECTION = Direction.EST
MAX_BATTERY = 100
STEP_DRAIN_AMT = 1
ROTATION_DRAIN_AMT = 1 # set 0 for free rotation cost 
ROBOT_NAME = "R"

class Robot:
    
    max_battery : int # range: 0 - 100
    step_drain_amt: int
    rotation_drain_amt: int
    nome : str
    direction: Direction
    isLocked: bool
    isRunning: bool

    def __init__(self):
        self.step_drain_amt = STEP_DRAIN_AMT
        self.rotation_drain_amt = ROTATION_DRAIN_AMT
        self.max_battery = MAX_BATTERY
        self.nome = ROBOT_NAME
        self.direction = START_DIRECTION
        self._sensori = [""]*3
        self.isLocked = False
        self.isRunning = True
        self.alreadyTriedNord = False

    def misura_sensori(self, array_sensori):
        self._sensori = array_sensori

    def azione(self):
        # algoritmo di decisione su quale azione prendere
        # restituisce una lista di azioni da compiere
        if self.isLocked == True:
            return self.randomPathfind()
        elif self.energyFound() == True:
            return self.pathfindToEnergy()
        elif self.direction != Direction.NORD and self.alreadyTriedNord == False:
            return self.tryNord()
        elif self.canGoForward() == True:
            return self.pathfindToForward()
        else:
            return self.randomPathfind()
         
    def tryNord(self):
        self.alreadyTriedNord = True
        if self.direction == Direction.EST:
            return [Action.RS, Action.UPDATE_SONAR]
        elif self.direction == Direction.SUD:
            return [Action.RS, Action.RS, Action.UPDATE_SONAR]
        elif self.direction == Direction.OVEST:
            return [Action.RD, Action.UPDATE_SONAR]
        else:
            raise Exception("tryNord error direction")

    def energyFound(self):
        if MapElement.ENERGY.value in self._sensori:
            return True
        else:
            return False
       
    def pathfindToEnergy(self):
        if self._sensori[1] == MapElement.ENERGY.value:
            return [Action.STEP] # step  
        elif self._sensori[0] == MapElement.ENERGY.value:
            return [Action.RS, Action.STEP, Action.RD, Action.STEP] #, Action.RD, Action.STEP ruota a sx, step  
        elif self._sensori[2] == MapElement.ENERGY.value:
            return [Action.RD, Action.STEP, Action.RS, Action.STEP] # ruota a dx, step

    def canGoForward(self):
        if MapElement.FREE.value in self._sensori:
            return True
        else:
            return False

    def pathfindToForward(self):
        self.alreadyTriedNord = False
        if self._sensori[1] == MapElement.FREE.value:
            return [Action.STEP] # step    
        elif self._sensori[0] == MapElement.FREE.value:
            return [Action.RS, Action.STEP, Action.RD, Action.STEP] #, Action.RD, Action.STEP ruota a sx, step  
        elif self._sensori[2] == MapElement.FREE.value:
            return [Action.RD, Action.STEP, Action.RS, Action.STEP] # ruota a dx, step

    def randomPathfind(self):
        random_action_list = []
        if self.isLocked == True:
            random_action_list.append(Action.randomWithoutSonarAndStep(Action))
            random_action_list.append(Action.STEP)
        else:
            random_action_list.append(Action.randomWithoutSonarAndStep(Action))
        self.isLocked = False
        return random_action_list


# Test Unit
if __name__ == "__main__":   
    for i in range(10):
        random_action_list = []
        for i in range(3):
            random_action_list.append(Action.randomWithoutSonar(Action))
        print(random_action_list)
