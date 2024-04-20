# /bin/python3
# ##########################################################################
#
#   Copyright (C) 2024 Michael Dompke (https://github.com/stinger81)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#   Michael Dompke (https://github.com/stinger81)
#   michael@dompke.dev
#
# ##########################################################################

import time
import keyboard
import threading

STOP_DELAY = 1.0
class control:
    def __init__(self):
        self.stop_time = 0

        self.LeftJoystickY = 0
        self.LeftJoystickX = 0
        self.RightJoystickY = 0
        self.RightJoystickX = 0
        self.LeftTrigger = 0
        self.RightTrigger = 0
        self.LeftBumper = 0
        self.RightBumper = 0
        self.A = 0
        self.X = 0
        self.Y = 0
        self.B = 0
        self.LeftThumb = 0
        self.RightThumb = 0
        self.Back = 0
        self.Start = 0
        self.LeftDPad = 0
        self.RightDPad = 0
        self.UpDPad = 0
        self.DownDPad = 0

        self._monitor_thread = threading.Thread(target=self._monitor_controller, args=())
        self._monitor_thread.daemon = True
        self._monitor_thread.start()

    def stop(self):
        self.stop_time = time.time()

    def disp_read(self): # return the buttons/triggers that you care about in this methode
        print("LeftJoystickY: ", self.LeftJoystickY)
        print("LeftJoystickX: ", self.LeftJoystickX)
        print("RightJoystickY: ", self.RightJoystickY)
        print("RightJoystickX: ", self.RightJoystickX)


    def get_Lstick(self, renormalize = False):
        if time.time() - self.stop_time < STOP_DELAY:
            return [0, 0]
        else:
            return [self.LeftJoystickX, self.LeftJoystickY]


    def get_Rstick(self, renormalize = False):
        if time.time() - self.stop_time < STOP_DELAY:
            return [0, 0]
        else:
            return [self.RightJoystickX, self.RightJoystickY]

    def _monitor_controller(self):
        while True:
            # wasd for left stick
            if keyboard.is_pressed('w'):
                self.LeftJoystickY = 1
            elif keyboard.is_pressed('s'):
                self.LeftJoystickY = -1
            else:
                self.LeftJoystickY = 0

            if keyboard.is_pressed('a'):
                self.LeftJoystickX = -1
            elif keyboard.is_pressed('d'):
                self.LeftJoystickX = 1
            else:
                self.LeftJoystickX = 0

            # arrow keys for right stick
            if keyboard.is_pressed('up'):
                self.RightJoystickY = 1
            elif keyboard.is_pressed('down'):
                self.RightJoystickY = -1
            else:
                self.RightJoystickY = 0

            if keyboard.is_pressed('left'):
                self.RightJoystickX = -1
            elif keyboard.is_pressed('right'):
                self.RightJoystickX = 1
            else:
                self.RightJoystickX = 0

            # buttons
            # A is not here because it used for steering use z instead

            if keyboard.is_pressed('z'):
                self.A = 1
            else:
                self.A = 0

            if keyboard.is_pressed('x'):
                self.X = 1
            else:
                self.X = 0

            if keyboard.is_pressed('y'):
                self.Y = 1
            else:
                self.Y = 0

            if keyboard.is_pressed('b'):
                self.B = 1
            else:
                self.B = 0



if __name__ == "__main__":
    c = control()
    while True:
        c.disp_read()
        time.sleep(1)

