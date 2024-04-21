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

from inputs import get_gamepad
import math
import threading

JOY_MIN_THRESH = 0.2
JOY_RENORMALIZE = True

STOP_DELAY = 1  # seconds, if the stop command is executed here it will


# ignore all joy stick input for the set amount of time
# all other buttons will still work
# step time to 0 to disable this feature



class XboxController(object):
    MAX_TRIG_VAL = math.pow(2, 8)
    MAX_JOY_VAL = math.pow(2, 15)

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

    def disp_read(self):  # return the buttons/triggers that you care about in this methode

        l_stick = self.get_Lstick()
        a = self.A
        b = self.B
        x = self.X
        y = self.Y
        return [l_stick[0], l_stick[1], a, b, x, y, self.RightTrigger, self.UpDPad, self.DownDPad, self.LeftTrigger, self.RightTrigger]

    def get_Lstick(self, MAG = None):
        output = [self.LeftJoystickX, self.LeftJoystickY]
        if time.time() - self.stop_time < STOP_DELAY:
            return [0, 0]
        elif MAG is not None:
            return self._normalize_joy_to_mag(output, MAG)
        elif JOY_RENORMALIZE:
            return self._renormalize_joy(output)
        else:
            return self._reset_w_joy_limits(output)

    def get_Rstick(self, MAG = None):
        output = [self.RightJoystickX, self.RightJoystickY]
        if time.time() - self.stop_time < STOP_DELAY:
            return [0, 0]
        elif MAG is not None:
            return self._normalize_joy_to_mag(output, MAG)
        elif JOY_RENORMALIZE:
            return self._renormalize_joy(output)
        else:
            return self._reset_w_joy_limits(output)

    def _reset_w_joy_limits(self, values):
        """
        Reset the joystick values to 0 if they are less than the threshold
        :param values:
        :return:
        """
        return [0 if abs(x) < JOY_MIN_THRESH else x for x in values]

    def _renormalize_joy(self, values):
        """
        Renormalize the joystick values to be between -1 and 1
        if values are less than the threshold 0 is returned.2
        values greater than the threshold are renormalized to be between 0 and 1
        if threshold is 0.5 and 0.6 is the value, the new value will be 0.2
        :param values:
        :return:
        """
        values = self._reset_w_joy_limits(values)
        for i in range(len(values)):
            if values[i] == 0:
                continue
            elif values[i] > 0:
                values[i] = (values[i] - JOY_MIN_THRESH) / (1 - JOY_MIN_THRESH)
            else:
                values[i] = (values[i] + JOY_MIN_THRESH) / (1 - JOY_MIN_THRESH)
        # print(values)
        return values

    def _normalize_joy_to_mag(self, values, mag):
        """
        Normalize the joystick values to be between -mag and mag
        :param values:
        :param mag:
        :return:
        """
        for i in range(len(values)):
            values[i] *= mag
        return values

    def _monitor_controller(self):
        while True:

            events = get_gamepad()
            for event in events:
                # print(event.code)
                if event.code == 'ABS_Y':
                    self.LeftJoystickY = event.state / XboxController.MAX_JOY_VAL
                elif event.code == 'ABS_X':
                    self.LeftJoystickX = event.state / XboxController.MAX_JOY_VAL  # normalize between -1 and 1
                elif event.code == 'ABS_RY':
                    self.RightJoystickY = event.state / XboxController.MAX_JOY_VAL  # normalize between -1 and 1
                elif event.code == 'ABS_RX':
                    self.RightJoystickX = event.state / XboxController.MAX_JOY_VAL  # normalize between -1 and 1
                elif event.code == 'ABS_Z':
                    self.LeftTrigger = event.state / XboxController.MAX_TRIG_VAL  # normalize between 0 and 1
                elif event.code == 'ABS_RZ':
                    self.RightTrigger = event.state / XboxController.MAX_TRIG_VAL  # normalize between 0 and 1
                elif event.code == 'BTN_TL':
                    self.LeftBumper = event.state
                elif event.code == 'BTN_TR':
                    self.RightBumper = event.state
                elif event.code == 'BTN_SOUTH':
                    self.A = event.state
                elif event.code == 'BTN_NORTH':
                    self.Y = event.state  # previously switched with X
                elif event.code == 'BTN_WEST':
                    self.X = event.state  # previously switched with Y
                elif event.code == 'BTN_EAST':
                    self.B = event.state
                elif event.code == 'BTN_THUMBL':
                    self.LeftThumb = event.state
                elif event.code == 'BTN_THUMBR':
                    self.RightThumb = event.state
                elif event.code == 'BTN_SELECT':
                    self.Back = event.state
                elif event.code == 'BTN_START':
                    self.Start = event.state
                elif event.code == 'ABS_HAT0X':
                    if event.state == 1:
                        self.RightDPad = 1
                        self.LeftDPad = 0
                    elif event.state == -1:
                        self.LeftDPad = 1
                        self.RightDPad = 0
                    else:
                        self.RightDPad = 0
                        self.LeftDPad = 0
                elif event.code == 'ABS_HAT0Y':
                    if event.state == 1:
                        self.DownDPad = 1
                        self.UpDPad = 0
                    elif event.state == -1:
                        self.UpDPad = 1
                        self.DownDPad = 0
                    else:
                        self.UpDPad = 0
                        self.DownDPad = 0
                # elif event.code == 'BTN_TRIGGER_HAPPY1':
                #     self.LeftDPad = event.state
                # elif event.code == 'BTN_TRIGGER_HAPPY2':
                #     self.RightDPad = event.state
                # elif event.code == 'BTN_TRIGGER_HAPPY3':
                #     self.UpDPad = event.state
                # elif event.code == 'BTN_TRIGGER_HAPPY4':
                #     self.DownDPad = event.state


if __name__ == '__main__':
    joy = XboxController()
    while True:
        print(joy.disp_read())
        # pass
