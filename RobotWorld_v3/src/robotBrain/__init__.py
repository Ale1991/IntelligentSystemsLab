import threading, json, redis, time

from src.direction import Direction
from src.action import Action
from src.mapelement import MapElement
from utility import EnumEncoder

# Robot Settings
START_DIRECTION = Direction.EST
MAX_BATTERY = 100
STEP_DRAIN_AMT = 1
ROTATION_DRAIN_AMT = 1 # set 0 for free rotation cost 
ROBOT_NAME = "R"

CH_BRAIN_BODY = "CH_BRAIN_BODY"

class RobotBrain(threading.Thread):
    
    max_battery : int # range: 0 - 100
    step_drain_amt: int
    rotation_drain_amt: int
    nome : str
    direction: Direction
    isLocked: bool
    goalReached: bool

    def __init__(self):
        threading.Thread.__init__(self) # inziatilze superclass attribute
        self._Redis = redis.Redis() # init redis
        self.init_BodyListener()
        self.init_Robot()

    def init_Robot(self):
        self.step_drain_amt = STEP_DRAIN_AMT
        self.rotation_drain_amt = ROTATION_DRAIN_AMT
        self.max_battery = MAX_BATTERY
        self.nome = ROBOT_NAME
        self.direction = None
        self.isLocked = False
        self.goalReached = False
        self._sensor_array = [""]*3
        self._alreadyTriedNord = False
        self._canStep = False

        self._canThink = False

    def init_BodyListener(self):
        self._pubsub = self._Redis.pubsub()
        self._pubsub.subscribe(CH_BRAIN_BODY)
        self._listener = threading.Thread(target=self.listen_body)
        self._listener.name = "RobotBrain_BodyListener"
        self._listener.start()

    def listen_body(self):
        for action_str in self._pubsub.listen(): # start listening
            if action_str["type"] == "message":
                jData = json.loads(action_str["data"])
                if "bodyResponse" in jData: # se trova una response
                    if jData["bodyResponse"] == "updateSensorResponse":
                        obj_dir = json.loads(jData['direction'], object_hook=EnumEncoder.as_enum)
                        self.onUpdateSensorResponse(jData["x"], jData["y"], jData["sensor_array"], obj_dir)

    def onUpdateSensorResponse(self, x, y, sensor_array, direction):
        self._sensor_array = sensor_array
        self._canThink = True
        self.direction = direction
        self.goalReached = self.checkGoal(x, y)

    def actionBodyRequest(self, action_list):
        if action_list != None:
            for action in action_list:
                jsn_act = json.dumps(action, cls=EnumEncoder)
                jsn = json.dumps({ 'brainRequest': 'Action', 'Action': jsn_act})
                self._Redis.publish(CH_BRAIN_BODY, jsn)

#region Decision Function
    def azione(self):
        # algoritmo di decisione su quale azione prendere
        # restituisce una lista di azioni da compiere
        if self.direction != Direction.NORD and self.direction != Direction.EST and self.direction != Direction.SUD and self.direction != Direction.OVEST :
            pass
        else:
            if self.isLocked == True:
                return self.randomPathfind()
            elif self.energyFound() == True:
                return self.pathfindToEnergy()
            elif self.direction != Direction.NORD and self._alreadyTriedNord == False:
                return self.tryNord()
            elif self.canGoForward() == True:
                return self.pathfindToForward()
            else:
                return self.randomPathfind()
         
    def tryNord(self):
        self._alreadyTriedNord = True
        self._canThink = False
        if self.direction == Direction.EST:
            return [Action.RS]
        elif self.direction == Direction.SUD:
            return [Action.RS, Action.RS]
        elif self.direction == Direction.OVEST:
            return [Action.RD]
        else:
            raise Exception("tryNord error direction")

    def energyFound(self):
        if MapElement.ENERGY.value in self._sensor_array:
            return True
        else:
            return False
       
    def pathfindToEnergy(self):
        self._canThink = False
        if self._sensor_array[1] == MapElement.ENERGY.value:
            return [Action.STEP] # step  
        elif self._sensor_array[0] == MapElement.ENERGY.value:
            return [Action.RS,  Action.STEP,  Action.RD,  Action.STEP] #, Action.RD, Action.STEP ruota a sx, step  
        elif self._sensor_array[2] == MapElement.ENERGY.value:
            return [Action.RD,  Action.STEP,  Action.RS,  Action.STEP] # ruota a dx, step

    def canGoForward(self):
        if MapElement.FREE.value in self._sensor_array:
            return True
        else:
            return False

    def pathfindToForward(self):
        self._alreadyTriedNord = False
        self._canThink = False
        if self._sensor_array[1] == MapElement.FREE.value:
            return [Action.STEP] # step    
        elif self._sensor_array[0] == MapElement.FREE.value:
            return [Action.RS, Action.STEP, Action.RD, Action.STEP] #, Action.RD, Action.STEP ruota a sx, step  
        elif self._sensor_array[2] == MapElement.FREE.value:
            return [Action.RD, Action.STEP, Action.RS, Action.STEP] # ruota a dx, step

    def randomPathfind(self):
        random_action_list = []
        if self.isLocked == True:
            random_action_list.append(Action.randomWithoutSonarAndStep(Action))
            random_action_list.append(Action.STEP)
        else:
            random_action_list.append(Action.randomWithoutSonarAndStep(Action))
            random_action_list.append(Action.STEP)
        self.isLocked = False
        self._canThink = False
        self._alreadyTriedNord = False
        return random_action_list
#endregion

    def checkGoal(self, x, y):
        if y <= 1:
            return True
        else:
            return False

    def run(self):
        while self.goalReached == False:
            print("-----------NEW ACTION-----------")
            self.actionBodyRequest(self.azione())
            time.sleep(0.1)