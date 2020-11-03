""""
    Embed a SWI Prolog Interpreter and ask to it were to go
    given my current sensor readings.
"""

from pyswip import Prolog
from src.mapelement import MapElement

if __name__== "__main__":
    prolog = Prolog()
    prolog.consult("robot_swi.pl")

    # read sensor value from redis
    leftValue = "W"
    forwardValue = "W"
    rightValue = "R"
    # pass them to prolog script
    prolog.assertz(f'sensor_Left("{leftValue}")')
    prolog.assertz(f'sensor_Forward("{forwardValue}")')
    prolog.assertz(f'sensor_Right("{rightValue}")')
    prolog.assertz("stucked(1)")
    query = "move(X)."# move(X).
    res = prolog.query(query)
    for solution in res:
        print("direction: ", solution["X"])