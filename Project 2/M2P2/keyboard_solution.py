#!/usr/bin/env python3

"""
GoPiGo3 for the Raspberry Pi: an open source robotics platform for the Raspberry Pi.
Copyright (C) 2019 Dexter Industries and Georgia State University

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/gpl-3.0.txt>.
"""

import GSUbot
import random
import threading
import time
import signal
import traceback
import curtsies

class KeyboardBot(object):
    """
    Class for controlling the GSUbot in a CLI
    by mapping keystrokes to robot commands
    """

    KEY_DESCRIPTION = 0
    KEY_FUNC_SUFFIX = 1

    def __init__(self):
        """
        Instantiates the key-bindings between the GoPiGo3 and the keyboard's keys.
        Sets the order of the keys in the menu.
        """
        self.robot = GSUbot.Robot()
        self.pattern = re.compile('[\W_]+')

    def keystroke( self, stroke ):
        """
        Stroke is the key identifier returned by curtsies
        For instance: if argument is "w", then the algorithm looks for the "keystroke_w" method
        """
        method_name = "keystroke_" + self.pattern.sub( "", stroke.printable )
        method = getattr(self, method_name, lambda : print( "Missing method "+method_name ) )
        return method() if method

    def drawLogo(self):
        """
        Draws the name of the GoPiGo3.
        """
        print("   _____       _____ _  _____         ____  ")
        print("  / ____|     |  __ (_)/ ____|       |___ \ ")
        print(" | |  __  ___ | |__) || |  __  ___     __) |")
        print(" | | |_ |/ _ \|  ___/ | | |_ |/ _ \   |__ < ")
        print(" | |__| | (_) | |   | | |__| | (_) |  ___) |")
        print("  \_____|\___/|_|   |_|\_____|\___/  |____/ ")
        print("                                            ")

    def drawDescription(self):
        print( "\n" + self.description() )

    def drawMenu(self):
        """
        Prints all the key-bindings between the keys and the GoPiGo3's commands on the screen.
        """
        try:
            for key in self.menu_order():
                print( "\r{:7} - {}".format( key, self.menu_descriptions()[key] ) )

    def description(self): return "Press the following keys for moving/orientating the robot by the 4 cardinal points"
    def menu_order(self): return [ "LEFT", "RIGHT", "UP", "DOWN", "w", "SPACE", "ESC" ]
    def menu_descriptions(self): return {
        "LEFT"  : "Face West",
        "RIGHT" : "Face East",
        "UP"    : "Face North",
        "DOWN"  : "Face South",
        "w"     : "Move",
        "SPACE" : "Stop",
        "ESC"   : "Exit",
        "q"     : "Quit",
        "SigIntEvent" : "Interrupt",
    }

    def keystroke_LEFT(       self): self.robot.spin( heading = -90 )
    def keystroke_RIGHT(      self): self.robot.spin( heading =  90 )
    def keystroke_UP(         self): self.robot.spin( heading =   0 )
    def keystroke_DOWN(       self): self.robot.spin( heading = 180 )
    def keystroke_w(          self): self.robot.forward()
    def keystroke_SPACE(      self): self.robot.stop()
    def keystroke_ESC(        self): self.interrupt.set()
    def keystroke_q(          self): self.interrupt.set()
    def keystroke_SigIntEvent(self): self.interrupt.set()

    def Main( self, interrupt=None ):

        if interrupt is None:
            interrupt = threading.Event()
            signal.signal( signal.SIGTSTP, lambda signal_id, stack_frame : ( print( "SIGSTP - interrupting KeyboardBot" ), interrupt.set() ) )  ## Handle Ctrl+Z
        self.interrupt = interrupt

        self.drawLogo() # draws the GoPiGo3 logo
        self.drawDescription() # writes some description on the GoPiGo3
        self.drawMenu() # writes the menu for controlling the GoPiGo3 robot

        refresh_rate = 20.0
        with curtsies.Input(keynames = "curtsies", sigint_event = True) as input_generator:
            while not interrupt.is_set():
                period = 1 / refresh_rate
                # if nothing is captured in [period] seconds
                # then send() function returns None
                key = input_generator.send(period)

                # if we've captured something from the keyboard
                if key is not None:
                    result = self.executeKeyboardJob(key)

if __name__ == "__main__":
    try:
        KeyboardBot().Main()
    except Exception as error:
        print( "Exception! -- ", traceback.format_exc() )
        exit(1)
    print( "Exiting" )
    exit(0)
