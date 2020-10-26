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
    from src.robot import Robot
else: 
    from .src.world import World
    from .src.robot import Robot
 

def main():
    # Inizializzo la mappa 
    mondo = World("mappa1.txt")

    #inserisco il robot nel mondo
    mondo.insert_robot(Robot())

    # Inizio simulazione
    mondo.start()

if __name__ == '__main__':
    main()