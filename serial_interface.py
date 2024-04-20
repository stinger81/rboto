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
import math
import serial
import threading

# Constant
JOY_SIZE = 1000 # what should one side be expanded to

class dummyInterface:
    def __init__(self):
        pass
    def send_data(self,**kwargs):
        print(kwargs)
    def send_stop(self):
        print("stop")
    def get_telemetry(self):
        return "TEL UNAVAILABLE THROUGH DUMMY INTERFACE"

class SerialInterface:
    """
    WARNING
    WARNING
    WARNING

    MODIFY THIS FILE AT YOUR OWN RISK
    CHANGING THIS FILE WILL DIRECTLY AFFECT HOW THE DATA SENT TO THE ARDUINO
    MAKE SURE THAT YOU UPGRADE THE ARDUINO CODE ACCORDINGLY
    """


    def __init__(self, port, baudrate):
        self.port = port
        self.baudrate = baudrate
        self.ser = serial.Serial(port=port,
                                 baudrate=baudrate,
                                 timeout=0.5)

        self.telemetry_buf = []
        self.message_buf = []

    def __del__(self):
        try:
            self.ser.close()
        except:
            pass

    def send_data(self, in_left_track_rate:float, in_right_track_rate:float, in_up_down_pos: float, in_gun_move:int, in_arm:int, in_fire:int):
        """
        Send the left and right track rates to the arduino
        :param in_right_track_rate: -1 to 1
        :param in_left_track_rate: -1 to 1
        :return: None
        """
        left_track_rate = self._pack_joy_data_255_int(in_left_track_rate)
        right_track_rate = self._pack_joy_data_255_int(in_right_track_rate)
        up_down_pos = str(in_up_down_pos + 255).zfill(4)
        gun_pos = str(in_gun_move + 255).zfill(4) # add 10 to the gun position to avoid sending 0
        arm = str(in_arm).zfill(4)
        fire = str(in_fire).zfill(4)

        # compile the data

        data = "D,"
        data += left_track_rate
        data += ","
        data += right_track_rate
        data += ","
        data += up_down_pos
        data += ","
        data += gun_pos # placeholder for stepper motor
        data += ","
        data += arm # placeholder for future use
        data += ","
        data += fire # placeholder for future use
        data += ","
        data += "3333" # placeholder for future use
        data += "\n"
        # print(data)
        self._write(data.encode("utf-8"))

    def send_stop(self):
        """
        Send the stop command to the arduino
        :return: None
        """
        data = "S\n"
        self._write(data.encode("utf-8"))

    def get_telemetry(self) -> str:
        data_out = "R\n"
        self._write(data_out.encode("utf-8"))
        # get data back
        return self._read()



    def _pack_joy_data(self, value):
        if value > 1:
            value = 1
        elif value < -1:
            value = -1
        # normalize between 0 and 2
        value += 1
        # convert to value between 0 and 2000
        value *= JOY_SIZE
        return str(int(value)).zfill(4)

    def _pack_joy_data_255_int(self, value):
        value *= 255
        if value > 255:
            value = 255
        elif value < -255:
            value = -255
        # normalize between 0 and max
        value += 255
        return str(int(value)).zfill(4)



    def _write(self, data):
        self.ser.write(data)

    def disp_incoming_thread(self):
        while True:
            print(self._read().decode().strip("\r\n"))
    def _read(self):
        data = self.ser.read_until(b'\n')
        # print(data)
        return data.decode().strip("\r\n")

    def close(self):
        self.ser.close()

if __name__ == "__main__":
    ser = SerialInterface("COM8", 9600)
    # ser.send_data(-1, 1)
    # # time.sleep(1)
    # while True:
    #     print(ser._read())

    # data sweep
    my_min = -1
    my_max = 1
    my_step = 0.1
    my_range = int((my_max - my_min)/my_step) + 1

    for i in range(my_range):
        print("SENT")
        my_val = my_min + (my_step *i)
        ser.send_data(my_val,my_val)
        time.sleep(0.1)
        print(ser._read().decode().strip("\r\n"))
    time.sleep(1)
    # ser.process_incoming()


    ser.close()
    print("done")