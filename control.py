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
import xbox_control
import time
import keyboard_control
import serial_interface

CONTROL_MODE = "xbox"  # xbox or keyboard
ENABLE_SERIAL = True
UPDATE_FREQUENCY = 10000  # Hz
COMM_PORT = "COM13"
GUN_STEPS_PER_PACKET = 10
UPDOWN_STEPS_PER_PACKET = 30


class control:
    def __init__(self):
        if ENABLE_SERIAL:

            self.ser = serial_interface.SerialInterface(COMM_PORT, 115200)
        else:
            self.ser = serial_interface.dummyInterface()
        if CONTROL_MODE == "xbox":
            self.control = xbox_control.XboxController()
        else:
            self.control = keyboard_control.control()
        self.drive_mode = "tank"  # tank or tank_pivot
        self.mode_set = time.time()

        self.right_tank_rate = 0
        self.left_tank_rate = 0
        self.gun_move = 0
        self.arm_val = 0
        self.fire_val = 0

    def interupt(self):
        name = input("Enter your name: ")

    def process(self):

        print(self.ser.get_telemetry())
        # print(self.ser.get_message())
        if self.control.A == 1 and self.control.B == 1:
            self.ser.send_stop()
        elif self.control.X == 1:
            if time.time() - self.mode_set > 1:  # 1 seconds delay required between mode changes
                if self.drive_mode == "tank":
                    self.drive_mode = "tank_pivot"
                    print("Tank Pivot Mode")
                elif self.drive_mode == "tank_pivot":
                    self.drive_mode = "tank"
                    print("Tank Mode")
                self.mode_set = time.time()
        elif self.control.B == 1:  # stop
            self.stop()
        elif self.control.RightBumper == 1 and self.control.LeftBumper == 1:
            self.gun_move = 0
        elif self.control.RightBumper == 1:
            self.gun_move = GUN_STEPS_PER_PACKET
        elif self.control.LeftBumper == 1:
            self.gun_move = -GUN_STEPS_PER_PACKET
        elif self.control.LeftTrigger > 0.75:
            self.arm()
        elif self.control.RightTrigger > 0.75:
            self.fire()
        else:
            if self.drive_mode == "tank":
                self.left_tank_rate, self.right_tank_rate = self.tank_drive()
            elif self.drive_mode == "tank_pivot":
                self.left_tank_rate, self.right_tank_rate = self.tank_pivot_drive()

        # print(self.control.LeftBumper)


        # handel serial output to robot
        self.ser.send_data(in_left_track_rate=self.left_tank_rate,
                           in_right_track_rate=self.right_tank_rate,
                           in_up_down_pos=self.up_down(),
                           in_gun_move=self.gun_move,
                           in_arm=self.arm_val,
                           in_fire=self.fire_val)

        self.gun_move = 0
        self.arm_val = 0
        self.fire_val = 0

    def stop(self):
        self.ser.send_stop()  # all movement on rboto is stopped
        self.control.stop()  # Halt control input for a set amount of time

    # def launch_ball(self):

    ############################################################################################################
    # region tank drive
    def tank_drive(self):
        # todo, double check math for turning in reverse
        x, y = self.control.get_Lstick()

        left = y
        if x > 0:
            left += x  # turning right
        right = y
        if x < 0:
            right -= x  # turning left (-= since it will receive a negative value)

        my_max = max(abs(left), abs(right))
        if my_max > 1:
            left /= my_max
            right /= my_max
        return -left, -right

    def tank_pivot_drive(self):
        x, y = self.control.get_Lstick()
        right = -x
        left = x
        return -left, -right

    def up_down(self):
        if self.control.UpDPad == 1:
            y = UPDOWN_STEPS_PER_PACKET
        elif self.control.DownDPad == 1:
            y = -UPDOWN_STEPS_PER_PACKET
        else:
            y = 0
        return y
    def arm(self):
        self.arm_val = 1

    def fire(self):
        self.fire_val = 1

    # endregion
    ############################################################################################################


def main():
    c = control()
    while True:
        start = time.time()
        c.process()
        end = time.time()
        # if end - start < 1 / UPDATE_FREQUENCY:
        #     time.sleep(1 / UPDATE_FREQUENCY - (end - start))


if __name__ == '__main__':
    main()
