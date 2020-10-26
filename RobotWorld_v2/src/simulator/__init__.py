import threading, pygame, redis, json
from src.mapelement import MapElement
from src.direction import Direction
from utility import EnumEncoder

# Necessario inizializzare qui per poter assegnare i valori globali
pygame.init()

# Color
BLACK = (0, 0, 0)
WHITE = (200, 200, 200)
GREEN = (0, 250, 0)
RED = (250, 0, 0)
YELLOW = (255,255,0)
BLUE = (0, 0, 255)

# Window Variable
WINDOW_HEIGHT = 500
WINDOW_WIDTH = 1000
GRID_BLOCK_SIZE = 20
BLOCK_HEIGHT = 20
BLOCK_WIDTH = 20
BLOCK_MARGIN = 5
SCREEN = pygame.display.set_mode([WINDOW_WIDTH, WINDOW_HEIGHT])
CLOCK = pygame.time.Clock()
FONT = pygame.font.SysFont("monospace", 16)
SIM_TICK = 15

# Robot Start Coordinate
x0, y0 = 14, 12

# STEP MODE (Press key for manual steps)
AUTO_STEP = True

CH_SIMULATOR = "CH_SIMULATOR"

class Simulator(threading.Thread):

    mappa : list
    step_counter: int

    def __init__(self):
        threading.Thread.__init__(self) # inziatilze superclass attribute
        self._Redis = redis.Redis() # init redis
        self._pubsub = self._Redis.pubsub()
        self._pubsub.subscribe(CH_SIMULATOR)

        self._listener = threading.Thread(target=self.listen_world_info)
        self._listener.name = "Simulator_WorldListener"
        self._listener.start()

        self.mappa = None

        self._robotBattery = None
        self._robotDirection = None
        self._Rx, self._Ry = None, None
        self._robotIsLocked = None
        self._robotGoalReached = False

    def listen_world_info(self):
        for action_str in self._pubsub.listen(): # start listening
            if action_str["type"] == "message":
                jData = json.loads(action_str["data"])
                if "worldInfo" in jData: # se trova una info
                    if jData["worldInfo"] == "robotInfo":
                        self.onRobotInfoReceived(jData["x"], jData["y"], json.loads(jData["direction"], object_hook=EnumEncoder.as_enum), jData["isLocked"], jData["goalReached"], jData['robotBattery'])
                    elif jData["worldInfo"] == "mapInfo":
                        self.onMapInfoReceived(jData["mappa"])

    def onRobotInfoReceived(self, x, y, direction, isLocked, goalReached, robotBattery):
        self._Rx, self._Ry = x, y
        self._robotDirection = direction
        self._robotIsLocked = isLocked
        #self._robotGoalReached = goalReached
        self._robotBattery = robotBattery

    def onMapInfoReceived(self, mappa):
        self.mappa = mappa

    def isNullRobotValue(self):
        # if self._robotDirection != None and self._Rx != None and self._Ry != None and self._robotIsLocked != None and self._robotBattery != None:
        bool = None in {self._robotDirection, self._robotBattery, self._robotIsLocked, self._Rx, self._Ry, self._robotGoalReached}
        if bool == True:
            return True
        else:
            return False

    def printRobotInfo(self):
        if self.isNullRobotValue() == False:
            pygame.draw.rect(SCREEN, RED, [(BLOCK_MARGIN + BLOCK_WIDTH) * self._Rx, (BLOCK_MARGIN + BLOCK_HEIGHT) * self._Ry, BLOCK_WIDTH + BLOCK_MARGIN, BLOCK_HEIGHT])
            if self._robotDirection == Direction.NORD:
                pygame.draw.rect(SCREEN, YELLOW, [(BLOCK_MARGIN + BLOCK_WIDTH) * (self._Rx - 1)  , (BLOCK_MARGIN + BLOCK_HEIGHT) * (self._Ry - 1), (BLOCK_WIDTH + BLOCK_MARGIN)* 3, BLOCK_HEIGHT], 1)
            elif self._robotDirection == Direction.EST:
                pygame.draw.rect(SCREEN, YELLOW, [(BLOCK_MARGIN + BLOCK_WIDTH) * (self._Rx + 1)  , (BLOCK_MARGIN + BLOCK_HEIGHT) * (self._Ry - 1), BLOCK_WIDTH, (BLOCK_HEIGHT + BLOCK_MARGIN)* 3], 1)
            elif self._robotDirection == Direction.SUD:
                pygame.draw.rect(SCREEN, YELLOW, [(BLOCK_MARGIN + BLOCK_WIDTH) * (self._Rx - 1)  , (BLOCK_MARGIN + BLOCK_HEIGHT) * (self._Ry + 1), (BLOCK_WIDTH + BLOCK_MARGIN)* 3, BLOCK_HEIGHT], 1)
            elif self._robotDirection == Direction.OVEST:
                pygame.draw.rect(SCREEN, YELLOW, [(BLOCK_MARGIN + BLOCK_WIDTH) * (self._Rx - 1)  , (BLOCK_MARGIN + BLOCK_HEIGHT) * (self._Ry - 1), BLOCK_WIDTH, (BLOCK_HEIGHT + BLOCK_MARGIN)* 3], 1)

    def printMapInfo(self):
        if self.mappa != None:
            for i in range(len(self.mappa)):
                for j in range(len(self.mappa[i])):
                    if self.mappa[i][j] == MapElement.FREE.value:
                        pygame.draw.rect(SCREEN, BLACK, [(BLOCK_MARGIN + BLOCK_WIDTH) * j, (BLOCK_MARGIN + BLOCK_HEIGHT) * i, BLOCK_WIDTH, BLOCK_HEIGHT])
                    elif self.mappa[i][j] == MapElement.ENERGY.value:
                        pygame.draw.rect(SCREEN, GREEN, [(BLOCK_MARGIN + BLOCK_WIDTH) * j, (BLOCK_MARGIN + BLOCK_HEIGHT) * i, BLOCK_WIDTH, BLOCK_HEIGHT])         
                    elif self.mappa[i][j] == MapElement.ROBOT.value:
                        pygame.draw.rect(SCREEN, RED, [(BLOCK_MARGIN + BLOCK_WIDTH) * j, (BLOCK_MARGIN + BLOCK_HEIGHT) * i, BLOCK_WIDTH, BLOCK_HEIGHT])             
                    else:
                        pygame.draw.rect(SCREEN, WHITE, [(BLOCK_MARGIN + BLOCK_WIDTH) * j, (BLOCK_MARGIN + BLOCK_HEIGHT) * i, BLOCK_WIDTH, BLOCK_HEIGHT])
        else:
            waitingMap_text = FONT.render(f"WAITING MAP INFO", 1, WHITE)
            SCREEN.blit(waitingMap_text, ((WINDOW_WIDTH / 2) - 50, (WINDOW_HEIGHT / 2) - 8))

    def print_text(self):
        # stepCounter_text = FONT.render(f"STEP_COUNT: {self.step_counter}", 1, WHITE)
        # SCREEN.blit(stepCounter_text, (5, 480))

        auto_text = FONT.render(f"AUTO_STEP_MODE: {AUTO_STEP}", 1, BLUE)
        SCREEN.blit(auto_text, (5, 420))

        if self.isNullRobotValue() == False:
            pass
            # batteryColor = GREEN if self._robotBattery > 0 else RED
            # battery_text = FONT.render(f"BATTERY: {self._robotBattery}", 1, batteryColor)
            # SCREEN.blit(battery_text, (200, 480))

            # lockedColor = RED if self._robotIsLocked == True else GREEN
            # isLocked_text = FONT.render(f"isLocked: {self._robotIsLocked}", 1, lockedColor)
            # SCREEN.blit(isLocked_text, (5, 450))

            # goalColor = GREEN if self._robotGoalReached == True else RED
            # goal_reached_text = FONT.render(f"GOAL_REACHED: {self._robotGoalReached}", 1, goalColor)
            # SCREEN.blit(goal_reached_text, (200, 450))

    def print(self):
        SCREEN.fill(BLACK)
        self.print_text()
        self.printMapInfo()
        self.printRobotInfo()
        pygame.display.update()
        CLOCK.tick(SIM_TICK)

    def run(self):
        run = True
        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    run = False
            #if self._robotGoalReached == False:
            self.print()
        pygame.quit()
