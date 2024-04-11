#  Copyright (c) 2024, Alexander Austin
#  All rights reserved.
#
#  This source code is licensed under the BSD-style license found in the
#  LICENSE file in the root directory of this source tree.


#!/usr/bin/python3.12
# -*- coding: utf-8 -*-


import json, sys
from flask import jsonify, make_response, request
from Paper import server


from Paper.Backend import Backend
logFileKey = 'server_log'
backend = Backend()


def getAuthorization(req):
    """Checks cookie authorization."""

    authorization = {
        'logged_in': False,
        'api': False,
        'admin': False,
        'settings': False,
        'media': False,
        'user': None
    }

    try:

        token = None

        try:

            token = req.cookies.get('token')

        except: pass

        if token is None:

            try:

                jsonData = req.json

                if not jsonData is None:

                    if 'token' in jsonData.keys():

                        token = jsonData['token']

            except: pass


        if not token is None:

            user = backend.getUserFromToken(token)

            if not user is None:

                authorization['logged_in'] = True
                authorization['user'] = user

                permissionIds = [
                    userPermission['permission_id']
                    for userPermission in user['user_permissions']
                ]

                if 0 in permissionIds: authorization['api'] = True

                if 1 in permissionIds: authorization['admin'] = True

                if 2 in permissionIds: authorization['settings'] = True

                if 3 in permissionIds: authorization['media'] = True

    except Exception as e:

        backend.log(
            logFileKey,
            '.'.join(
                [
                    'Server_API',
                    str(sys._getframe().f_code.co_name),
                    req.method
                ]
            ),
            str(e)
        )


    return authorization


@server.route('/api/alive', methods=['GET'])
def alive():
    """Reports server is alive."""
    

    return jsonify({'status': 'ok'}), 200


@server.route('/api/auth/<path:subpath>', methods=['POST'])
def apiAuth(subpath):
    """Handles API Authentication."""

    try:

        if request.method == 'POST':

            if subpath == 'login':

                requestData = request.json

                if not requestData is None:

                    if all([key in requestData.keys() for key in ['username', 'password']]) == True:

                        token = backend.getUserToken(
                            requestData['username'],
                            requestData['password']
                        )

                        if not token is None:

                            response = make_response(
                                jsonify(token), 200
                            )
                            response.set_cookie(
                                'token',
                                value=token['token'],
                                expires=token['expires']
                            )

                            return response

    except Exception as e:

        backend.log(
            logFileKey,
            '.'.join(
                [
                    'Server_API',
                    str(sys._getframe().f_code.co_name),
                    request.method
                ]
            ),
            str(e)
        )


    return jsonify({'error': 'Bad Request'}), 400


@server.route('/api/images/<path:subpath>', methods=['GET', 'POST', 'DELETE'])
def apiImages(subpath):
    """Handles API image data."""

    try:

        authorization = getAuthorization(request)

        if request.method == 'GET':

            if authorization['logged_in'] == True:

                imageData = backend.getImageData(subpath)

                return jsonify(imageData), 200

            else:

                return jsonify({'error': 'Unauthorized'}), 401

        elif request.method == 'POST':

            if subpath == 'display':

                if authorization['logged_in'] == True:

                    imageInfo = None

                    try:

                        requestData = request.json

                        if isinstance(requestData, dict):

                            if 'data' in requestData.keys():

                                imageInfo = requestData['data']

                            if 'action' in requestData.keys():

                                imageInfo = {
                                    'action': requestData['action']
                                }

                                if requestData['action'] == 'set' and 'id' in requestData.keys():

                                    imageInfo['id'] = requestData['id']

                    except: pass

                    statusMessage, statusCode = backend.displayImage(imageInfo)

                    if not statusCode == 200:

                        return jsonify(statusMessage), statusCode

                    imageSettings = backend.getSettingsData('image')

                    return jsonify(imageSettings), 200

                else:

                    return jsonify({'error': 'Unauthorized'}), 401

            elif subpath == 'edit':

                if authorization['api'] == True or authorization['media'] == True:

                    requestData = request.json

                    if isinstance(requestData, dict):

                        if 'data' in requestData.keys():

                            requestData = requestData['data']

                        if 'id' in requestData.keys():

                            if 'tags' in requestData.keys() or 'description' in requestData.keys():

                                if 'tags' in requestData.keys():

                                    backend.setImageTags(
                                        requestData['id'],
                                        requestData['tags']
                                    )

                                if 'description' in requestData.keys():

                                    backend.setImageDescription(
                                        requestData['id'],
                                        requestData['description']
                                    )

                                imageData = backend.getImageData('all')

                                return jsonify(imageData), 200

                else:

                    return jsonify({'error': 'Unauthorized'}), 401

            elif subpath == 'upload':

                if authorization['api'] == True or authorization['media'] == True:

                    requestData = request.form.to_dict()

                    fileInfo = json.loads(requestData['info'])
                    fileBytes = request.files.getlist('file')[0]
                    
                    uploadProgress, uploadStatus = backend.processUploadChunk(fileInfo, fileBytes)
                    
                    return jsonify(uploadProgress), uploadStatus

                else:

                    return jsonify({'error': 'Unauthorized'}), 401

        elif request.method == 'DELETE':

            if subpath == 'delete':

                if authorization['api'] == True or authorization['media'] == True:

                    requestData = request.json

                    if isinstance(requestData, dict):

                        if 'data' in requestData.keys():

                            requestData = requestData['data']

                        if 'id' in requestData.keys():

                            backend.deleteImage(requestData['id'])

                            imageData = backend.getImageData('all')

                            return jsonify(imageData), 200

                else:

                    return jsonify({'error': 'Unauthorized'}), 401

    except Exception as e:

        backend.log(
            logFileKey,
            '.'.join(
                [
                    'Server_API',
                    str(sys._getframe().f_code.co_name),
                    request.method
                ]
            ),
            str(e)
        )


    return jsonify({'error': 'Bad Request'}), 400


@server.route('/api/settings/<path:subpath>', methods=['GET', 'POST', 'DELETE'])
def apiSettings(subpath):
    """Handles settings data."""

    try:

        authorization = getAuthorization(request)

        if authorization['logged_in'] == True:

            if request.method == 'GET':

                if subpath == 'image':

                    imageSettings = backend.getSettingsData('image')

                    return jsonify(imageSettings), 200

                elif subpath == 'password':

                    passwordSettings = backend.getSettingsData('password')

                    return jsonify(passwordSettings), 200

                elif subpath == 'category':

                    categoriesSettings = backend.getCategoryData()

                    return jsonify(categoriesSettings), 200

                elif subpath == 'user':

                    if authorization['api'] == True or authorization['admin'] == True:

                        userData = backend.getUserData('all')

                        return jsonify(userData), 200

                    else:

                        userData = backend.getUserData(authorization['user']['id'])

                        return jsonify(userData), 200

                elif subpath == 'permission':

                    if authorization['api'] == True or authorization['admin'] == True:

                        permissionData = backend.getSettingsData('permission')

                        return jsonify(permissionData), 200

            elif request.method == 'POST':

                if subpath == 'image':

                    if authorization['api'] == True or authorization['settings'] == True:

                        requestData = request.json

                        if isinstance(requestData, dict):

                            if 'data' in requestData.keys():

                                requestData = requestData['data']

                            settingsData = dict(
                                [
                                    (
                                        key,
                                        requestData[key]
                                    )
                                    for key in requestData.keys()
                                    if not key == 'token'
                                ]
                            )

                            backend.setSettingsData('image', settingsData)

                            imageSettings = backend.getSettingsData('image')

                            return jsonify(imageSettings), 200

                    else:

                        return jsonify({'error': 'Unauthorized'}), 401

                elif subpath == 'password':

                    if authorization['api'] == True or authorization['settings'] == True:

                        requestData = request.json

                        if isinstance(requestData, dict):

                            if 'data' in requestData.keys():

                                requestData = requestData['data']

                            settingsData = dict(
                                [
                                    (
                                        key,
                                        requestData[key]
                                    )
                                    for key in requestData.keys()
                                    if not key == 'token'
                                ]
                            )

                            backend.setSettingsData('password', settingsData)

                            passwordSettings = backend.getSettingsData('password')

                            return jsonify(passwordSettings), 200

                    else:

                        return jsonify({'error': 'Unauthorized'}), 401

                elif subpath == 'category':

                    if authorization['api'] == True or authorization['settings'] == True:

                        requestData = request.json

                        if isinstance(requestData, dict):

                            if 'data' in requestData.keys():

                                requestData = requestData['data']

                            requestData = dict(
                                [
                                    (
                                        key,
                                        requestData[key]
                                    )
                                    for key in requestData.keys()
                                    if not key == 'token'
                                ]
                            )

                        backend.setCategoryData(requestData)

                        categoriesSettings = backend.getCategoryData()

                        return jsonify(categoriesSettings), 200

                    else:

                        return jsonify({'error': 'Unauthorized'}), 401

                elif subpath == 'user':

                    requestData = request.json

                    if isinstance(requestData, dict):

                        if 'data' in requestData.keys():

                            requestData = requestData['data']

                    if authorization['api'] == True or authorization['admin'] == True:

                        backend.setUserData(requestData)

                        userData = backend.getUserData('all')

                        return jsonify(userData), 200

                    elif requestData['id'] == authorization['user']['id']:

                        backend.setUserData(requestData)

                        userData = backend.getUserData(authorization['user']['id'])

                        return jsonify(userData), 200

                    else:

                        return jsonify({'error': 'Unauthorized'}), 401

            elif request.method == 'DELETE':

                if subpath == 'user':

                    requestData = request.json

                    if isinstance(requestData, dict):

                        if 'data' in requestData.keys():

                            requestData = requestData['data']

                    if authorization['api'] == True or authorization['admin'] == True:

                        if 'id' in requestData.keys():

                            backend.deleteUser(requestData['id'])

                            userData = backend.getUserData('all')

                            return jsonify(userData), 200

                    else:

                        return jsonify({'error': 'Unauthorized'}), 401

        else:

            return jsonify({'error': 'Unauthorized'}), 401

    except Exception as e:

        backend.log(
            logFileKey,
            '.'.join(
                [
                    'Server_API',
                    str(sys._getframe().f_code.co_name),
                    request.method
                ]
            ),
            str(e)
        )


    return jsonify({'error': 'Bad Request'}), 400


@server.route('/api/maintenance/<path:subpath>', methods=['GET', 'POST', 'DELETE'])
def maintenance(subpath):
    """Handles API log requests."""

    try:

        authorization = getAuthorization(request)

        if request.method == 'GET':

            if subpath == 'info':

                if authorization['api'] == True or authorization['admin'] == True:

                    serverData = backend.getServerInfo()

                    return jsonify(serverData), 200

                else:

                    return jsonify({'error': 'Unauthorized'}), 401

            elif subpath == 'logs':

                if authorization['api'] == True or authorization['admin'] == True:
                    
                    requestData = request.json

                    if isinstance(requestData, dict):

                        if 'data' in requestData.keys():

                            requestData = requestData['data']

                    logData = backend.getLogs(requestData)

                    return jsonify(logData), 200

                else:

                    return jsonify({'error': 'Unauthorized'}), 401

            elif subpath == 'task':

                if authorization['api'] == True or authorization['admin'] == True:

                    taskData = backend.getTaskData()

                    return jsonify(taskData), 200

                else:

                    return jsonify({'error': 'Unauthorized'}), 401

        elif request.method == 'POST':

            if subpath == 'export':

                statusMessage, statusCode = backend.exportApiUser()

                return jsonify(statusMessage), statusCode

            elif subpath == 'info':

                if authorization['api'] == True or authorization['admin'] == True:

                    statusMessage, statusCode = backend.collectServerInfo()

                    return jsonify(statusMessage), statusCode

                else:

                    return jsonify({'error': 'Unauthorized'}), 401

            elif subpath == 'ingest':

                if authorization['api'] == True or authorization['admin'] == True:

                    statusMessage, statusCode = backend.ingestLocalImages()

                    return jsonify(statusMessage), statusCode

                else:

                    return jsonify({'error': 'Unauthorized'}), 401

            elif subpath == 'task':

                if authorization['api'] == True or authorization['admin'] == True:

                    requestData = request.json

                    if isinstance(requestData, dict):

                        if 'data' in requestData.keys():

                            requestData = requestData['data']

                    statusMessage, statusCode = backend.setTaskData(requestData)

                    if not statusCode == 200:

                        return jsonify(statusMessage), statusCode

                    taskData = backend.getTaskData()

                    return jsonify(taskData), 200

                else:

                    return jsonify({'error': 'Unauthorized'}), 401

        elif request.method == 'DELETE':

            if subpath == 'logs':

                if authorization['api'] == True or authorization['admin'] == True:

                    statusMessage, statusCode = backend.rotateLogs()

                    return jsonify(statusMessage), statusCode

                else:

                    return jsonify({'error': 'Unauthorized'}), 401

            elif subpath == 'temp':

                if authorization['api'] == True or authorization['admin'] == True:

                    statusMessage, statusCode = backend.clearTempFiles()

                    return jsonify(statusMessage), statusCode

                else:

                    return jsonify({'error': 'Unauthorized'}), 401

            elif subpath == 'tokens':

                if authorization['api'] == True or authorization['admin'] == True:

                    statusMessage, statusCode = backend.reapExpiredTokens()

                    return jsonify(statusMessage), statusCode

                else:

                    return jsonify({'error': 'Unauthorized'}), 401

    except Exception as e:

        backend.log(
            logFileKey,
            '.'.join(
                [
                    'Server_API',
                    str(sys._getframe().f_code.co_name),
                    request.method
                ]
            ),
            str(e)
        )


    return jsonify({'error': 'Bad Request'}), 400
