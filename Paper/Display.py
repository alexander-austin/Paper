#  Copyright (c) 2024, Alexander Austin
#  All rights reserved.
#
#  This source code is licensed under the BSD-style license found in the
#  LICENSE file in the root directory of this source tree.


# Primarily derived from the manufacturer's repository:
# https://github.com/waveshareteam/e-Paper/blob/master/RaspberryPi_JetsonNano/python/lib/waveshare_epd/epd7in3f.py


#!/usr/bin/python3.12
# -*- coding: utf-8 -*-


from Paper.DB import DB
import time, sys


class Display:


    RST_PIN  = 17
    DC_PIN   = 25
    CS_PIN   = 8
    BUSY_PIN = 24
    PWR_PIN  = 18
    initSequence = [
        {
	        'type': 'command',
	        'data': 0xAA
        }, {
	        'type': 'data',
	        'data': 0x49
        }, {
	        'type': 'data',
	        'data': 0x55
        }, {
	        'type': 'data',
	        'data': 0x20
        }, {
	        'type': 'data',
	        'data': 0x08
        }, {
	        'type': 'data',
	        'data': 0x09
        }, {
	        'type': 'data',
	        'data': 0x18
        }, {
	        'type': 'command',
	        'data': 0x01
        }, {
	        'type': 'data',
	        'data': 0x3F
        }, {
	        'type': 'data',
	        'data': 0x00
        }, {
	        'type': 'data',
	        'data': 0x32
        }, {
	        'type': 'data',
	        'data': 0x2A
        }, {
	        'type': 'data',
	        'data': 0x0E
        }, {
	        'type': 'data',
	        'data': 0x2A
        }, {
	        'type': 'command',
	        'data': 0x00
        }, {
	        'type': 'data',
	        'data': 0x5F
        }, {
	        'type': 'data',
	        'data': 0x69
        }, {
	        'type': 'command',
	        'data': 0x03
        }, {
	        'type': 'data',
	        'data': 0x00
        }, {
	        'type': 'data',
	        'data': 0x54
        }, {
	        'type': 'data',
	        'data': 0x00
        }, {
	        'type': 'data',
	        'data': 0x44
        }, {
	        'type': 'command',
	        'data': 0x05
        }, {
	        'type': 'data',
	        'data': 0x40
        }, {
	        'type': 'data',
	        'data': 0x1F
        }, {
	        'type': 'data',
	        'data': 0x1F
        }, {
	        'type': 'data',
	        'data': 0x2C
        }, {
	        'type': 'command',
	        'data': 0x06
        }, {
	        'type': 'data',
	        'data': 0x6F
        }, {
	        'type': 'data',
	        'data': 0x1F
        }, {
	        'type': 'data',
	        'data': 0x1F
        }, {
	        'type': 'data',
	        'data': 0x22
        }, {
	        'type': 'command',
	        'data': 0x08
        }, {
	        'type': 'data',
	        'data': 0x6F
        }, {
	        'type': 'data',
	        'data': 0x1F
        }, {
	        'type': 'data',
	        'data': 0x1F
        }, {
	        'type': 'data',
	        'data': 0x22
        }, {
	        'type': 'command',
	        'data': 0x13
        }, {
	        'type': 'data',
	        'data': 0x00
        }, {
	        'type': 'data',
	        'data': 0x04
        }, {
	        'type': 'command',
	        'data': 0x30
        }, {
	        'type': 'data',
	        'data': 0x3C
        }, {
	        'type': 'command',
	        'data': 0x41
        }, {
	        'type': 'data',
	        'data': 0x00
        }, {
	        'type': 'command',
	        'data': 0x50
        }, {
	        'type': 'data',
	        'data': 0x3F
        }, {
	        'type': 'command',
	        'data': 0x60
        }, {
	        'type': 'data',
	        'data': 0x02
        }, {
	        'type': 'data',
	        'data': 0x00
        }, {
	        'type': 'command',
	        'data': 0x61
        }, {
	        'type': 'data',
	        'data': 0x03
        }, {
	        'type': 'data',
	        'data': 0x20
        }, {
	        'type': 'data',
	        'data': 0x01
        }, {
	        'type': 'data',
	        'data': 0xE0
        }, {
	        'type': 'command',
	        'data': 0x82
        }, {
	        'type': 'data',
	        'data': 0x1E
        }, {
	        'type': 'command',
	        'data': 0x84
        }, {
	        'type': 'data',
	        'data': 0x00
        }, {
	        'type': 'command',
	        'data': 0x86
        }, {
	        'type': 'data',
	        'data': 0x00
        }, {
	        'type': 'command',
	        'data': 0xE3
        }, {
	        'type': 'data',
	        'data': 0x2F
        }, {
	        'type': 'command',
	        'data': 0xE0
        }, {
	        'type': 'data',
	        'data': 0x00
        }, {
	        'type': 'command',
	        'data': 0xE6
        }, {
	        'type': 'data',
	        'data': 0x00
        }
    ]


    def __init__(self):
        """Initialize."""

        self.status = 'initializing'

        self.logFileKey = 'display_log'
        self.db = DB()


        try:

            import RPi.GPIO, spidev
            self.GPIO = RPi.GPIO
            self.SPI = spidev.SpiDev()

        except ImportError:

            from Paper.FakeIO import FakeGPIO, FakeSPI
            self.GPIO = FakeGPIO()
            self.SPI = FakeSPI()


        try:

            self.GPIO.setmode(self.GPIO.BCM)
            self.GPIO.setwarnings(False)
            self.GPIO.setup(self.RST_PIN, self.GPIO.OUT)
            self.GPIO.setup(self.DC_PIN, self.GPIO.OUT)
            self.GPIO.setup(self.CS_PIN, self.GPIO.OUT)
            self.GPIO.setup(self.PWR_PIN, self.GPIO.OUT)
            self.GPIO.setup(self.BUSY_PIN, self.GPIO.IN)
            self.GPIO.output(self.PWR_PIN, 1)

            self.SPI.open(0, 0)
            self.SPI.max_speed_hz = 4000000
            self.SPI.mode = 0b00


            self.reset()
            self.readWait()
            time.sleep(0.03)


            for item in self.initSequence:

                if item['type'] == 'command':

                    self.sendCommand(
                        item['data']
                    )

                elif item['type'] == 'data':

                    self.sendData(
                        item['data']
                    )

        except Exception as e:

            self.db.log(
                self.logFileKey,
                '.'.join(
                    [
                        str(self.__class__.__name__),
                        str(sys._getframe().f_code.co_name)
                    ]
                ),
                str(e)
            )

        self.status = 'available'


        return


    def displayBytes(self, buffered):
        """Display buffered image bytes."""

        try:

            self.sendCommand(0x10)
            self.sendData2(buffered)

            self.turnOn()

        except Exception as e:

            self.db.log(
                self.logFileKey,
                '.'.join(
                    [
                        str(self.__class__.__name__),
                        str(sys._getframe().f_code.co_name)
                    ]
                ),
                str(e)
            )


        return

    def turnOn(self):
        """Turn Display on."""

        try:

            self.sendCommand(0x04)
            self.readWait()

            self.sendCommand(0x12)
            self.sendData(0X00)
            self.readWait()

            self.sendCommand(0x02)
            self.sendData(0X00)
            self.readWait()

        except Exception as e:

            self.db.log(
                self.logFileKey,
                '.'.join(
                    [
                        str(self.__class__.__name__),
                        str(sys._getframe().f_code.co_name)
                    ]
                ),
                str(e)
            )


        return
    def sendCommand(self, command):
        """Send command to display."""

        try:

            self.GPIO.output(self.DC_PIN, 0)
            self.GPIO.output(self.CS_PIN, 0)
            self.SPI.writebytes([command])
            self.GPIO.output(self.CS_PIN, 1)

        except Exception as e:

            self.db.log(
                self.logFileKey,
                '.'.join(
                    [
                        str(self.__class__.__name__),
                        str(sys._getframe().f_code.co_name)
                    ]
                ),
                str(e)
            )


        return
    def sendData(self, data):
        """Send data to display."""

        try:

            self.GPIO.output(self.DC_PIN, 1)
            self.GPIO.output(self.CS_PIN, 0)
            self.SPI.writebytes([data])
            self.GPIO.output(self.CS_PIN, 1)

        except Exception as e:

            self.db.log(
                self.logFileKey,
                '.'.join(
                    [
                        str(self.__class__.__name__),
                        str(sys._getframe().f_code.co_name)
                    ]
                ),
                str(e)
            )


        return
    def sendData2(self, data):
        """Send bulk data to display."""

        try:

            self.GPIO.output(self.DC_PIN, 1)
            self.GPIO.output(self.CS_PIN, 0)
            self.SPI.writebytes2(data)
            self.GPIO.output(self.CS_PIN, 1)

        except Exception as e:

            self.db.log(
                self.logFileKey,
                '.'.join(
                    [
                        str(self.__class__.__name__),
                        str(sys._getframe().f_code.co_name)
                    ]
                ),
                str(e)
            )


        return
    def readWait(self):
        """Wait while display is busy."""

        try:

            while(self.GPIO.input(self.BUSY_PIN) == 0):

                time.sleep(0.005)

        except Exception as e:

            self.db.log(
                self.logFileKey,
                '.'.join(
                    [
                        str(self.__class__.__name__),
                        str(sys._getframe().f_code.co_name)
                    ]
                ),
                str(e)
            )


        return
    def reset(self):
        """Display hardware reset."""

        try:

            self.GPIO.output(self.RST_PIN, 1)
            time.sleep(0.02)
            self.GPIO.output(self.RST_PIN, 0)
            time.sleep(0.002)
            self.GPIO.output(self.RST_PIN, 1)
            time.sleep(0.02)

        except Exception as e:

            self.db.log(
                self.logFileKey,
                '.'.join(
                    [
                        str(self.__class__.__name__),
                        str(sys._getframe().f_code.co_name)
                    ]
                ),
                str(e)
            )


        return
