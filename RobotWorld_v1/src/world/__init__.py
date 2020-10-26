import pygame
from src.robot import Action, Direction, Robot
from src.mapelement import MapElement

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
SIM_TICK = 10

# Robot Start Coordinate
x0, y0 = 14, 12

# STEP MODE (Press key for manual steps)
AUTO_STEP = True

# Quantita' di batteria fornita da una fonte di energia
ENERGY_VALUE = 100

class World():

    mappa : list
    robot: Robot
    step_counter: int
    goal_reached: bool
    X_MAX: int
    Y_MAX: int
    robot_path: list

    def __init__(self, file_mappa_name):
        f = open(file_mappa_name, "r")
        self._Rx = x0
        self._Ry = y0
        self._prev_x = self._Rx
        self._prev_y = self._Ry
        self.step_counter = 0
        self.goal_reached = False
        self.X_MAX, self.Y_MAX = 0, 0
        self.mappa = [line.rstrip('\n') for line in f.readlines()]
        self.Y_MAX = len(self.mappa)
        self.robot_path = []
        for riga in self.mappa:
            if len(riga) > self.X_MAX:
                self.X_MAX = len(riga)
        f.close()

    def __repr__(self):
        out = ""
        for riga in self.mappa:
            new = riga
            out += riga
        return out

    def change_carattere(self, x, y, carattere):
        new_riga = self.mappa[y][0:x]
        new_riga += carattere
        new_riga += self.mappa[y][x + 1:]
        self.mappa[y] = new_riga
    
    def insert_robot(self, robot):
        self.robot = robot
        self.change_carattere(x0, y0, MapElement.ROBOT.value)
        self.calc_robot_sonar()
        self.robot.r_map = self

    def compute_isLocked(self):
        self.robot_path.append([self._prev_x, self._prev_y])
        if len(self.robot_path) > 10:
            last_three_element = self.robot_path[-10:]
            # print(f"l3e: {last_three_element} + Rx,Ry={[self._prev_x, self._prev_y]}")
            if last_three_element.count([self._prev_x, self._prev_y]) == len(last_three_element):# tutti e 10 le coppie sono uguali
                self.robot.isLocked = True

    def can_step(self):
        if self.robot._sensori[1] == MapElement.WALL.value:
            return False
        elif self.robot._sensori[1] == MapElement.ROBOT.value and self.robot.isLocked == False:
            return False
        else:
            return True

    def step_robot(self):      
        self._prev_x, self._prev_y = self._Rx, self._Ry
        if self.can_step() == True:
            if self.robot.direction == Direction.NORD:
                self._Rx, self._Ry = self.check_map_bounds(self._Rx, self._Ry - 1)
            elif self.robot.direction == Direction.EST:
                self._Rx, self._Ry = self.check_map_bounds(self._Rx + 1, self._Ry)
            elif self.robot.direction == Direction.SUD:
                self._Rx, self._Ry = self.check_map_bounds(self._Rx, self._Ry + 1)
            elif self.robot.direction == Direction.OVEST:
                self._Rx, self._Ry = self.check_map_bounds(self._Rx - 1, self._Ry)
            
            if self.mappa[self._Ry][self._Rx] == MapElement.ENERGY.value:
                self.robot.max_battery += ENERGY_VALUE
            # self.change_carattere(prev_x, prev_y, MapElement.FREE.value) # non salva la posizione dove e' passato
            self.change_carattere(self._Rx, self._Ry, MapElement.ROBOT.value)
            self.robot.max_battery -= self.robot.step_drain_amt
            self.robot.alreadyTriedNord = False

    def rotate_robot(self, rotation):
        dir = Direction.NORD # Default rotation

        if rotation == Action.RD:
            if self.robot.direction == Direction.NORD:
                dir = Direction.EST
            elif self.robot.direction == Direction.EST:
                dir = Direction.SUD
            elif self.robot.direction == Direction.SUD:
                dir = Direction.OVEST
            elif self.robot.direction == Direction.OVEST:
                dir = Direction.NORD
            else:
                raise Exception("Action.RD ERROR")
        elif rotation == Action.RS:
            if self.robot.direction == Direction.NORD:
                dir = Direction.OVEST
            elif self.robot.direction == Direction.EST:
                dir = Direction.NORD
            elif self.robot.direction == Direction.SUD:
                dir = Direction.EST
            elif self.robot.direction == Direction.OVEST:
                dir = Direction.SUD
            else:
                raise Exception("Action.RS ERROR")
            self.robot.max_battery -= self.robot.rotation_drain_amt
        return dir

    def do_robot_action(self):
        if self.robot.max_battery < max(self.robot.step_drain_amt, self.robot.rotation_drain_amt):
            self.robot.isRunning = False # OUT OF BATTERY
        elif self._Ry == 1:
            self.goal_reached = True # GOAL REACHED
        else:           
            self.execute_actions() # NORMAL EXEC

    def execute_actions(self):
        self.calc_robot_sonar()
        action_list = self.robot.azione()

        if len(action_list) > 0:
            for action in action_list:
                self.calc_robot_sonar()
                self.step_counter += 1
                self.compute_isLocked()
                if action == Action.STEP:
                    if self.can_step() == True:
                        self.step_robot()
                elif action == Action.RS:
                    self.robot.direction = self.rotate_robot(Action.RS)
                elif action == Action.RD:
                    self.robot.direction = self.rotate_robot(Action.RD)
                elif action == Action.UPDATE_SONAR:
                    self.calc_robot_sonar()
                else:
                    raise Exception("azione non ammessa")
        else:
            pass # Do nothing

    def check_map_bounds(self, temp_x, temp_y):
        if temp_x < 1: temp_x = 1
        if temp_y < 1: temp_y = 1
        if temp_x > self.X_MAX - 1: temp_x = self.X_MAX
        if temp_y > self.Y_MAX - 1: temp_y = self.Y_MAX
        return temp_x, temp_y

    def peek_mappa(self, dx, dy):
        riga = self._Ry + dy
        colonna = self._Rx + dx
        colonna , riga = self.check_map_bounds(colonna, riga)
        return self.mappa[riga][colonna]

    def calc_robot_sonar(self):
        # Simula i valori dei sensori sonar del robot
        # Il robot guarda sempre a NORD
        if self.robot.direction == Direction.NORD:
            S = self.peek_mappa(-1, -1)
            C = self.peek_mappa( 0, -1)
            D = self.peek_mappa( 1, -1)
        elif self.robot.direction == Direction.EST:
            S = self.peek_mappa( 1, -1)
            C = self.peek_mappa( 1,  0)
            D = self.peek_mappa( 1,  1)
        elif self.robot.direction == Direction.SUD:
            S = self.peek_mappa( 1,  1)
            C = self.peek_mappa( 0,  1)
            D = self.peek_mappa(-1,  1)
        elif self.robot.direction == Direction.OVEST:
            S = self.peek_mappa(-1,  1)
            C = self.peek_mappa(-1,  0)
            D = self.peek_mappa(-1, -1)
        else:
            raise Exception("Wrong Direction")

        self.robot.misura_sensori([S, C, D])
        return [S, C, D]

    def init_map(self):
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

        if self.robot.direction == Direction.NORD:
            pygame.draw.rect(SCREEN, YELLOW, [(BLOCK_MARGIN + BLOCK_WIDTH) * (self._Rx - 1)  , (BLOCK_MARGIN + BLOCK_HEIGHT) * (self._Ry - 1), (BLOCK_WIDTH + BLOCK_MARGIN)* 3, BLOCK_HEIGHT], 1)
        elif self.robot.direction == Direction.EST:
            pygame.draw.rect(SCREEN, YELLOW, [(BLOCK_MARGIN + BLOCK_WIDTH) * (self._Rx + 1)  , (BLOCK_MARGIN + BLOCK_HEIGHT) * (self._Ry - 1), BLOCK_WIDTH, (BLOCK_HEIGHT + BLOCK_MARGIN)* 3], 1)
        elif self.robot.direction == Direction.SUD:
            pygame.draw.rect(SCREEN, YELLOW, [(BLOCK_MARGIN + BLOCK_WIDTH) * (self._Rx - 1)  , (BLOCK_MARGIN + BLOCK_HEIGHT) * (self._Ry + 1), (BLOCK_WIDTH + BLOCK_MARGIN)* 3, BLOCK_HEIGHT], 1)
        elif self.robot.direction == Direction.OVEST:
            pygame.draw.rect(SCREEN, YELLOW, [(BLOCK_MARGIN + BLOCK_WIDTH) * (self._Rx - 1)  , (BLOCK_MARGIN + BLOCK_HEIGHT) * (self._Ry - 1), BLOCK_WIDTH, (BLOCK_HEIGHT + BLOCK_MARGIN)* 3], 1)

    def print_text(self):
        self.init_map()

        stepCounter_text = FONT.render(f"STEP_COUNT: {self.step_counter}", 1, WHITE)
        SCREEN.blit(stepCounter_text, (5, 480))

        batteryColor = GREEN if self.robot.isRunning == True else RED
        battery_text = FONT.render(f"BATTERY: {self.robot.max_battery}", 1, batteryColor)
        SCREEN.blit(battery_text, (200, 480))

        lockedColor = RED if self.robot.isLocked == True else GREEN
        isLocked_text = FONT.render(f"isLocked: {self.robot.isLocked}", 1, lockedColor)
        SCREEN.blit(isLocked_text, (5, 450))

        goalColor = GREEN if self.goal_reached == True else RED
        goal_reached_text = FONT.render(f"GOAL_REACHED: {self.goal_reached}", 1, goalColor)
        SCREEN.blit(goal_reached_text, (200, 450))

        auto_text = FONT.render(f"AUTO_STEP_MODE: {AUTO_STEP}", 1, BLUE)
        SCREEN.blit(auto_text, (5, 420))

        pygame.display.flip()
        CLOCK.tick(SIM_TICK)

    def start(self):
        self.init_map()
        pygame.display.flip()
        run = True
        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    run = False
                elif AUTO_STEP == False and event.type == pygame.KEYDOWN:
                    SCREEN.fill(BLACK)
                    if self.robot.isRunning == True:
                        self.do_robot_action()
                    self.print_text()
            if AUTO_STEP == True:
                if self.goal_reached == False:
                    SCREEN.fill(BLACK)
                    if self.robot.isRunning == True:
                        self.do_robot_action()
                    self.print_text()
        pygame.quit()