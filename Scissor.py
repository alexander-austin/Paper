#  Copyright (c) 2024, Alexander Austin
#  All rights reserved.
#
#  This source code is licensed under the BSD-style license found in the
#  LICENSE file in the root directory of this source tree.


# Background worker for periodic tasks


#!/usr/bin/python3.12
# -*- coding: utf-8 -*-


import datetime, json, os, requests, time, sys


class Scissor:


    def __init__(self):
        """Initialize."""

        self.loadEnvironment()

        self.waitForServer()

        self.refreshCredentials()

        self.refreshToken()


        self.loop()


        return
    def loadEnvironment(self):
        """Loads basic settings."""

        if not hasattr(self, 'settings'):

            self.settings = {
                'loop_delay': 5.0
            }


        self.settings['log_file'] = os.path.join(
            os.path.dirname(
                os.path.realpath(__file__)
            ),
            'Paper',        
            'data',
            'Scissor.log'
        )
        self.settings['credentials_file'] = os.path.join(
            os.path.dirname(
                os.path.realpath(__file__)
            ),
            'Paper',        
            'data',
            'Scissor.json'
        )
        

        self.settings['server'] = {}
        
        self.settings['server']['protocol'] = os.environ.get(
            'PAPER_SERVER_PROTOCOL',
            None
        )
        self.settings['server']['host'] = os.environ.get(
            'PAPER_SERVER_HOST',
            None
        )
        self.settings['server']['port'] = int(
            os.environ.get(
                'PAPER_SERVER_PORT',
                '-1'
            )
        )
        
        if self.settings['server']['protocol'] is None or self.settings['server']['host'] is None or self.settings['server']['port'] == -1:

            self.log('Scissor.loadEnvironment', 'No server settings, exiting.')

            sys.exit(-1)


        return
    def waitForServer(self):
        """Checks server status until it's online."""

        while True:

            serverStatus = -1

            try:

                apiStatus, apiResponse = self.sendRequest(
                    method='GET',
                    endpoint='/api/alive',
                    data=None,
                    appendToken=False,
                    returnJson=True,
                    timeout=3.0,
                    logError=True
                )

                if not apiStatus == 200:

                    serverStatus = -1

                elif not apiResponse is None:

                    if 'status' in apiResponse.keys():

                        if apiResponse['status'] == 'ok':

                            serverStatus = 0

            except: serverStatus = -1


            if serverStatus == 0:

                break


            time.sleep(self.settings['loop_delay'])


        return


    def refreshCredentials(self):
        """Refresh API user credentials."""

        try:

            refreshed = False

            apiStatus, apiResponse = self.sendRequest(
                method='POST',
                endpoint='/api/maintenance/export',
                data=None,
                appendToken=False,
                returnJson=True,
                timeout=3.0,
                logError=True
            )

            if apiStatus == 200:

                if not apiResponse is None:

                    if isinstance (apiResponse, dict):

                        if not 'error' in apiResponse.keys():

                            if os.path.exists(self.settings['credentials_file']):

                                with open(self.settings['credentials_file'], 'r', encoding='utf-8') as f:

                                    creds = json.loads(f.read())

                                    self.settings['credentials'] = creds

                                    refreshed = True

                                if refreshed == True:

                                    os.remove(self.settings['credentials_file'])

            if refreshed == False:

                time.sleep(self.settings['loop_delay'])

                self.refreshCredentials()

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
    def refreshToken(self):
        """Refresh API token."""

        try:

            refreshed = False

            login = False

            if 'token' in self.settings.keys():

                if isinstance(self.settings['token'], dict):

                    if 'token' in self.settings['token'] and 'expires' in self.settings['token']:

                        current = (datetime.datetime.now() - datetime.datetime.fromtimestamp(0)).total_seconds()

                        if self.settings['token']['expires'] < current:

                            login = True

                        else:

                            refreshed = True

                            return

                    else:

                        login = True

                else:

                    login = True

            else:

                login = True


            if login == True:

                if not 'credentials' in self.settings.keys():

                    self.refreshCredentials()

                if 'credentials' in self.settings.keys():

                    apiStatus, apiResponse = self.sendRequest(
                        method='POST',
                        endpoint='/api/auth/login',
                        data={
                            'username': self.settings['credentials']['username'],
                            'password': self.settings['credentials']['password']
                        },
                        appendToken=False,
                        returnJson=True,
                        timeout=3.0,
                        logError=True
                    )

                    if apiStatus == 200:

                        if not apiResponse is None:

                            if isinstance(apiResponse, dict):

                                if 'token' in apiResponse.keys():

                                    self.settings['token'] = apiResponse

                                    refreshed = True


            if refreshed == False:

                self.refreshCredentials()

                time.sleep(self.settings['loop_delay'])

                self.refreshToken()

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


    def getTasks(self):
        """Gets tasks from API."""

        try:

            apiStatus, apiResponse = self.sendRequest(
                method='GET',
                endpoint='/api/maintenance/task',
                data=None,
                appendToken=True,
                returnJson=True,
                logError=True
            )

            if (not apiResponse is None) and apiStatus == 200:

                if isinstance(apiResponse, dict):

                    if 'task_data' in apiResponse.keys():

                        if not apiResponse['task_data'] is None:

                            if hasattr(self, 'tasks'):

                                for t in range(len(self.tasks)):

                                    for apiTask in apiResponse['task_data']:

                                        if self.tasks[t]['name'] == apiTask['name']:

                                            if self.tasks[t]['last'] < apiTask['last']:

                                                for taskKey in apiTask.keys():

                                                    self.tasks[t][taskKey] = apiTask[taskKey]

                                            break

                                for apiTask in apiResponse['task_data']:

                                    if not apiTask['name'] in [task['name'] for task in self.tasks]:

                                        self.tasks.append(apiTask)

                            else:

                                self.tasks = apiResponse['task_data']

                        self.log(
                            '.'.join(
                                [
                                    str(self.__class__.__name__),
                                    str(sys._getframe().f_code.co_name)
                                ]
                            ),
                            'Empty task data.'
                        )

                    else:

                        self.log(
                            '.'.join(
                                [
                                    str(self.__class__.__name__),
                                    str(sys._getframe().f_code.co_name)
                                ]
                            ),
                            'Error getting tasks.'
                        )

                else:

                    self.log(
                        '.'.join(
                            [
                                str(self.__class__.__name__),
                                str(sys._getframe().f_code.co_name)
                            ]
                        ),
                        'Error getting tasks.'
                    )

            else:

                self.log(
                    '.'.join(
                        [
                            str(self.__class__.__name__),
                            str(sys._getframe().f_code.co_name)
                        ]
                    ),
                    'Error getting tasks.'
                )

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
    def setTask(self, task, apiStatus, apiResponse):
        """Updates task to API."""

        try:

            task['last'] = (datetime.datetime.now() - datetime.datetime.fromtimestamp(0)).total_seconds()

            if isinstance(apiResponse, dict):

                if 'error' in apiResponse.keys():

                    if isinstance(apiResponse['error'], str):

                        task['status'] = apiResponse['error']

                elif 'status' in apiResponse.keys():

                    if isinstance(apiResponse['status'], str):

                        task['status'] = apiResponse['status']

            else:

                if apiResponse == 200:

                    task['status'] == 'ok'

                else:

                    task['status'] == 'error: ' + str(apiStatus)


            updateStatus, updateResponse = self.sendRequest(
                method='POST',
                endpoint='/api/maintenance/task',
                data={
                    'name': task['name'],
                    'last': task['last'],
                    'status': task['status']
                },
                appendToken=True,
                returnJson=False,
                logError=True
            )

            if not updateStatus == 200:

                self.log(
                    '.'.join(
                        [
                            str(self.__class__.__name__),
                            str(sys._getframe().f_code.co_name)
                        ]
                    ),
                    'Error updating task "%(task_name)s" - %(status_code)i - %(response)s' % {
                        'task_name': task['name'],
                        'status_code': updateStatus,
                        'response': '' if updateResponse is None else json.dumps(updateResponse)
                    }
                )

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


    def sendRequest(self, method='GET', endpoint='/api/alive', data=None, appendToken=True, returnJson=True, timeout=3.0, logError=True):
        """Send API request, receive response."""

        responseStatus = None
        responseJson = None

        try:

            requestData = None
            response = None

            if appendToken == True:

                self.refreshToken()

                if hasattr(self, 'settings'):

                    if 'token' in self.settings.keys():

                        if data is None:

                            requestData = {
                                'token': self.settings['token']['token']
                            }

                        elif isinstance(data, dict):

                            requestData = requestData = {
                                'token': self.settings['token']['token']
                            }

                            for dataKey in data.keys():

                                requestData[dataKey] = data[dataKey]

                        elif isinstance(data, list):

                            requestData = {
                                'token': self.settings['token']['token'],
                                'data': data
                            }

                    else:

                        self.log(
                            '.'.join(
                                [
                                    str(self.__class__.__name__),
                                    str(sys._getframe().f_code.co_name)
                                ]
                            ),
                            'Missing token.'
                        )

                        return responseStatus, responseJson

                else:

                    self.log(
                        '.'.join(
                            [
                                str(self.__class__.__name__),
                                str(sys._getframe().f_code.co_name)
                            ]
                        ),
                        'Missing settings.'
                    )

                    return responseStatus, responseJson

            else:

                requestData = data


            if method == 'GET':

                response = requests.get(
                    url='%(protocol)s://%(host)s:%(port)s%(endpoint)s' % {
                        'protocol': self.settings['server']['protocol'],
                        'host': self.settings['server']['host'],
                        'port': self.settings['server']['port'],
                        'endpoint': endpoint
                    },
                    headers={
                        'Accept': 'application/json'
                    } if requestData is None else {
                        'Accept': 'application/json',
                        'Content-Type': 'application/json'
                    },
                    data=None if requestData is None else json.dumps(requestData),
                    timeout=timeout
                )

            elif method == 'POST':

                response = requests.post(
                    url='%(protocol)s://%(host)s:%(port)s%(endpoint)s' % {
                        'protocol': self.settings['server']['protocol'],
                        'host': self.settings['server']['host'],
                        'port': self.settings['server']['port'],
                        'endpoint': endpoint
                    },
                    headers={
                        'Accept': 'application/json'
                    } if requestData is None else {
                        'Accept': 'application/json',
                        'Content-Type': 'application/json'
                    },
                    data=None if requestData is None else json.dumps(requestData),
                    timeout=timeout
                )

            elif method == 'DELETE':

                response = requests.delete(
                    url='%(protocol)s://%(host)s:%(port)s%(endpoint)s' % {
                        'protocol': self.settings['server']['protocol'],
                        'host': self.settings['server']['host'],
                        'port': self.settings['server']['port'],
                        'endpoint': endpoint
                    },
                    headers={
                        'Accept': 'application/json'
                    } if requestData is None else {
                        'Accept': 'application/json',
                        'Content-Type': 'application/json'
                    },
                    data=None if requestData is None else json.dumps(requestData),
                    timeout=timeout
                )


            if not response is None:

                responseStatus = response.status_code

                if response.status_code == 200:

                    if returnJson == True:

                        responseJson = response.json()

        except Exception as e:

            if logError == True:

                self.log(
                    '.'.join(
                        [
                            str(self.__class__.__name__),
                            str(sys._getframe().f_code.co_name)
                        ]
                    ),
                    str(e)
                )


        return responseStatus, responseJson


    def loop(self):
        """Main loop."""

        while True:

            self.getTasks()

            if hasattr(self, 'tasks'):

                if isinstance(self.tasks, list):

                    for task in self.tasks:

                        if isinstance(task, dict):

                            timestamp = (datetime.datetime.now() - datetime.datetime.fromtimestamp(0)).total_seconds()

                            if (task['last'] + task['delay']) < timestamp:

                                task['last'] = timestamp
                                task['status'] = 'ok'

                                apiStatus, apiResponse = self.sendRequest(
                                    method=task['method'],
                                    endpoint=task['endpoint'],
                                    data=None,
                                    appendToken=True,
                                    returnJson=True,
                                    logError=True
                                )

                                self.setTask(
                                    task,
                                    apiStatus,
                                    apiResponse
                                )


            time.sleep(self.settings['loop_delay'])


    def log(self, source, status):
        """Write log."""

        try:

            with open(self.settings['log_file'], 'a', encoding='utf-8') as f:

                f.write(
                    '%s | %s : %s\n' % (
                        str(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S.%f'))[0:-3],
                        source,
                        status
                    )
                )

        except:

            print(
                'Could not open',
                self.settings['log_file'],
                source,
                status
            )


        return


if __name__ == '__main__':

    scissor = Scissor()
