#  Copyright (c) 2024, Alexander Austin
#  All rights reserved.
#
#  This source code is licensed under the BSD-style license found in the
#  LICENSE file in the root directory of this source tree.


#!/usr/bin/python3.12
# -*- coding: utf-8 -*-


import glob, os, sys
from flask import jsonify, make_response, redirect, render_template, request, send_file
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
                    'Server_UI',
                    str(sys._getframe().f_code.co_name),
                    req.method
                ]
            ),
            str(e)
        )


    return authorization


@server.route('/', methods=['GET'])
def home():
    """Renders the home page."""

    try:

        authorization = getAuthorization(request)

        if authorization['logged_in'] == True:

            return render_template(
                'index.html',
                title='Paper',
                show_navigation=True,
                auth_admin=authorization['admin'],
                auth_settings=authorization['settings'],
                auth_media=authorization['media'],
                user=authorization['user'],
                chunk_size=server.CHUNKSIZE
            ), 200

        else:

            return redirect('/login', 302)

    except Exception as e:

        backend.log(
            logFileKey,
            '.'.join(
                [
                    'Server_UI',
                    str(sys._getframe().f_code.co_name),
                    request.method
                ]
            ),
            str(e)
        )


    return redirect('/login', 302)


@server.route('/settings', methods=['GET'])
def settings():
    """Renders the settings page."""

    try:

        authorization = getAuthorization(request)

        if authorization['admin'] == True or authorization['settings'] == True:

            return render_template(
                'settings.html',
                title='Paper | Settings',
                show_navigation=True,
                auth_admin=authorization['admin'],
                auth_settings=authorization['settings'],
                auth_media=authorization['media'],
                user=authorization['user'],
                chunk_size=server.CHUNKSIZE
            ), 200

        else:

            return redirect('/login', 302)

    except Exception as e:

        backend.log(
            logFileKey,
            '.'.join(
                [
                    'Server_UI',
                    str(sys._getframe().f_code.co_name),
                    request.method
                ]
            ),
            str(e)
        )


    return redirect('/login', 302)


@server.route('/user', methods=['GET'])
def user():
    """Renders the user page."""

    try:

        authorization = getAuthorization(request)

        if authorization['logged_in'] == True:

            return render_template(
                'user.html',
                title='Paper | User',
                show_navigation=True,
                auth_admin=authorization['admin'],
                auth_settings=authorization['settings'],
                auth_media=authorization['media'],
                user=authorization['user'],
                chunk_size=server.CHUNKSIZE
            ), 200

        else:

            return redirect('/login', 302)

    except Exception as e:

        backend.log(
            logFileKey,
            '.'.join(
                [
                    'Server_UI',
                    str(sys._getframe().f_code.co_name),
                    request.method
                ]
            ),
            str(e)
        )


    return redirect('/login', 302)


@server.route('/login', methods=['GET', 'POST'])
def login():

    try:

        if request.method == 'GET':

            return render_template(
                'login.html',
                title='Paper | Login',
                show_navigation=False,
                password_regex=backend.db.getPasswordRegex(),
                login_error=''
            ), 200

        elif request.method == 'POST':

            requestData = request.form.to_dict()

            if all([key in requestData.keys() for key in ['username', 'password']]) == True:

                token = backend.getUserToken(
                    username=requestData['username'],
                    password=requestData['password']
                )

                if not token is None:

                    response = make_response(
                        redirect('/', 302)
                    )
                    response.set_cookie(
                        'token',
                        value=token['token'],
                        expires=token['expires']
                    )

                    return response

                else:

                    return render_template(
                        'login.html',
                        title='Paper | Login',
                        password_regex=backend.db.getPasswordRegex(),
                        login_error='Invalid username/password.'
                    ), 401

    except Exception as e:

        backend.log(
            logFileKey,
            '.'.join(
                [
                    'Server_UI',
                    str(sys._getframe().f_code.co_name),
                    request.method
                ]
            ),
            str(e)
        )


    return jsonify({'error': 'Bad Request'}), 400


@server.route('/images/<path:subpath>', methods=['GET'])
def images(subpath):
    """Returns uploaded images."""

    try:

        authorization = getAuthorization(request)

        if authorization['logged_in'] == True:

            for imageType in ['original', 'thumbnail', 'quantization']:

                if subpath.startswith(imageType + '/'):

                    for imagePath in glob.glob(os.path.join(backend.db.paths[imageType]['path'], '*')):

                        if imagePath.rsplit(os.sep, 1)[-1] == subpath.rsplit('/', 1)[-1]:

                            return send_file(imagePath), 200

    except Exception as e:

        backend.log(
            logFileKey,
            '.'.join(
                [
                    'Server_UI',
                    str(sys._getframe().f_code.co_name),
                    request.method
                ]
            ),
            str(e)
        )


    return jsonify({'error': 'Not Found'}), 404


@server.route('/scripts/<path:subpath>', methods=['GET'])
def scripts(subpath):
    """Return js files."""

    try:

        if subpath in ['login.js', 'main.js']:

            localPath = os.path.join(
                os.path.dirname(
                    os.path.realpath(__file__)
                ),
                'scripts',
                subpath.strip('/').split('?')[0]
            )

            if os.path.exists(localPath):

                return send_file(localPath), 200

            else:

                return jsonify({'error': 'Not Found'}), 404

        else:

            authorization = getAuthorization(request)

            if authorization['logged_in'] == True:

                if subpath in ['images.js', 'menu.js', 'user.js']:

                    localPath = os.path.join(
                        os.path.dirname(
                            os.path.realpath(__file__)
                        ),
                        'scripts',
                        subpath.strip('/').split('?')[0]
                    )

                    if os.path.exists(localPath):

                        return send_file(localPath), 200

                    else:

                        return jsonify({'error': 'Not Found'}), 404

                elif subpath == 'images_extended.js':

                    if authorization['admin'] == True or authorization['settings'] == True or authorization['media'] == True:

                        localPath = os.path.join(
                            os.path.dirname(
                                os.path.realpath(__file__)
                            ),
                            'scripts',
                            subpath.strip('/').split('?')[0]
                        )

                        if os.path.exists(localPath):

                            return send_file(localPath), 200

                        else:

                            return jsonify({'error': 'Not Found'}), 404

                elif subpath == 'settings.js':

                    if authorization['admin'] == True or authorization['settings'] == True:

                        localPath = os.path.join(
                            os.path.dirname(
                                os.path.realpath(__file__)
                            ),
                            'scripts',
                            subpath.strip('/').split('?')[0]
                        )

                        if os.path.exists(localPath):

                            return send_file(localPath), 200

                        else:

                            return jsonify({'error': 'Not Found'}), 404

                elif subpath == 'user_extended.js':

                    if authorization['admin'] == True:

                        localPath = os.path.join(
                            os.path.dirname(
                                os.path.realpath(__file__)
                            ),
                            'scripts',
                            subpath.strip('/').split('?')[0]
                        )

                        if os.path.exists(localPath):

                            return send_file(localPath), 200

                        else:

                            return jsonify({'error': 'Not Found'}), 404

                else:

                    return jsonify({'error': 'Not Found'}), 404

            else:

                return jsonify({'error': 'Unauthorized'}), 401

    except Exception as e:

        backend.log(
            logFileKey,
            '.'.join(
                [
                    'Server_UI',
                    str(sys._getframe().f_code.co_name),
                    request.method
                ]
            ),
            str(e)
        )


    return jsonify({'error': 'Bad Request'}), 400


@server.route('/styles/<path:subpath>', methods=['GET'])
def styles(subpath):
    """Return css files."""

    try:

        if subpath in ['login.css', 'main.css']:

            localPath = os.path.join(
                os.path.dirname(
                    os.path.realpath(__file__)
                ),
                'styles',
                subpath.strip('/').split('?')[0]
            )

            if os.path.exists(localPath):

                return send_file(localPath), 200

            else:

                return jsonify({'error': 'Not Found'}), 404

        else:

            authorization = getAuthorization(request)

            if authorization['logged_in'] == True:

                if subpath in ['images.css', 'menu.css', 'user.css']:

                    localPath = os.path.join(
                        os.path.dirname(
                            os.path.realpath(__file__)
                        ),
                        'styles',
                        subpath.strip('/').split('?')[0]
                    )

                    if os.path.exists(localPath):

                        return send_file(localPath), 200

                    else:

                        return jsonify({'error': 'Not Found'}), 404

                elif subpath == 'images_extended.css':

                    if authorization['admin'] == True or authorization['settings'] == True or authorization['media'] == True:

                        localPath = os.path.join(
                            os.path.dirname(
                                os.path.realpath(__file__)
                            ),
                            'styles',
                            subpath.strip('/').split('?')[0]
                        )

                        if os.path.exists(localPath):

                            return send_file(localPath), 200

                        else:

                            return jsonify({'error': 'Not Found'}), 404

                elif subpath == 'settings.css':

                    if authorization['admin'] == True or authorization['settings'] == True:

                        localPath = os.path.join(
                            os.path.dirname(
                                os.path.realpath(__file__)
                            ),
                            'styles',
                            subpath.strip('/').split('?')[0]
                        )

                        if os.path.exists(localPath):

                            return send_file(localPath), 200

                        else:

                            return jsonify({'error': 'Not Found'}), 404

                elif subpath == 'user_extended.css':

                    if authorization['admin'] == True:

                        localPath = os.path.join(
                            os.path.dirname(
                                os.path.realpath(__file__)
                            ),
                            'styles',
                            subpath.strip('/').split('?')[0]
                        )

                        if os.path.exists(localPath):

                            return send_file(localPath), 200

                        else:

                            return jsonify({'error': 'Not Found'}), 404

                else:

                    return jsonify({'error': 'Not Found'}), 404

            else:

                return jsonify({'error': 'Unauthorized'}), 401

    except Exception as e:

        backend.log(
            logFileKey,
            '.'.join(
                [
                    'Server_UI',
                    str(sys._getframe().f_code.co_name),
                    request.method
                ]
            ),
            str(e)
        )


    return jsonify({'error': 'Bad Request'}), 400


def root():
    """Return root level files."""

    if request.method == 'GET':

        localPath = os.path.join(
            os.path.dirname(
                os.path.realpath(__file__)
            ),
            'static',
            request.path.strip('/').split('?')[0]
        )

        if os.path.exists(localPath):

            return send_file(localPath), 200


    return jsonify({'error': 'Not Found'}), 404
for rootFile in glob.glob(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static', '*')):

    server.add_url_rule(
        '/' + rootFile.rsplit(os.sep, 1)[-1],
        'root',
        root,
        methods=['GET']
    )
