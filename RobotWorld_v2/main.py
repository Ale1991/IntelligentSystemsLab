"""
    Simulatore di un robot mobile in 2D
    su una griglia discreta con pareti invalicabili
    (labirinto)
    e oggetti energetici da raccogliere che ricaricano la
    batteria del robot per continuare a funzionare
"""

# NECESSARIA LA LIBRERIA "pygame" per funzionare (necessaria per il plot grafico)
# Win10: py -m pip install -U pygame --user
# Debian: sudo apt-get install python3-pygame

if __name__ == '__main__':
    from src.world import World
    from src.robotBrain import RobotBrain
    from src.robotBody import RobotBody
    from src.simulator import Simulator
else: 
    from .src.world import World
    from .src.robotBrain import RobotBrain
    from .src.robotBody import RobotBody
    from .src.simulator import Simulator

 

def main():
    rBrain = RobotBrain()
    rBrain.name = "RobotBrainThread"
    rBrain.start()

    rBody = RobotBody()
    rBody.name = "RobotBodyThread"
    rBody.start()

    world = World("mappa2.txt")
    world.name = "WorlThread"
    world.start()

    simulator = Simulator()
    simulator.name = "SimulatorThread"
    simulator.start()



# DEVO FINIRE DI FARE IL BUFFER NEL MONDO CHE VERRA RIEMPITO DAL SUBSCRIBER CHIAMATO CONSUMER
# DOPODICHE' VA RIALLACCIATO IL PLOT E LO STEPPER DEL MONDO CON IL BUFFER

if __name__ == '__main__':
    main()