#!/usr/bin/env python3

# This example shows how to read values from the Distance Sensor

import GSUbot
import signal

robot = GSUbot.Robot()

loop = True
def stop():
    global loop
    loop = False
signal.signal( signal.SIGINT, lambda signal_id, stack_frame : stop() )  ##  Handle ctrl+c

while loop:
    print( "Distance Sensor Reading: {} mm ".format(robot.distance.mm) )
