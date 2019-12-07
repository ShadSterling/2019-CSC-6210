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

class KeyboardCommands(object):
    """
    Class for interfacing with the GoPiGo3.
    It's functionality is to map different keys
    of the keyboard to different commands of the GoPiGo3.
    """

    KEY_DESCRIPTION = 0
    KEY_FUNC_SUFFIX = 1

    def __init__(self):
        """
        Instantiates the key-bindings between the GoPiGo3 and the keyboard's keys.
        Sets the order of the keys in the menu.
        """
        self.robot = GSUbot.Robot()

        self.keybindings = {
            "<LEFT>"  : [ "Face West",  "west"  ],
            "<RIGHT>" : [ "Face East",  "east"  ],
            "<UP>"    : [ "Face North", "north" ],
            "<DOWN>"  : [ "Face South", "south" ],
            "w"       : [ "Move",       "move"  ],
            "<SPACE>" : [ "Stop",       "stop"  ],
            "<ESC>"   : [ "Exit",       "exit"  ],
            "q"       : [ "Quit",       "exit"  ],
            "<SigInt Event>" : [ "Interrupt", "exit" ],
        }
        self.order_of_keys = [ "<LEFT>", "<RIGHT>", "<UP>", "<DOWN>", "w", "<SPACE>", "<ESC>" ]

    def executeKeyboardJob(self, argument):
        """
        Argument is the key identifier returned by curtsies

        For instance: if argument is "w", then the algorithm looks inside self.keybinds dict and finds
        the "forward" value, which in turn calls the "_gopigo3_command_forward" method
        for driving the gopigo3 forward.
        """

        method_prefix = "_gopigo3_command_"
        try: method_suffix = str(self.keybindings[str(argument)][self.KEY_FUNC_SUFFIX])
        except KeyError: method_suffix = "binding_"+str(argument)
        method_name = method_prefix + method_suffix

        method = getattr(self, method_name, lambda : print( "Missing method "+method_name ) )

        return method()

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
        print("\nPress the following keys for moving/orientating the robot by the 4 cardinal points")

    def drawMenu(self):
        """
        Prints all the key-bindings between the keys and the GoPiGo3's commands on the screen.
        """
        try:
            for key in self.order_of_keys:
                print("\r{:7} - {}".format(key, self.keybindings[key][self.KEY_DESCRIPTION]))
        except KeyError:
            print("Error: Keys found GoPiGo3WithKeyboard.order_of_keys don't match with those in GoPiGo3WithKeyboard.keybindings.")

    def _gopigo3_command_west( self): self.robot.spin( heading = -90 )
    def _gopigo3_command_east( self): self.robot.spin( heading =  90 )
    def _gopigo3_command_north(self): self.robot.spin( heading =   0 )
    def _gopigo3_command_south(self): self.robot.spin( heading = 180 )
    def _gopigo3_command_move( self): self.robot.forward()
    def _gopigo3_command_stop( self): self.robot.stop()
    def _gopigo3_command_exit( self): interrupt.set()

    def Main( self, interrupt ):
        self.drawLogo() # draws the GoPiGo3 logo
        self.drawDescription() # writes some description on the GoPiGo3
        self.drawMenu() # writes the menu for controlling the GoPiGo3 robot

        # result holds the exit string when we call a gopigo3 command
        # with the GoPiGo3WithKeyboard object
        result = "nothing"
        successful_exit = True
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
    interrupt = threading.Event()

    signal.signal( signal.SIGTSTP, lambda signal_id, stack_frame : interrupt.set() )  ## Handle Ctrl+Z

    try:
        KeyboardCommands().Main( interrupt )
    except Exception as error:
        print( "Exception! -- ", traceback.format_exc() )
        exit(1)
    print( "Exiting" )
    exit(0)
