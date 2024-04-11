#  Copyright (c) 2024, Alexander Austin
#  All rights reserved.
#
#  This source code is licensed under the BSD-style license found in the
#  LICENSE file in the root directory of this source tree.


#!/usr/bin/python3.12
# -*- coding: utf-8 -*-


from os import environ
from Paper import server
import Paper.Api, Paper.Ui


if __name__ == '__main__':

    HOST = environ.get(
        'PAPER_SERVER_HOST',
        'localhost'
    )
    PORT = int(
        environ.get(
            'PAPER_SERVER_PORT',
            '5000'
        )
    )


    server.run(HOST, PORT)
