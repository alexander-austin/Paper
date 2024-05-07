#  Copyright (c) 2024, Alexander Austin
#  All rights reserved.
#
#  This source code is licensed under the BSD-style license found in the
#  LICENSE file in the root directory of this source tree.


#!/usr/bin/python3.12
# -*- coding: utf-8 -*-


# Accesses MPU6050 data
# Modified from https://www.electronicwings.com/raspberry-pi/mpu6050-accelerometergyroscope-interfacing-with-raspberry-pi
# as well as https://engineering.stackexchange.com/questions/3348/calculating-pitch-yaw-and-roll-from-mag-acc-and-gyro-data
# sudo raspi-config nonint do_i2c 0


import math
from smbus2 import SMBus


class Mpu6050:


    address = 0x68
    registers = {
        'rate_sample': 0x19,
        'power_management': 0x6B,
        'config': 0x1A,
        'interrupt_state': 0x38,
        'accelerometer': {
            'x': 0x3B,
            'y': 0x3D,
            'z': 0x3F
        },
        'gyro': {
            'config': 0x1B,
            'x': 0x43,
            'y': 0x45,
            'z': 0x47
        }
    }
    smoothing = 10


    def __init__(self):
        """Initialize."""

        self.device = SMBus(1)

        self.write(self.registers['rate_sample'], 7)
        self.write(self.registers['power_management'], 1)
        self.write(self.registers['config'], 1)
        self.write(self.registers['gyro']['config'], 24)
        self.write(self.registers['interrupt_state'], 1)


        return


    def getValues(self):
        """Get current values."""

        values = {
            'accelerometer': {
                'x': 0.0,
                'y': 0.0,
                'z': 0.0
            },
            'gyro': {
                'x': 0.0,
                'y': 0.0,
                'z': 0.0
            }
        }

        for n in range(self.smoothing):

            for d in ['x', 'y', 'z']:

                values['accelerometer'][d] += self.read(self.registers['accelerometer'][d]) / 16384.0
                values['gyro'][d] += self.read(self.registers['gyro'][d]) / 131.0

        values['gyro']['y'] *= -1.0

        for t in ['accelerometer', 'gyro']:

            for d in ['x', 'y', 'z']:

                values[t][d] = values[t][d] / self.smoothing

        values['pitch'] = 180.0 * math.atan(values['accelerometer']['x'] / math.sqrt(math.pow(values['accelerometer']['y'], 2) + math.pow(values['accelerometer']['z'], 2))) / math.pi
        values['roll'] = 180.0 * math.atan(values['accelerometer']['y'] / math.sqrt(math.pow(values['accelerometer']['x'], 2) + math.pow(values['accelerometer']['z'], 2))) / math.pi
        values['yaw'] = 180.0 * math.atan(values['accelerometer']['z'] / math.sqrt(math.pow(values['accelerometer']['x'], 2) + math.pow(values['accelerometer']['z'], 2))) / math.pi


        return values


    def read(self, register):
        """Reads raw data from device bus."""

        hi = self.device.read_byte_data(self.address, register)
        lo = self.device.read_byte_data(self.address, register + 1)

        value = ((hi << 8) | lo) if ((hi << 8) | lo) <= 32768 else (((hi << 8) | lo) - 65536)


        return value
    def write(self, register, value):
        """Writes to device bus."""

        self.device.write_byte_data(self.address, register, value)


        return
