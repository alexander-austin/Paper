#  Copyright (c) 2024, Alexander Austin
#  All rights reserved.
#
#  This source code is licensed under the BSD-style license found in the
#  LICENSE file in the root directory of this source tree.


# Parent class for client API services


#!/usr/bin/python3.12
# -*- coding: utf-8 -*-


import datetime, json, os, requests, sys, time


class ApiAgent:


    def apiAuthenticate(self):
        """Authenticates API."""

        self.loadEnvironment()

        self.waitForServer()

        self.refreshCredentials()

        self.refreshToken()


        return
    def loadEnvironment(self):
        """Loads required settings."""

        if not hasattr(self, 'settings'):

            self.settings = {
                'init_delay': 0.0,
                'loop_delay': 5.0,
                'server_wait_delay': 3.0
            }


        self.settings['log_file'] = os.path.join(
            os.path.dirname(
                os.path.realpath(__file__)
            ),
            'Paper',        
            'data',
            '.'.join(
                [
                    str(self.__class__.__name__),
                    'log'
                ]
            )
        )
        self.settings['credentials_file'] = os.path.join(
            os.path.dirname(
                os.path.realpath(__file__)
            ),
            'Paper',        
            'data',
            'api_credentials.json'
        )

        self.log(
            '.'.join(
                [
                    str(self.__class__.__name__),
                    str(sys._getframe().f_code.co_name)
                ]
            ),
            'Loading environment.'
        )


        self.settings['server'] = {
            'protocol': None,
            'host': None,
            'port': -1
        }

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

            self.log(
                '.'.join(
                    [
                        str(self.__class__.__name__),
                        str(sys._getframe().f_code.co_name)
                    ]
                ),
                'No server settings, exiting.'
            )

            sys.exit('No server settings, exiting.')

        self.log(
            '.'.join(
                [
                    str(self.__class__.__name__),
                    str(sys._getframe().f_code.co_name)
                ]
            ),
            'Environment loaded.'
        )


        return
    def waitForServer(self):
        """Checks server status until it's online."""

        self.log(
            '.'.join(
                [
                    str(self.__class__.__name__),
                    str(sys._getframe().f_code.co_name)
                ]
            ),
            'Waiting for server.'
        )

        time.sleep(self.settings['init_delay'])

        serverAlive = False

        while serverAlive == False:

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

                if apiStatus == 200:

                    if not apiResponse is None:

                        if 'status' in apiResponse.keys():

                            if apiResponse['status'] == 'ok':

                                serverAlive = True

            except: pass

            time.sleep(self.settings['server_wait_delay'])

        self.log(
            '.'.join(
                [
                    str(self.__class__.__name__),
                    str(sys._getframe().f_code.co_name)
                ]
            ),
            'Server online.'
        )


        return
    def refreshCredentials(self):
        """Refresh API user credentials."""

        self.log(
            '.'.join(
                [
                    str(self.__class__.__name__),
                    str(sys._getframe().f_code.co_name)
                ]
            ),
            'Refreshing credentials.'
        )

        refreshed = False

        while refreshed == False:

            try:

                apiStatus, apiResponse = self.sendRequest(
                    method='POST',
                    endpoint='/api/maintenance/export',
                    data=None,
                    appendToken=False,
                    returnJson=True,
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

                                        os.remove(self.settings['credentials_file'])

                                        refreshed = True

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

                self.refreshCredentials()

                break

            time.sleep(self.settings['server_wait_delay'])

        self.log(
            '.'.join(
                [
                    str(self.__class__.__name__),
                    str(sys._getframe().f_code.co_name)
                ]
            ),
            'Credentials refreshed.'
        )


        return
    def refreshToken(self):
        """Refresh API token."""

        refreshed = False

        while refreshed == False:

            try:

                login = False

                if 'token' in self.settings.keys():

                    if isinstance(self.settings['token'], dict):

                        if 'token' in self.settings['token'].keys() and 'expires' in self.settings['token'].keys():

                            if self.settings['token']['expires'] >= ((datetime.datetime.now() - datetime.datetime.fromtimestamp(0)).total_seconds() + 30.0):

                                refreshed = True

                            else: login = True

                        else: login = True

                    else: login = True

                else: login = True


                if login == True:

                    self.log(
                        '.'.join(
                            [
                                str(self.__class__.__name__),
                                str(sys._getframe().f_code.co_name)
                            ]
                        ),
                        'Refreshing token.'
                    )

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
                            logError=True
                        )

                        if apiStatus == 200:

                            if isinstance(apiResponse, dict):

                                if 'token' in apiResponse.keys():

                                    self.settings['token'] = apiResponse

                                    if isinstance(self.settings['token'], dict):

                                        if 'token' in self.settings['token'].keys() and 'expires' in self.settings['token'].keys():

                                            refreshed = True

                                            self.log(
                                                '.'.join(
                                                    [
                                                        str(self.__class__.__name__),
                                                        str(sys._getframe().f_code.co_name)
                                                    ]
                                                ),
                                                'Token refreshed.'
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

                self.refreshToken()

                break

            time.sleep(self.settings['server_wait_delay'])


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

                        if 'token' in self.settings['token'].keys():

                            if data is None:

                                requestData = {
                                    'token': self.settings['token']['token']
                                }

                            elif isinstance(data, dict):

                                requestData = {
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
                                'Invalid token.'
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


            requestUrl='%(protocol)s://%(host)s:%(port)s%(endpoint)s' % {
                'protocol': self.settings['server']['protocol'],
                'host': self.settings['server']['host'],
                'port': self.settings['server']['port'],
                'endpoint': endpoint
            }
            requestHeaders={
                'Accept': 'application/json'
            } if requestData is None else {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            if not requestData is None: requestData = json.dumps(requestData)

            if method == 'GET':

                response = requests.get(
                    url=requestUrl,
                    headers=requestHeaders,
                    data=requestData,
                    timeout=timeout
                )

            elif method == 'POST':

                response = requests.post(
                    url=requestUrl,
                    headers=requestHeaders,
                    data=requestData,
                    timeout=timeout
                )

            elif method == 'DELETE':

                response = requests.delete(
                    url=requestUrl,
                    headers=requestHeaders,
                    data=requestData,
                    timeout=timeout
                )


            if not response is None:

                responseStatus = response.status_code

                if response.status_code == 200:

                    if returnJson == True:

                        responseJsonTemp = response.json()

                        responseJson = responseJsonTemp

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


    def log(self, source, status):
        """Write log."""

        try:

            if not isinstance(status, str): status = json.dumps(status)

            with open(self.settings['log_file'], 'a', encoding='utf-8') as f:

                f.write(
                    '%s | %s : %s\n' % (
                        str(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S.%f'))[0:-3],
                        source,
                        status.replace('\r', '').replace('\n', '\\n')
                    )
                )

        except Exception as e:

            print(
                '.'.join(
                    [
                        str(self.__class__.__name__),
                        str(sys._getframe().f_code.co_name)
                    ]
                ),
                ' - '.join(
                    [
                        'Error writing log',
                        str(e)
                    ]
                )
            )


        return
