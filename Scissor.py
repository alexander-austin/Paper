#  Copyright (c) 2024, Alexander Austin
#  All rights reserved.
#
#  This source code is licensed under the BSD-style license found in the
#  LICENSE file in the root directory of this source tree.


# Background worker for periodic maintenance tasks


#!/usr/bin/python3.12
# -*- coding: utf-8 -*-


import datetime, json, time, sys
from ApiAgent import ApiAgent


class Scissor(ApiAgent):


    def __init__(self):
        """Initialize."""

        self.settings = {
            'init_delay': 5.0,
            'loop_delay': 5.0,
            'server_wait_delay': 3.0
        }

        self.apiAuthenticate()

        self.loop()


        return


    def getTasks(self):
        """Gets tasks from API."""
        self.log('Scissor.getTasks', 'getting tasks')
        try:

            apiStatus, apiResponse = self.sendRequest(
                method='GET',
                endpoint='/api/maintenance/task',
                data=None,
                appendToken=True,
                returnJson=True,
                timeout=3.0,
                logError=True
            )

            if apiStatus == 200:

                if isinstance(apiResponse, dict):

                    if 'task_data' in apiResponse.keys():

                        if isinstance(apiResponse['task_data'], dict|list):

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

                        else:

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


if __name__ == '__main__':

    scissor = Scissor()
