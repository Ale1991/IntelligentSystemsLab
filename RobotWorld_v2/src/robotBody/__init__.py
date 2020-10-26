from os import truncate
import threading, json, redis, time

from src.direction import Direction
from src.action import Action
from src.mapelement import MapElement
from utility import EnumEncoder

START_DIRECTION = Direction.NORD
STEP_DRAIN_AMT = 1
ROTATION_DRAIN_AMT = 1 # set 0 for free rotation cost 
MAX_BATTERY = 100
ROBOT_NAME = "R"

CH_IN= "CH_WORLD"
CH_OUT = "CH_BRAIN"

CH_BODY_WORLD = "CH_BODY_WORLD"# canale di comunicazione tra body e world
CH_BRAIN_BODY = "CH_BRAIN_BODY"# canale di comunicazione tra body e brain

class RobotBody(threading.Thread):

    direction: Direction
    x: int
    y: int
    sensor: list
    path: list

    max_battery : int # range: 0 - 100
    step_drain_amt: int
    rotation_drain_amt: int
    nome : str

    isRunning: bool

    def __init__(self):
        threading.Thread.__init__(self) # inziatilze superclass attribute
        self._Redis = redis.Redis() # init redis

        self.init_WorldListeners()
        self.init_BrainListeners()
        self.init_Robot()

    def init_WorldListeners(self):
        self._worldPubSub = self._Redis.pubsub()
        self._worldPubSub.subscribe(CH_BODY_WORLD)
        self._WorldListener = threading.Thread(target=self.listen_world)
        self._WorldListener.name = "RobotBody_WorldListener"
        self._WorldListener.start()

    def init_BrainListeners(self):
        self._brainPubSub = self._Redis.pubsub()
        self._brainPubSub.subscribe(CH_BRAIN_BODY)
        self._BrainListener = threading.Thread(target=self.listen_brain)
        self._BrainListener.name = "RobotBody_BrainListener"
        self._BrainListener.start()

    def init_Robot(self):
        self.direction = START_DIRECTION
        self.x, self.y = 14, 12
        self.sensor = [""]*3
        self.path = []

        self.step_drain_amt = STEP_DRAIN_AMT
        self.rotation_drain_amt = ROTATION_DRAIN_AMT
        self.max_battery = MAX_BATTERY
        self.nome = ROBOT_NAME

        self.isRunning = True

    def listen_world(self):
        for jsn in self._worldPubSub.listen(): # start listening
            if jsn["type"] == "message":
                jData = json.loads(jsn["data"])
                if "worldResponse" in jData: # se trova una response
                    if jData["worldResponse"] == "updateSensorResponse":
                        self.onUpdateSensorResponse(jData["x"], jData["y"], jData["sensor_array"])

    def listen_brain(self):
        for jsn in self._brainPubSub.listen(): # start listening
            if jsn["type"] == "message":
                jData = json.loads(jsn["data"])
                if "brainRequest" in jData: # se trova una response
                    action = json.loads(jData["Action"], object_hook=EnumEncoder.as_enum)
                    print(f"robotBody->listen_brain action: {action}")
                    self.onActionRequest(action)
                    self.updateSensorRequest()

    def rotate_robot(self, rotation):
        dir = Direction.NORD # Default rotation

        if rotation == Action.RD:
            if self.direction == Direction.NORD:
                dir = Direction.EST
            elif self.direction == Direction.EST:
                dir = Direction.SUD
            elif self.direction == Direction.SUD:
                dir = Direction.OVEST
            elif self.direction == Direction.OVEST:
                dir = Direction.NORD
            else:
                raise Exception("Action.RD ERROR")
        elif rotation == Action.RS:
            if self.direction == Direction.NORD:
                dir = Direction.OVEST
            elif self.direction == Direction.EST:
                dir = Direction.NORD
            elif self.direction == Direction.SUD:
                dir = Direction.EST
            elif self.direction == Direction.OVEST:
                dir = Direction.SUD
            else:
                raise Exception("Action.RS ERROR")
            self.max_battery -= self.rotation_drain_amt
        return dir

    def onActionRequest(self, action):
        print(f"onActionRequest: {action}, x: {self.x}, y: {self.y}")
        if action == Action.UPDATE_SONAR:
            self.updateSensorRequest()
        elif action == Action.STEP:
            self.step()
        elif action == Action.RS:
            self.direction = self.rotate_robot(Action.RS)
        elif action == Action.RD:
            self.direction = self.rotate_robot(Action.RD)


    def can_step(self):
        if self.sensor[1] == MapElement.FREE.value:
            return True
        elif self.sensor[1] == MapElement.ENERGY.value:
            return True
        else: #self.sensor[1] == MapElement.WALL:
            return False
        # else:
        #     raise Exception("Element sensor error in robotBody")

    # Incrementa le coordinate, consuma la batteria, guadagna energia all'occorrenza
    def on_step(self):
        if self.direction == Direction.NORD:
            self.y -= 1
        elif self.direction == Direction.EST:
            self.x += 1
        elif self.direction == Direction.SUD:
            self.y += 1
        elif self.direction == Direction.OVEST:
            self.x += -1

        if self.check_energy():
            self.on_energy_gain()

        self.max_battery -= self.step_drain_amt

    # Il brain richiede l'azione di step al body (attuazione)
    def step(self):
        if self.can_step():
            self.on_step()

    def updateSensorRequest(self):
        jsn_dir = json.dumps(self.direction, cls=EnumEncoder)
        jsn = json.dumps({ 'request': 'updateSensorRequest', 'x': self.x, 'y': self.y, 'direction': jsn_dir})
        self._Redis.publish(CH_BODY_WORLD, jsn)

    def check_energy(self):
        if self.sensor[1] == MapElement.ENERGY:
            return True
        else:
            return False
    def on_energy_gain(self):
        self.max_battery += MapElement.getEnergyValue()

    def onUpdateSensorResponse(self, x, y, sensor_array):
        self.x, self.y = x, y
        self.sensor = sensor_array
        jsn_dir = json.dumps(self.direction, cls=EnumEncoder)
        jsn = json.dumps({ 'bodyResponse': 'updateSensorResponse', 'x': x, 'y': y, 'sensor_array': sensor_array, 'direction':  jsn_dir})
        self._Redis.publish(CH_BRAIN_BODY, jsn)

    # Override del metodo del super() (threading.Thread.run())
    def run(self):
        pass