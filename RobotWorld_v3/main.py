"""
    Simulatore di un robot mobile in 2D
    su una griglia discreta con pareti invalicabili
    (labirinto)
    e oggetti energetici da raccogliere che ricaricano la
    batteria del robot per continuare a funzionare

    UPDATE:
    -Wrold: SENSE ->invia il risultato dei sensori sul canale WORLD-BODY
                    ->invia i parametri del mondo da stampare al Simulator sul canale SIMULATOR
    -RobotBrain: PLAN -> invia il risultato decisionale sul canale BRAIN-BODY
    -RobotBody: ACT -> invia le request per i sensori sul canale WORLD-BODY
                    -> invia i propri parametri al brain sul canale BRAIN-BODY
    -Simulator: PLOT-> riceve i dati del mondo da stampare sul canale SIMULATOR

    tutti i canali di comunicazione sono stati implementati attraverso redis
    le 4 classi sono state implementate attraverso l'utilizzo di Thread
    ogni classe instanzia i rispettivi listener per i canali attraverso altri Thread
    le race condition tra body e brain sono state evitate attraverso l'ausilio di due flag e Action.UPDATE-SENSOR come trigger di request dati

    ENCODE-DECODE attraverso json: ricostruzione di object custom attraverso EnumEncode in ./utility.py
    
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

 # prova git

def main():
    rBrain = RobotBrain()
    rBrain.name = "RobotBrainThread"
    rBrain.start()

    rBody = RobotBody()
    rBody.name = "RobotBodyThread"
    rBody.start()

    world = World("mappa1.txt")
    world.name = "WorldThread"
    world.start()

    simulator = Simulator()
    simulator.name = "SimulatorThread"
    simulator.start()


# TODO miss implementation for plot goal, battery, number_of_steps and stop brain when out of battery

if __name__ == '__main__':
    main()