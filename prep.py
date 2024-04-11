#  Copyright (c) 2024, Alexander Austin
#  All rights reserved.
#
#  This source code is licensed under the BSD-style license found in the
#  LICENSE file in the root directory of this source tree.


#!/usr/bin/python3.12
# -*- coding: utf-8 -*-


import os, subprocess
from cryptography.fernet import Fernet
from random import choice


class Prep:


    presets = {
        'protocol': 'http',
        'host': 'localhost',
        'port': '5000'
    }

    services = [
        {
            'name': 'paper',
            'description': 'ePaper Server',
            'exec': 'run.py',
            'template': '[Unit]\nDescription=%(description)s\nAfter=network.target\n\n[Service]\nUser=%(username)s\nWorkingDirectory=%(project_path)s\nEnvironment="PAPER_SERVER_PROTOCOL=%(protocol)s"\nEnvironment="PAPER_SERVER_HOST=%(host)s"\nEnvironment="PAPER_SERVER_PORT=%(port)s"\nEnvironment="PAPER_DB_KEY=%(db_key)s"\nEnvironment="PAPER_DB_SALT=%(db_salt)s"\nExecStart=/usr/bin/python3.12 %(exec)s\nRestart=always\n\n[Install]\nWantedBy=multi-user.target'
        }, {
            'name': 'scissor',
            'description': 'ePaper Background Worker',
            'exec': 'Scissor.py',
            'template': '[Unit]\nDescription=%(description)s\nAfter=network.target\n\n[Service]\nUser=%(username)s\nWorkingDirectory=%(project_path)s\nEnvironment="PAPER_SERVER_PROTOCOL=%(protocol)s"\nEnvironment="PAPER_SERVER_HOST=%(host)s"\nEnvironment="PAPER_SERVER_PORT=%(port)s"\nExecStart=/usr/bin/python3.12 %(exec)s\nRestart=always\n\n[Install]\nWantedBy=multi-user.target'
        }
    ]


    def __init__(self):
        """Initialize."""

        self.setVariables()
        self.createFiles()

        self.ingestLocal()

        self.startServer()


        return


    def setVariables(self):
        """Set service file variables."""

        print('Setting variables...')

        # Database Key
        if not 'db_key' in self.presets.keys():

            self.presets['db_key'] = Fernet.generate_key().decode('utf-8')

        # Database Salt
        if not 'db_salt' in self.presets.keys():

            self.presets['db_salt'] = ''.join(
                [
                    choice(
                        'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_'
                    )
                    for c in range(64)
                ]
            )

        # Run as current user if not specified
        if not 'username' in self.presets.keys():

            self.presets['username'] = os.getlogin()

        os.environ['PAPER_DB_PROTOCOL'] = self.presets['protocol']
        os.environ['PAPER_DB_HOST'] = self.presets['host']
        os.environ['PAPER_DB_PORT'] = self.presets['port']
        os.environ['PAPER_DB_KEY'] = self.presets['db_key']
        os.environ['PAPER_DB_SALT'] = self.presets['db_salt']


        # Service File Variables
        for s in range(len(self.services)):

            self.services[s]['path'] = '/etc/systemd/system/%(name)s.service' % {
                'name': self.services[s]['name']
            }

            self.services[s]['project_path'] = os.path.dirname(
                os.path.realpath(__file__)
            )

            self.services[s]['text'] = self.services[s]['template'] % dict(
                [
                    (
                        presetKey,
                        self.presets[presetKey]
                    )
                    for presetKey in ['protocol', 'host', 'port', 'db_key', 'db_salt', 'username']
                ] + [
                    (
                        serviceKey,
                        self.services[s][serviceKey]
                    )
                    for serviceKey in ['name', 'description', 'exec', 'project_path']
                ]
            )


        return
    def createFiles(self):
        """Create service files."""

        print('Creating files...')

        for s in range(len(self.services)):

            tempPath = os.path.join(
                os.path.dirname(
                    os.path.realpath(__file__)
                ),
                self.services[s]['path'].rsplit(os.sep, 1)[-1]
            )

            # Remove Existing
            self.runCommands(
                [
                    'sudo bash -c \'rm %(temp_path)s\'\n' % {
                        'temp_path': tempPath
                    },
                    'sudo bash -c \'rm %(service_path)s\'\n' % {
                        'service_path': self.services[s]['path']
                    }
                ]
            )


            # Write Temp File
            with open(tempPath, 'w', encoding='utf-8') as f:

                f.write(self.services[s]['text'])


            # Set Permissions & Move
            self.runCommands(
                [
                    'sudo chmod 0644 %(temp_path)s' % {
                        'temp_path': tempPath
                    },
                    'sudo chown root:root %(temp_path)s' % {
                        'temp_path': tempPath
                    },
                    'sudo bash -c \'mv %(temp_path)s %(service_path)s\'\n' % {
                        'temp_path': tempPath,
                        'service_path': self.services[s]['path']
                    }
                ]
            )


        return


    def ingestLocal(self):
        """Ingest locally added images."""

        print('Ingesting local files...')

        from Paper.Backend import Backend

        backend = Backend()
        backend.ingestLocalImages()


        return


    def startServer(self):
        """Starts server processes."""

        print('Starting services...')

        self.runCommands(
            [
                'sudo systemctl daemon-reload',
                'sudo systemctl enable paper.service',
                'sudo systemctl enable scissor.service',
                'sudo systemctl enable nginx.service',
                'sudo systemctl start paper.service',
                'sudo systemctl start nginx.service',
                'sudo systemctl start scissor.service'
            ]
        )


        return


    def runCommands(self, commands):
        """Runs os commands."""

        for command in commands:

            commandProcess = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )

            while True:

                processOut = commandProcess.stdout.readline().strip('\n').strip('\r').strip()

                if len(processOut) > 0: print(processOut)

                if processOut == '' and commandProcess.poll() is not None: break


        return


if __name__ == '__main__':

    prep = Prep()
