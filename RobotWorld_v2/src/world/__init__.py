import json, redis, threading, time

from utility import EnumEncoder
from src.action import Action
from src.direction import Direction
from src.mapelement import MapElement

CH_BODY_WORLD = "CH_BODY_WORLD"
CH_SIMULATOR = "CH_SIMULATOR"

class World(threading.Thread):

    mappa : list
    X_MAX: int
    Y_MAX: int
    isRunning: bool

    robotX: int
    robotY: int
    robotDirection: Direction


    def __init__(self, file_mappa_name):
        threading.Thread.__init__(self) # inziatilze superclass attribute
        self._Redis = redis.Redis() # init redis

        self.init_BodyListener()
        
        self.isRunning = True

        self.init_map(file_mappa_name)

        self.robotX, self.robotY = None, None
        self.robotDirection = None

    def __repr__(self):
        out = ""
        for riga in self.mappa:
            out += riga
        return out

    def init_map(self, file_mappa_name):
        f = open(file_mappa_name, "r")
        self.mappa = [line.rstrip('\n') for line in f.readlines()]
        self.X_MAX, self.Y_MAX = 0, len(self.mappa)
        for riga in self.mappa:
            if len(riga) > self.X_MAX:
                self.X_MAX = len(riga)
        f.close()

    def init_BodyListener(self):
        self._bodyPubSub = self._Redis.pubsub()
        self._bodyPubSub.subscribe(CH_BODY_WORLD)
        self._BodyListener = threading.Thread(target=self.listen_body_request)
        self._BodyListener.name = "World_BodyRequestListener"
        self._BodyListener.start()

    def listen_body_request(self):
        for action_str in self._bodyPubSub.listen(): # start listening
            if action_str["type"] == "message":
                jData = json.loads(action_str["data"])
                if "request" in jData: # se trova una request
                    if jData["request"] == "updateSensorRequest":
                        self.onUpdateSensorRequest(jData["x"], jData["y"], json.loads(jData["direction"], object_hook=EnumEncoder.as_enum))
                    # RIDONDANZA PER ASSICURARE LE CONDIZIONI DI STEP IN CASO DI RACE CONDITION (FINIRE DI IMPLEMENTARE SE NECESSARIO)
                    elif jData["request"] == "canStepRequest":
                        self.onCanStepRequest(jData["x"], jData["y"], json.loads(jData["direction"], object_hook=EnumEncoder.as_enum))

    # Trigger: al verificarsi di una richiesta di update_sensori
    def onUpdateSensorRequest(self, x, y, direction):
        self.updateSensorResponse(x, y, direction)

    # Response da World a RobotBody
    def updateSensorResponse(self, x, y, direction):
        # print(f"onUpdateSensorRequest: x={x}, y= {y}, direction={direction}")
        # ritorno il vettore dei sensori, sul canale CH_BODY_WORLD, sotto il nome updateSensorResponse
        # ritorno un json con: response:  onUpdateSensorResponse, sensor_array : [MapElement, MapElement, MapElement]
        sensor_array = self.calc_robot_sonar(x, y, direction)

        jsn = json.dumps({ 'worldResponse': 'updateSensorResponse', 'x': x, 'y': y, 'sensor_array': sensor_array})
        self._Redis.publish(CH_BODY_WORLD, jsn)

        self.updateRobotPosition(x ,y, direction)


    # Aggiorno la conoscenza che ha la mappa sulla posizione del robot e la sua direzione
    def updateRobotPosition(self, x, y, direction):
        self.robotX, self.robotY, self.robotDirection = x, y, direction
        self.updateMap()
        self.publishMapInfo()
        self.publishRobotInfo()

    def updateMap(self):
        self.change_carattere(self.robotX, self.robotY, MapElement.ROBOT.value)

    def change_carattere(self, x, y, carattere):
        new_riga = self.mappa[y][0:x]
        new_riga += carattere
        new_riga += self.mappa[y][x + 1:]
        self.mappa[y] = new_riga

    # UNUSED - DA FIXARE
    def check_map_bounds(self, temp_x, temp_y):
        if temp_x < 1: temp_x = 1
        if temp_y < 1: temp_y = 1
        if temp_x > self.X_MAX - 1: temp_x = self.X_MAX
        if temp_y > self.Y_MAX - 1: temp_y = self.Y_MAX
        return temp_x, temp_y

    def peek_mappa(self, x, y, dx, dy):
        riga = y + dy
        colonna = x + dx
        #colonna , riga = self.check_map_bounds(colonna, riga) # bug su prima e ultima colonna, da fixare check_map_bounds (serve adesso?)
        return self.mappa[riga][colonna]

    def calc_robot_sonar(self, x, y, direction):
        # Simula i valori dei sensori sonar del robot
        # Il robot guarda sempre a NORD
        if direction == Direction.NORD:
            S = self.peek_mappa(x, y, -1, -1)
            C = self.peek_mappa(x, y,  0, -1)
            D = self.peek_mappa(x, y,  1, -1)
        elif direction == Direction.EST:
            S = self.peek_mappa(x, y,  1, -1)
            C = self.peek_mappa(x, y,  1,  0)
            D = self.peek_mappa(x, y,  1,  1)
        elif direction == Direction.SUD:
            S = self.peek_mappa(x, y,  1,  1)
            C = self.peek_mappa(x, y,  0,  1)
            D = self.peek_mappa(x, y, -1,  1)
        elif direction == Direction.OVEST:
            S = self.peek_mappa(x, y, -1,  1)
            C = self.peek_mappa(x, y, -1,  0)
            D = self.peek_mappa(x, y, -1, -1)
        else:
            raise Exception("Wrong Direction")
        return [S, C, D]

    # toDO
    def computeGoalReached(self):
        return 'toDo'

    def publishRobotInfo(self):
        jsn_dir = json.dumps(self.robotDirection, cls=EnumEncoder)
        jsn = json.dumps({ 'worldInfo': 'robotInfo', 'x': self.robotX, 'y': self.robotY, 'direction': jsn_dir, 'isLocked': 'toDo', 'goalReached': self.computeGoalReached(), 'robotBattery':'toDo'})
        self._Redis.publish(CH_SIMULATOR, jsn)

    def publishMapInfo(self):
        jsn = json.dumps({'worldInfo': 'mapInfo', 'mappa': self.mappa})
        self._Redis.publish(CH_SIMULATOR, jsn)

    # Override del metodo del super() (threading.Thread.run())
    def run(self):
        pass
