#  Copyright (c) 2024, Alexander Austin
#  All rights reserved.
#
#  This source code is licensed under the BSD-style license found in the
#  LICENSE file in the root directory of this source tree.


# Monitors and forwards GPIO input events


#!/usr/bin/python3.12
# -*- coding: utf-8 -*-


import datetime, os, sys, time
from ApiAgent import ApiAgent
from Mpu6050 import Mpu6050


class Pencil(ApiAgent):


    pins = {
        'GPIO_02': {
            'type': 'reserved', # Mpu6050
            'gpio': 2,
            'pin': 3,
            'actions': None
        },
        'GPIO_03': {
            'type': 'reserved', # Mpu6050
            'gpio': 3,
            'pin': 5,
            'actions': None
        },
        'GPIO_04': {
            'type': 'input',
            'gpio': 4,
            'pin': 7,
            'actions': {
                'short': {
					'type': 'previous'
				},
                'long': {
					'type': 'none'
				},
                'long_combo': {
					'type': 'reboot',
                    'combo_pins': [
                        'GPIO_04',
                        'GPIO_26'
                    ]
				}
            }
        },
        'GPIO_17': {
            'type': 'reserved', # e-Paper SPI
            'gpio': 17,
            'pin': 11,
            'actions': None
        },
        'GPIO_27': {
            'type': 'available',
            'gpio': 27,
            'pin': 13,
            'actions': None
        },
        'GPIO_22': {
            'type': 'available',
            'gpio': 22,
            'pin': 15,
            'actions': None
        },
        'GPIO_10': {
            'type': 'reserved', # e-Paper SPI
            'gpio': 10,
            'pin': 19,
            'actions': None
        },
        'GPIO_09': {
            'type': 'available',
            'gpio': 9,
            'pin': 21,
            'actions': None
        },
        'GPIO_11': {
            'type': 'reserved', # e-Paper SPI
            'gpio': 11,
            'pin': 23,
            'actions': None
        },
        'GPIO_05': {
            'type': 'available',
            'gpio': 5,
            'pin': 29,
            'actions': None
        },
        'GPIO_06': {
            'type': 'available',
            'gpio': 6,
            'pin': 31,
            'actions': None
        },
        'GPIO_13': {
            'type': 'available',
            'gpio': 13,
            'pin': 33,
            'actions': None
        },
        'GPIO_19': {
            'type': 'available',
            'gpio': 19,
            'pin': 35,
            'actions': None
        },
        'GPIO_26': {
            'type': 'input',
            'gpio': 26,
            'pin': 37,
            'actions': {
                'short': {
					'type': 'next'
				},
                'long': {
					'type': 'pause_toggle'
				},
                'long_combo': {
					'type': 'reboot',
                    'combo_pins': [
                        'GPIO_04',
                        'GPIO_26'
                    ]
				}
            }
        },
        
        'GPIO_14': {
            'type': 'available',
            'gpio': 14,
            'pin': 8,
            'actions': None
        },
        'GPIO_15': {
            'type': 'available',
            'gpio': 15,
            'pin': 10,
            'actions': None
        },
        'GPIO_18': {
            'type': 'available',
            'gpio': 18,
            'pin': 12,
            'actions': None
        },
        'GPIO_23': {
            'type': 'available',
            'gpio': 23,
            'pin': 16,
            'actions': None
        },
        'GPIO_24': {
            'type': 'reserved', # e-Paper SPI
            'gpio': 24,
            'pin': 18,
            'actions': None
        },
        'GPIO_25': {
            'type': 'reserved', # e-Paper SPI
            'gpio': 25,
            'pin': 22,
            'actions': None
        },
        'GPIO_08': {
            'type': 'reserved', # e-Paper SPI
            'gpio': 8,
            'pin': 24,
            'actions': None
        },
        'GPIO_07': {
            'type': 'available',
            'gpio': 7,
            'pin': 26,
            'actions': None
        },
        'GPIO_15': {
            'type': 'available',
            'gpio': 15,
            'pin': 10,
            'actions': None
        },
        'GPIO_12': {
            'type': 'available',
            'gpio': 12,
            'pin': 32,
            'actions': None
        },
        'GPIO_16': {
            'type': 'available',
            'gpio': 16,
            'pin': 36,
            'actions': None
        },
        'GPIO_20': {
            'type': 'available',
            'gpio': 20,
            'pin': 38,
            'actions': None
        },
        'GPIO_21': {
            'type': 'available',
            'gpio': 21,
            'pin': 40,
            'actions': None
        }
    }


    def __init__(self):
        """Initialize."""

        self.settings = {
            'init_delay': 3.0,
            'loop_delay': 0.1,
            'server_wait_delay': 3.0,
            'long_press_delay': 3.0,
            'action_throttle': 0.5,
            'last_loop': 0.0
        }

        self.apiAuthenticate()

        self.initMpu6050()
        self.initGpio()

        self.loop()


        return
    def initMpu6050(self):
        """Initialize MPU 6050."""

        self.log(
            '.'.join(
                [
                    str(self.__class__.__name__),
                    str(sys._getframe().f_code.co_name)
                ]
            ),
            'Initializing MPU 6050.'
        )

        for mpuAttr in ['mpu6050', 'mpu6050State']:

            if hasattr(self, mpuAttr):

                delattr(self, mpuAttr)


        try:

            mpu6050 = Mpu6050()
            self.mpu6050 = mpu6050
            self.mpu6050State = {
                'orientation': None,
                'error_threshold': 5,
                'error_count': 0
            }

            self.sendRequest(
                method='POST',
                endpoint='/api/settings/image',
                data={
                    'orientation_control': 'auto',
                    'orientation_auto_control_available': True
                },
                appendToken=True,
                returnJson=False,
                timeout=3.0,
                logError=True
            )

            self.log(
                '.'.join(
                    [
                        str(self.__class__.__name__),
                        str(sys._getframe().f_code.co_name)
                    ]
                ),
                'MPU 6050 initialized.'
            )

        except Exception as e:

            self.log(
                '.'.join(
                    [
                        str(self.__class__.__name__),
                        str(sys._getframe().f_code.co_name)
                    ]
                ),
                ' '.join(
                    [
                        'Failed to initialize MPU 6050.',
                        str(e)
                    ]
                )
            )


        return
    def initGpio(self):
        """Initialize hardware inputs/outputs."""

        self.log(
            '.'.join(
                [
                    str(self.__class__.__name__),
                    str(sys._getframe().f_code.co_name)
                ]
            ),
            'Initializing GPIO.'
        )

        # Imports
        try:

            import RPi.GPIO
            self.GPIO = RPi.GPIO

        except ImportError:

            from Paper.FakeIO import FakeGPIO
            self.GPIO = FakeGPIO()


        # Initialize
        try:

            self.GPIO.setmode(self.GPIO.BCM)
            self.GPIO.setwarnings(False)

            for pin in self.pins.keys():

                if self.pins[pin]['type'] == 'input':

                    self.GPIO.setup(self.pins[pin]['gpio'], self.GPIO.IN)

                    self.pins[pin]['state'] = {
                        'active': False,
                        'start': (datetime.datetime.now() - datetime.datetime.fromtimestamp(0)).total_seconds()
                    }

                    if isinstance(self.pins[pin]['actions'], dict):

                        for actionType in self.pins[pin]['actions'].keys():

                            self.pins[pin]['actions'][actionType]['last'] = (datetime.datetime.now() - datetime.datetime.fromtimestamp(0)).total_seconds()

                elif self.pins[pin]['type'] == 'output':

                    self.GPIO.setup(self.pins[pin]['gpio'], self.GPIO.OUT)

                    if self.pins[pin]['state']['active'] == True:

                        self.GPIO.output(self.pins[pin]['gpio'], self.GPIO.LOW)

                    else:

                        self.GPIO.output(self.pins[pin]['gpio'], self.GPIO.HIGH)

        except Exception as e:

            self.log(
                '.'.join(
                    [
                        str(self.__class__.__name__),
                        str(sys._getframe().f_code.co_name)
                    ]
                ),
                str(e)
            )


        return


    def pollGpio(self):
        """Handles input events."""

        try:

            for pin in self.pins.keys():

                if self.pins[pin]['type'] == 'input':

                    self.pins[pin]['state']['active'] = self.GPIO.input(self.pins[pin]['gpio'])
                    self.pins[pin]['state']['start'] = (datetime.datetime.now() - datetime.datetime.fromtimestamp(0)).total_seconds()

            for pin in self.pins.keys():

                if self.pins[pin]['type'] == 'input':

                    if isinstance(self.pins[pin]['actions'], dict):

                        timestamp = (datetime.datetime.now() - datetime.datetime.fromtimestamp(0)).total_seconds()

                        if 'short' in self.pins[pin]['actions'].keys() or 'short_combo' in self.pins[pin]['actions'].keys():

                            if self.pins[pin]['state']['active'] == False and self.pins[pin]['state']['start'] > self.settings['last_loop']:

                                if 'short' in self.pins[pin]['actions'].keys():

                                    if timestamp - self.pins[pin]['actions']['short']['last'] >= self.settings['action_throttle']:

                                        self.pins[pin]['actions']['short']['last'] = timestamp

                                        self.triggerAction(self.pins[pin]['actions']['short']['type'])

                                if 'short_combo' in self.pins[pin]['actions'].keys():

                                    if timestamp - self.pins[pin]['actions']['short_combo']['last'] >= self.settings['action_throttle']:

                                        comboTriggered = all(
                                            [
                                                (self.pins[comboPin]['state']['active'] == False and self.pins[comboPin]['state']['start'] > self.settings['last_loop'])
                                                for comboPin in self.pins[pin]['actions']['short_combo']['combo_pins']
                                            ]
                                        )

                                        if comboTriggered == True:

                                            self.pins[pin]['actions']['short_combo']['last'] = timestamp

                                            for comboPin in self.pins[pin]['actions']['long_combo']['combo_pins']:

                                                self.pins[comboPin]['actions']['short_combo']['last'] = timestamp

                                            self.triggerAction(self.pins[pin]['actions']['short_combo']['type'])

                        if 'long' in self.pins[pin]['actions'].keys() or 'long_combo' in self.pins[pin]['actions'].keys():

                            if self.pins[pin]['state']['active'] == True and (timestamp - self.pins[pin]['state']['start']) >= self.settings['long_press_delay']:

                                if 'long' in self.pins[pin]['actions'].keys():

                                    if timestamp - self.pins[pin]['actions']['long']['last'] >= self.settings['action_throttle']:

                                        self.pins[pin]['actions']['long']['last'] = timestamp

                                        self.triggerAction(self.pins[pin]['actions']['long']['type'])

                                if 'long_combo' in self.pins[pin]['actions'].keys():

                                    if timestamp - self.pins[pin]['actions']['long_combo']['last'] >= self.settings['action_throttle']:

                                        comboTriggered = all(
                                            [
                                                (self.pins[comboPin]['state']['active'] == True and (timestamp - self.pins[comboPin]['state']['start']) >= self.settings['long_press_delay'])
                                                for comboPin in self.pins[pin]['actions']['long_combo']['combo_pins']
                                            ]
                                        )

                                        if comboTriggered == True:

                                            self.pins[pin]['actions']['long_combo']['last'] = timestamp

                                            for comboPin in self.pins[pin]['actions']['long_combo']['combo_pins']:

                                                self.pins[comboPin]['actions']['long_combo']['last'] = timestamp

                                            self.triggerAction(self.pins[pin]['actions']['long_combo']['type'])

        except Exception as e:

            self.log(
                '.'.join(
                    [
                        str(self.__class__.__name__),
                        str(sys._getframe().f_code.co_name)
                    ]
                ),
                str(e)
            )


        return
    def pollMpu6050(self):
        """Update orientation from MPU 6050."""

        if hasattr(self, 'mpu6050'):

            values = None

            try:

                tempValues = self.mpu6050.getValues()
                values = tempValues

            except Exception as e:

                self.log(
                    '.'.join(
                        [
                            str(self.__class__.__name__),
                            str(sys._getframe().f_code.co_name)
                        ]
                    ),
                    ' - '.join(
                        [
                            'Error getting MPU 6050 values',
                            str(e)
                        ]
                    )
                )

                self.mpu6050State['error_count'] = self.mpu6050State['error_count'] + 1

                if self.mpu6050State['error_count'] >= self.mpu6050State['error_threshold']:

                    self.initMpu6050()


            if isinstance(values, dict):

                for key in values.keys():

                    self.mpu6050State[key] = values[key]

                if (self.mpu6050State['roll'] >= -45.0 and self.mpu6050State['roll'] <= 45.0) or (self.mpu6050State['roll'] >= 135.0 and self.mpu6050State['roll'] <= 225.0):

                    if not self.mpu6050State['orientation'] == 'landscape':

                        self.mpu6050State['orientation'] = 'landscape'

                        self.sendRequest(
                            method='POST',
                            endpoint='/api/settings/image',
                            data={
                                'orientation': 'landscape'
                            },
                            appendToken=True,
                            returnJson=False,
                            logError=True
                        )

                else:

                    if not self.mpu6050State['orientation'] == 'portrait':

                        self.mpu6050State['orientation'] = 'portrait'

                        self.sendRequest(
                            method='POST',
                            endpoint='/api/settings/image',
                            data={
                                'orientation': 'portrait'
                            },
                            appendToken=True,
                            returnJson=False,
                            logError=True
                        )


        return
    def triggerAction(self, action):
        """Actions in response to input events."""

        if action == 'reboot':

            os.system('sudo reboot')

        elif action == 'next':

            self.sendRequest(
                method='POST',
                endpoint='/api/images/display',
                data={
                    'action': 'next'
                },
                appendToken=True,
                returnJson=False,
                logError=True
            )

        elif action == 'previous':

            self.sendRequest(
                method='POST',
                endpoint='/api/images/display',
                data={
                    'action': 'previous'
                },
                appendToken=True,
                returnJson=False,
                logError=True
            )

        elif action == 'pause_toggle':

            self.sendRequest(
                method='POST',
                endpoint='/api/settings/image',
                data={
                    'paused': True # auto toggle
                },
                appendToken=True,
                returnJson=False,
                logError=True
            )


        return


    def loop(self):
        """Main loop."""

        self.log(
            '.'.join(
                [
                    str(self.__class__.__name__),
                    str(sys._getframe().f_code.co_name)
                ]
            ),
            'Starting main loop.'
        )

        self.settings['last_loop'] = (datetime.datetime.now() - datetime.datetime.fromtimestamp(0)).total_seconds()

        while True:

            self.pollGpio()
            self.pollMpu6050()

            self.settings['last_loop'] = (datetime.datetime.now() - datetime.datetime.fromtimestamp(0)).total_seconds()

            time.sleep(self.settings['loop_delay'])


if __name__ == '__main__':

    pencil = Pencil()
