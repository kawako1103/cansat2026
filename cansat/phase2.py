from tegusu import tegusu
from Motor import robot
import time


def phase2():
    tegusu.cutWire()
    time.sleep(3)

    ##GPIO setup
    robot.initialize()
    ##

    robot.move(0.5, 6)
    robot.stop()