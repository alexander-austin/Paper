#  Copyright (c) 2024, Alexander Austin
#  All rights reserved.
#
#  This source code is licensed under the BSD-style license found in the
#  LICENSE file in the root directory of this source tree.


#!/usr/bin/python3.12
# -*- coding: utf-8 -*-


import datetime, json, os, re, sqlite3, sys
from cryptography.fernet import Fernet
from random import choice


class DB:


    dbObjectInfo = [
        {
            'index': 0,
            'type': 'settings',
            'table': 'settings',
            'db_object': 'DbSettings',
            'db_type': 'config',
            'queries': {
                'create': 'CREATE TABLE settings (' \
                    '    id       INTEGER PRIMARY KEY ASC ON CONFLICT ROLLBACK' \
                    '                     UNIQUE ON CONFLICT ROLLBACK' \
                    '                     NOT NULL ON CONFLICT ROLLBACK' \
                    '                     CHECK (id = 0)' \
                    '                     DEFAULT (0),' \
                    '    cypher   BLOB,' \
                    '    token    BLOB,' \
                    '    password BLOB,' \
                    '    image    BLOB' \
                    ');',
                'insert': 'INSERT OR REPLACE INTO %(table)s (%(columns)s) VALUES (%(value_placeholders)s);',
                'default_sort': 'ORDER BY id ASC'
            },
            'columns': [
                {
                    'index': 0,
                    'key': 'id',
                    'data_info': {
                        'storage_type': 'INTEGER',
                        'primary_key': True,
                        'unique': True,
                        'unique_validation': {
                            'table': 'settings',
                            'key': 'id'
                        },
                        'unique_generator': None,
                        'not_null': True,
                        'boolean': False,
                        'password': False,
                        'json': False,
						'date': False,
                        'api': False
                    }
                }, {
                    'index': 1,
                    'key': 'cypher',
                    'data_info': {
                        'storage_type': 'BLOB',
                        'primary_key': False,
                        'unique': False,
                        'not_null': False,
                        'boolean': False,
                        'password': False,
                        'json': True,
						'date': False,
                        'api': False
                    }
                }, {
                    'index': 2,
                    'key': 'token',
                    'data_info': {
                        'storage_type': 'BLOB',
                        'primary_key': False,
                        'unique': False,
                        'not_null': False,
                        'boolean': False,
                        'password': False,
                        'json': True,
						'date': False,
                        'api': False
                    }
                }, {
                    'index': 3,
                    'key': 'password',
                    'data_info': {
                        'storage_type': 'BLOB',
                        'primary_key': False,
                        'unique': False,
                        'not_null': False,
                        'boolean': False,
                        'password': False,
                        'json': True,
						'date': False,
                        'api': True
                    }
                }, {
                    'index': 4,
                    'key': 'image',
                    'data_info': {
                        'storage_type': 'BLOB',
                        'primary_key': False,
                        'unique': False,
                        'not_null': False,
                        'boolean': False,
                        'password': False,
                        'json': True,
						'date': False,
                        'api': False
                    }
                }
            ],
            'defaults': [
                {
                    'id': 0,
                    'cypher': None,
                    'token': {
                        'choices': 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789`~!@#$%^&*()-_=+,.<>?|[];',
                        'length': 64,
                        'duration': 604800
                    },
                    'password': {
                        'upper': True,
                        'lower': True,
                        'number': True,
                        'special': True,
                        'length': 8
                    },
                    'image': {
                        'paused': False,
                        'current': -1,
                        'queue': [],
                        'filters': [],
                        'orientation': 'landscape',
                        'orientation_control': 'manual',
                        'orientation_auto_control_available': False,
                        'size': [800, 480],
                        'sizing': {
                            'type': 'fit',
                            'fill': 'blur'
                        },
                        'blur_brightness': 0.5,
                        'thumbnail_sizes': [256, 128, 64],
                        'extension': 'png',
                        'palette': {
                            'black': [0, 0, 0],
                            'white': [255, 255, 255],
                            'green': [0, 255, 0],
                            'blue': [0, 0, 255],
                            'red': [255, 0, 0],
                            'yellow': [255, 255, 0],
                            'orange': [255, 128, 0]
                        }
                    }
                }
            ],
            'children': []
        }, {
            'index': 1,
            'type': 'user',
            'table': 'users',
            'db_object': 'DbUser',
            'db_type': 'standard',
            'queries': {
                'create': 'CREATE TABLE users (' \
                    '    id          INTEGER PRIMARY KEY ASC ON CONFLICT ROLLBACK' \
                    '                        UNIQUE ON CONFLICT ROLLBACK' \
                    '                        NOT NULL ON CONFLICT ROLLBACK,' \
                    '    username    TEXT    UNIQUE ON CONFLICT ROLLBACK' \
                    '                        NOT NULL ON CONFLICT ROLLBACK,' \
                    '    given_name  TEXT,' \
                    '    family_name TEXT,' \
                    '    password    TEXT    NOT NULL ON CONFLICT ROLLBACK' \
                    ');',
                'default_sort': 'ORDER BY id ASC'
            },
            'columns': [
                {
                    'index': 0,
                    'key': 'id',
                    'data_info': {
                        'storage_type': 'INTEGER',
                        'primary_key': True,
                        'unique': True,
                        'unique_validation': {
                            'table': 'users',
                            'key': 'id'
                        },
                        'unique_generator': 'generateUniqueInt',
                        'unique_generator_args': {
                            'table': 'users',
                            'key': 'id'
                        },
                        'not_null': True,
                        'boolean': False,
                        'password': False,
                        'json': False,
						'date': False,
                        'api': True
                    }
                }, {
                    'index': 1,
                    'key': 'username',
                    'data_info': {
                        'storage_type': 'TEXT',
                        'primary_key': False,
                        'unique': True,
                        'unique_validation': {
                            'table': 'users',
                            'key': 'username'
                        },
                        'unique_generator': None,
                        'not_null': True,
                        'boolean': False,
                        'password': False,
                        'json': False,
						'date': False,
                        'api': True
                    }
                }, {
                    'index': 2,
                    'key': 'given_name',
                    'data_info': {
                        'storage_type': 'TEXT',
                        'primary_key': False,
                        'unique': False,
                        'not_null': False,
                        'boolean': False,
                        'password': False,
                        'json': False,
						'date': False,
                        'api': True
                    }
                }, {
                    'index': 3,
                    'key': 'family_name',
                    'data_info': {
                        'storage_type': 'TEXT',
                        'primary_key': False,
                        'unique': False,
                        'not_null': False,
                        'boolean': False,
                        'password': False,
                        'json': False,
						'date': False,
                        'api': True
                    }
                }, {
                    'index': 4,
                    'key': 'password',
                    'data_info': {
                        'storage_type': 'TEXT',
                        'primary_key': False,
                        'unique': False,
                        'not_null': True,
                        'boolean': False,
                        'password': True,
                        'json': False,
						'date': False,
                        'api': False
                    }
                }
            ],
            'defaults': [
                {
                    'id': 1,
                    'username': 'admin',
                    'given_name': '',
                    'family_name': '',
                    'password': 'Ch@ng3_!+'
                }
            ],
            'children': [
                {
                    'type': 'user_permission',
                    'key': 'user_permissions',
                    'local_key': 'id',
                    'foreign_key': 'user_id',
                    'relationship': 'one_to_many',
                    'modify_first': False
                }, {
                    'type': 'token',
                    'key': 'tokens',
                    'local_key': 'id',
                    'foreign_key': 'user_id',
                    'relationship': 'one_to_many',
                    'modify_first': False
                }
            ]
        }, {
            'index': 2,
            'type': 'permission',
            'table': 'permissions',
            'db_object': 'DbPermission',
            'db_type': 'standard',
            'queries': {
                'create': 'CREATE TABLE permissions (' \
                    '    id          INTEGER PRIMARY KEY ASC ON CONFLICT ROLLBACK' \
                    '                        UNIQUE ON CONFLICT ROLLBACK' \
                    '                        NOT NULL ON CONFLICT ROLLBACK,' \
                    '    name        TEXT    UNIQUE ON CONFLICT ROLLBACK' \
                    '                        NOT NULL ON CONFLICT ROLLBACK,' \
                    '    description TEXT' \
                    ');',
                'default_sort': 'ORDER BY id ASC'
            },
            'columns': [
                {
                    'index': 0,
                    'key': 'id',
                    'data_info': {
                        'storage_type': 'INTEGER',
                        'primary_key': True,
                        'unique': True,
                        'unique_validation': {
                            'table': 'permissions',
                            'key': 'id'
                        },
                        'unique_generator': 'generateUniqueInt',
                        'unique_generator_args': {
                            'table': 'permissions',
                            'key': 'id'
                        },
                        'not_null': True,
                        'boolean': False,
                        'password': False,
                        'json': False,
						'date': False,
                        'api': True
                    }
                }, {
                    'index': 1,
                    'key': 'name',
                    'data_info': {
                        'storage_type': 'TEXT',
                        'primary_key': False,
                        'unique': True,
                        'unique_validation': {
                            'table': 'permissions',
                            'key': 'name'
                        },
                        'unique_generator': None,
                        'not_null': True,
                        'boolean': False,
                        'password': False,
                        'json': False,
						'date': False,
                        'api': True
                    }
                }, {
                    'index': 2,
                    'key': 'description',
                    'data_info': {
                        'storage_type': 'TEXT',
                        'primary_key': False,
                        'unique': False,
                        'not_null': False,
                        'boolean': False,
                        'password': False,
                        'json': False,
						'date': False,
                        'api': True
                    }
                }
            ],
            'defaults': [
                {
                    'id': 0,
                    'name': 'API',
                    'description': 'Full API control.'
                }, {
                    'id': 1,
                    'name': 'Admin',
                    'description': 'All "Settings" and "Media" permissions as well as allows user to add, edit, and delete users including resetting passwords.'
                }, {
                    'id': 2,
                    'name': 'Settings',
                    'description': 'All "Media" permissions as well as allows user to change settings.'
                }, {
                    'id': 3,
                    'name': 'Media',
                    'description': 'Allows user to select, upload, delete, and modify media/tags.'
                }
            ],
            'children': []
        }, {
            'index': 3,
            'type': 'user_permission',
            'table': 'user_permissions',
            'db_object': 'DbUserPermission',
            'db_type': 'standard',
            'queries': {
                'create': 'CREATE TABLE user_permissions (' \
                    '    user_id       INTEGER REFERENCES users (id) ON DELETE CASCADE' \
                    '                                                ON UPDATE CASCADE' \
                    '                                                MATCH SIMPLE NOT DEFERRABLE' \
                    '                          NOT NULL ON CONFLICT ROLLBACK,' \
                    '    permission_id INTEGER REFERENCES permissions (id) ON DELETE CASCADE' \
                    '                                                      ON UPDATE CASCADE' \
                    '                                                      MATCH SIMPLE NOT DEFERRABLE' \
                    '                          NOT NULL ON CONFLICT ROLLBACK' \
                    ');',
                'default_sort': 'ORDER BY user_id ASC'
            },
            'columns': [
                {
                    'index': 0,
                    'key': 'user_id',
                    'data_info': {
                        'storage_type': 'INTEGER',
                        'primary_key': False,
                        'unique': False,
                        'not_null': True,
                        'boolean': False,
                        'password': False,
                        'json': False,
						'date': False,
                        'api': True
                    }
                }, {
                    'index': 1,
                    'key': 'permission_id',
                    'data_info': {
                        'storage_type': 'INTEGER',
                        'primary_key': False,
                        'unique': False,
                        'not_null': True,
                        'boolean': False,
                        'password': False,
                        'json': False,
						'date': False,
                        'api': True
                    }
                }
            ],
            'defaults': [
                {
                    'user_id': 0,
                    'permission_id': 0
                }, {
                    'user_id': 1,
                    'permission_id': 1
                }, {
                    'user_id': 1,
                    'permission_id': 2
                }, {
                    'user_id': 1,
                    'permission_id': 3
                }
            ],
            'children': [
                {
                    'type': 'permission',
                    'key': 'permissions',
                    'local_key': 'permission_id',
                    'foreign_key': 'id',
                    'relationship': 'one_to_one',
                    'modify_first': False
                }
            ],
        }, {
            'index': 4,
            'type': 'token',
            'table': 'tokens',
            'db_object': 'DbToken',
            'db_type': 'standard',
            'queries': {
                'create': 'CREATE TABLE tokens (' \
                    '    user_id INTEGER REFERENCES users (id) ON DELETE CASCADE' \
                    '                                          ON UPDATE CASCADE' \
                    '                                          MATCH SIMPLE NOT DEFERRABLE INITIALLY IMMEDIATE' \
                    '                    NOT NULL ON CONFLICT ROLLBACK,' \
                    '    token   TEXT    UNIQUE ON CONFLICT ROLLBACK' \
                    '                    NOT NULL ON CONFLICT ROLLBACK,' \
                    '    expires NUMERIC NOT NULL ON CONFLICT ROLLBACK' \
                    ');',
                'default_sort': 'ORDER BY expires ASC'
            },
            'columns': [
                {
                    'index': 0,
                    'key': 'user_id',
                    'data_info': {
                        'storage_type': 'INTEGER',
                        'primary_key': False,
                        'unique': False,
                        'not_null': True,
                        'boolean': False,
                        'password': False,
                        'json': False,
						'date': False,
                        'api': True
                    }
                }, {
                    'index': 1,
                    'key': 'token',
                    'data_info': {
                        'storage_type': 'TEXT',
                        'primary_key': False,
                        'unique': True,
                        'unique_validation': {
                            'table': 'tokens',
                            'key': 'token'
                        },
                        'unique_generator': 'generateUniqueToken',
                        'unique_generator_args': {
                            'table': 'tokens',
                            'key': 'token'
                        },
                        'not_null': True,
                        'boolean': False,
                        'password': False,
                        'json': False,
						'date': False,
                        'api': True
                    }
                }, {
                    'index': 2,
                    'key': 'expires',
                    'data_info': {
                        'storage_type': 'NUMERIC',
                        'primary_key': False,
                        'unique': False,
                        'not_null': True,
                        'boolean': False,
                        'password': False,
                        'json': False,
						'date': True,
                        'api': True
                    }
                }
            ],
            'defaults': [],
            'children': []
        }, {
            'index': 5,
            'type': 'image',
            'table': 'images',
            'db_object': 'DbImage',
            'db_type': 'standard',
            'queries': {
                'create': 'CREATE TABLE images (' \
                    '    id          INTEGER PRIMARY KEY ASC ON CONFLICT ROLLBACK' \
                    '                        UNIQUE ON CONFLICT ROLLBACK' \
                    '                        NOT NULL ON CONFLICT ROLLBACK,' \
                    '    width       INTEGER NOT NULL ON CONFLICT ROLLBACK,' \
                    '    height      INTEGER NOT NULL ON CONFLICT ROLLBACK,' \
                    '    bytes       INTEGER NOT NULL ON CONFLICT ROLLBACK,' \
                    '    path        TEXT    UNIQUE ON CONFLICT ROLLBACK' \
                    '                        NOT NULL ON CONFLICT ROLLBACK,' \
                    '    file        TEXT    UNIQUE ON CONFLICT ROLLBACK' \
                    '                        NOT NULL ON CONFLICT ROLLBACK,' \
                    '    url         TEXT    UNIQUE ON CONFLICT ROLLBACK' \
                    '                        NOT NULL ON CONFLICT ROLLBACK,' \
                    '    created     NUMERIC NOT NULL ON CONFLICT ROLLBACK,' \
                    '    ingested    NUMERIC NOT NULL ON CONFLICT ROLLBACK,' \
                    '    description TEXT' \
                    ');',
                'default_sort': 'ORDER BY created DESC'
            },
            'columns': [
                {
                    'index': 0,
                    'key': 'id',
                    'data_info': {
                        'storage_type': 'INTEGER',
                        'primary_key': True,
                        'unique': True,
                        'unique_validation': {
                            'table': 'images',
                            'key': 'id'
                        },
                        'unique_generator': 'generateUniqueInt',
                        'unique_generator_args': {
                            'table': 'images',
                            'key': 'id'
                        },
                        'not_null': True,
                        'boolean': False,
                        'password': False,
                        'json': False,
						'date': False,
                        'api': True
                    }
                }, {
                    'index': 1,
                    'key': 'width',
                    'data_info': {
                        'storage_type': 'INTEGER',
                        'primary_key': False,
                        'unique': False,
                        'not_null': True,
                        'boolean': False,
                        'password': False,
                        'json': False,
						'date': False,
                        'api': True
                    }
                }, {
                    'index': 2,
                    'key': 'height',
                    'data_info': {
                        'storage_type': 'INTEGER',
                        'primary_key': False,
                        'unique': False,
                        'not_null': True,
                        'boolean': False,
                        'password': False,
                        'json': False,
						'date': False,
                        'api': True
                    }
                }, {
                    'index': 3,
                    'key': 'bytes',
                    'data_info': {
                        'storage_type': 'INTEGER',
                        'primary_key': False,
                        'unique': False,
                        'not_null': True,
                        'boolean': False,
                        'password': False,
                        'json': False,
						'date': False,
                        'api': True
                    }
                }, {
                    'index': 4,
                    'key': 'path',
                    'data_info': {
                        'storage_type': 'TEXT',
                        'primary_key': False,
                        'unique': True,
                        'unique_validation': {
                            'table': 'images',
                            'key': 'path'
                        },
                        'unique_generator': None,
                        'not_null': True,
                        'boolean': False,
                        'password': False,
                        'json': False,
						'date': False,
                        'api': False
                    }
                }, {
                    'index': 5,
                    'key': 'file',
                    'data_info': {
                        'storage_type': 'TEXT',
                        'primary_key': False,
                        'unique': True,
                        'unique_validation': {
                            'table': 'images',
                            'key': 'file'
                        },
                        'unique_generator': None,
                        'not_null': True,
                        'boolean': False,
                        'password': False,
                        'json': False,
						'date': False,
                        'api': True
                    }
                }, {
                    'index': 6,
                    'key': 'url',
                    'data_info': {
                        'storage_type': 'TEXT',
                        'primary_key': False,
                        'unique': True,
                        'unique_validation': {
                            'table': 'images',
                            'key': 'url'
                        },
                        'unique_generator': None,
                        'not_null': True,
                        'boolean': False,
                        'password': False,
                        'json': False,
						'date': False,
                        'api': True
                    }
                }, {
                    'index': 7,
                    'key': 'created',
                    'data_info': {
                        'storage_type': 'NUMERIC',
                        'primary_key': False,
                        'unique': False,
                        'not_null': True,
                        'boolean': False,
                        'password': False,
                        'json': False,
						'date': True,
                        'api': True
                    }
                }, {
                    'index': 8,
                    'key': 'ingested',
                    'data_info': {
                        'storage_type': 'NUMERIC',
                        'primary_key': False,
                        'unique': False,
                        'not_null': True,
                        'boolean': False,
                        'password': False,
                        'json': False,
						'date': True,
                        'api': True
                    }
                }, {
                    'index': 9,
                    'key': 'description',
                    'data_info': {
                        'storage_type': 'TEXT',
                        'primary_key': False,
                        'unique': False,
                        'not_null': False,
                        'boolean': False,
                        'password': False,
                        'json': False,
						'date': True,
                        'api': True
                    }
                }
            ],
            'defaults': [],
            'children': [
                {
                    'type': 'quantization',
                    'key': 'quantizations',
                    'local_key': 'id',
                    'foreign_key': 'image_id',
                    'relationship': 'one_to_many',
                    'modify_first': False
                }, {
                    'type': 'thumbnail',
                    'key': 'thumbnails',
                    'local_key': 'id',
                    'foreign_key': 'image_id',
                    'relationship': 'one_to_many',
                    'modify_first': False
                }, {
                    'type': 'tag',
                    'key': 'tags',
                    'local_key': 'id',
                    'foreign_key': 'image_id',
                    'relationship': 'one_to_many',
                    'modify_first': False
                }
            ]
        }, {
            'index': 6,
            'type': 'quantization',
            'table': 'quantizations',
            'db_object': 'DbQuantization',
            'db_type': 'standard',
            'queries': {
                'create': 'CREATE TABLE quantizations (' \
                    '    image_id    INTEGER REFERENCES images (id) ON DELETE CASCADE' \
                    '                                               ON UPDATE CASCADE' \
                    '                                               MATCH SIMPLE NOT DEFERRABLE INITIALLY IMMEDIATE' \
                    '                        NOT NULL ON CONFLICT ROLLBACK,' \
                    '    width       INTEGER NOT NULL ON CONFLICT ROLLBACK,' \
                    '    height      INTEGER NOT NULL ON CONFLICT ROLLBACK,' \
                    '    bytes       INTEGER NOT NULL ON CONFLICT ROLLBACK,' \
                    '    path        TEXT    UNIQUE ON CONFLICT ROLLBACK' \
                    '                        NOT NULL ON CONFLICT ROLLBACK,' \
                    '    url         TEXT    UNIQUE ON CONFLICT ROLLBACK' \
                    '                        NOT NULL ON CONFLICT ROLLBACK,' \
                    '    orientation TEXT    NOT NULL ON CONFLICT ROLLBACK' \
                    '                        CHECK (orientation IN (\'landscape\', \'portrait\'))' \
                    ');',
                'default_sort': 'ORDER BY image_id ASC'
            },
            'columns': [
                {
                    'index': 0,
                    'key': 'image_id',
                    'data_info': {
                        'storage_type': 'INTEGER',
                        'primary_key': False,
                        'unique': False,
                        'not_null': True,
                        'boolean': False,
                        'password': False,
                        'json': False,
						'date': False,
                        'api': True
                    }
                }, {
                    'index': 1,
                    'key': 'width',
                    'data_info': {
                        'storage_type': 'INTEGER',
                        'primary_key': False,
                        'unique': False,
                        'not_null': True,
                        'boolean': False,
                        'password': False,
                        'json': False,
						'date': False,
                        'api': True
                    }
                }, {
                    'index': 2,
                    'key': 'height',
                    'data_info': {
                        'storage_type': 'INTEGER',
                        'primary_key': False,
                        'unique': False,
                        'not_null': True,
                        'boolean': False,
                        'password': False,
                        'json': False,
						'date': False,
                        'api': True
                    }
                }, {
                    'index': 3,
                    'key': 'bytes',
                    'data_info': {
                        'storage_type': 'INTEGER',
                        'primary_key': False,
                        'unique': False,
                        'not_null': True,
                        'boolean': False,
                        'password': False,
                        'json': False,
						'date': False,
                        'api': True
                    }
                }, {
                    'index': 4,
                    'key': 'path',
                    'data_info': {
                        'storage_type': 'TEXT',
                        'primary_key': False,
                        'unique': True,
                        'unique_validation': {
                            'table': 'quantizations',
                            'key': 'path'
                        },
                        'unique_generator': None,
                        'not_null': True,
                        'boolean': False,
                        'password': False,
                        'json': False,
						'date': False,
                        'api': False
                    }
                }, {
                    'index': 5,
                    'key': 'url',
                    'data_info': {
                        'storage_type': 'TEXT',
                        'primary_key': False,
                        'unique': True,
                        'unique_validation': {
                            'table': 'quantizations',
                            'key': 'url'
                        },
                        'unique_generator': None,
                        'not_null': True,
                        'boolean': False,
                        'password': False,
                        'json': False,
						'date': False,
                        'api': True
                    }
                }, {
                    'index': 6,
                    'key': 'orientation',
                    'data_info': {
                        'storage_type': 'TEXT',
                        'primary_key': False,
                        'unique': False,
                        'not_null': True,
                        'boolean': False,
                        'password': False,
                        'json': False,
						'date': False,
                        'api': True
                    }
                }
            ],
            'defaults': [],
            'children': []
        }, {
            'index': 7,
            'type': 'thumbnail',
            'table': 'thumbnails',
            'db_object': 'DbThumbnail',
            'db_type': 'standard',
            'queries': {
                'create': 'CREATE TABLE thumbnails (' \
                    '    image_id INTEGER REFERENCES images (id) ON DELETE CASCADE' \
                    '                                            ON UPDATE CASCADE' \
                    '                                            MATCH SIMPLE NOT DEFERRABLE INITIALLY IMMEDIATE' \
                    '                     NOT NULL ON CONFLICT ROLLBACK,' \
                    '    width    INTEGER NOT NULL ON CONFLICT ROLLBACK,' \
                    '    height   INTEGER NOT NULL ON CONFLICT ROLLBACK,' \
                    '    bytes    INTEGER NOT NULL ON CONFLICT ROLLBACK,' \
                    '    path     TEXT    UNIQUE ON CONFLICT ROLLBACK' \
                    '                     NOT NULL ON CONFLICT ROLLBACK,' \
                    '    url      TEXT    UNIQUE ON CONFLICT ROLLBACK' \
                    '                     NOT NULL ON CONFLICT ROLLBACK' \
                    ');',
                'default_sort': 'ORDER BY image_id ASC'
            },
            'columns': [
                {
                    'index': 0,
                    'key': 'image_id',
                    'data_info': {
                        'storage_type': 'INTEGER',
                        'primary_key': False,
                        'unique': False,
                        'not_null': True,
                        'boolean': False,
                        'password': False,
                        'json': False,
						'date': False,
                        'api': True
                    }
                }, {
                    'index': 1,
                    'key': 'width',
                    'data_info': {
                        'storage_type': 'INTEGER',
                        'primary_key': False,
                        'unique': False,
                        'not_null': True,
                        'boolean': False,
                        'password': False,
                        'json': False,
						'date': False,
                        'api': True
                    }
                }, {
                    'index': 2,
                    'key': 'height',
                    'data_info': {
                        'storage_type': 'INTEGER',
                        'primary_key': False,
                        'unique': False,
                        'not_null': True,
                        'boolean': False,
                        'password': False,
                        'json': False,
						'date': False,
                        'api': True
                    }
                }, {
                    'index': 3,
                    'key': 'bytes',
                    'data_info': {
                        'storage_type': 'INTEGER',
                        'primary_key': False,
                        'unique': False,
                        'not_null': True,
                        'boolean': False,
                        'password': False,
                        'json': False,
						'date': False,
                        'api': True
                    }
                }, {
                    'index': 4,
                    'key': 'path',
                    'data_info': {
                        'storage_type': 'TEXT',
                        'primary_key': False,
                        'unique': True,
                        'unique_validation': {
                            'table': 'thumbnails',
                            'key': 'path'
                        },
                        'unique_generator': None,
                        'not_null': True,
                        'boolean': False,
                        'password': False,
                        'json': False,
						'date': False,
                        'api': False
                    }
                }, {
                    'index': 5,
                    'key': 'url',
                    'data_info': {
                        'storage_type': 'TEXT',
                        'primary_key': False,
                        'unique': True,
                        'unique_validation': {
                            'table': 'thumbnails',
                            'key': 'url'
                        },
                        'unique_generator': None,
                        'not_null': True,
                        'boolean': False,
                        'password': False,
                        'json': False,
						'date': False,
                        'api': True
                    }
                }
            ],
            'defaults': [],
            'children': []
        }, {
            'index': 8,
            'type': 'category',
            'table': 'categories',
            'db_object': 'DbCategory',
            'db_type': 'standard',
            'queries': {
                'create': 'CREATE TABLE categories (' \
                    '    id   INTEGER PRIMARY KEY ASC ON CONFLICT ROLLBACK' \
                    '                 UNIQUE ON CONFLICT ROLLBACK' \
                    '                 NOT NULL ON CONFLICT ROLLBACK,' \
                    '    name TEXT    UNIQUE ON CONFLICT ROLLBACK' \
                    '                 NOT NULL ON CONFLICT ROLLBACK' \
                    ');',
                'default_sort': 'ORDER BY name ASC'
            },
            'columns': [
                {
                    'index': 0,
                    'key': 'id',
                    'data_info': {
                        'storage_type': 'INTEGER',
                        'primary_key': True,
                        'unique': True,
                        'unique_validation': {
                            'table': 'categories',
                            'key': 'id'
                        },
                        'unique_generator': 'generateUniqueInt',
                        'unique_generator_args': {
                            'table': 'categories',
                            'key': 'id'
                        },
                        'not_null': True,
                        'boolean': False,
                        'password': False,
                        'json': False,
						'date': False,
                        'api': True
                    }
                }, {
                    'index': 1,
                    'key': 'name',
                    'data_info': {
                        'storage_type': 'TEXT',
                        'primary_key': False,
                        'unique': True,
                        'unique_validation': {
                            'table': 'categories',
                            'key': 'name'
                        },
                        'unique_generator': None,
                        'not_null': True,
                        'boolean': False,
                        'password': False,
                        'json': False,
						'date': False,
                        'api': True
                    }
                }
            ],
            'defaults': [
                {
                    'id': 0,
                    'name': 'People'
                }, {
                    'id': 1,
                    'name': 'Nature'
                }, {
                    'id': 2,
                    'name': 'Places'
                }, {
                    'id': 3,
                    'name': 'Art'
                }
            ],
            'children': [
                {
                    'type': 'subcategory',
                    'key': 'subcategories',
                    'local_key': 'id',
                    'foreign_key': 'category_id',
                    'relationship': 'one_to_many',
                    'modify_first': False
                }
            ]
        }, {
            'index': 9,
            'type': 'subcategory',
            'table': 'subcategories',
            'db_object': 'DbSubcategory',
            'db_type': 'standard',
            'queries': {
                'create': 'CREATE TABLE subcategories (' \
                    '    id          INTEGER PRIMARY KEY ASC ON CONFLICT ROLLBACK' \
                    '                        UNIQUE ON CONFLICT ROLLBACK' \
                    '                        NOT NULL ON CONFLICT ROLLBACK,' \
                    '    category_id INTEGER REFERENCES categories (id) ON DELETE CASCADE' \
                    '                                                   ON UPDATE CASCADE' \
                    '                                                   MATCH SIMPLE NOT DEFERRABLE INITIALLY IMMEDIATE' \
                    '                        NOT NULL ON CONFLICT ROLLBACK,' \
                    '    name        TEXT    NOT NULL ON CONFLICT ROLLBACK' \
                    ');',
                'default_sort': 'ORDER BY name ASC'
            },
            'columns': [
                {
                    'index': 0,
                    'key': 'id',
                    'data_info': {
                        'storage_type': 'INTEGER',
                        'primary_key': True,
                        'unique': True,
                        'unique_validation': {
                            'table': 'subcategories',
                            'key': 'id'
                        },
                        'unique_generator': 'generateUniqueInt',
                        'unique_generator_args': {
                            'table': 'subcategories',
                            'key': 'id'
                        },
                        'not_null': True,
                        'boolean': False,
                        'password': False,
                        'json': False,
						'date': False,
                        'api': True
                    }
                }, {
                    'index': 1,
                    'key': 'category_id',
                    'data_info': {
                        'storage_type': 'INTEGER',
                        'primary_key': False,
                        'unique': False,
                        'not_null': True,
                        'boolean': False,
                        'password': False,
                        'json': False,
						'date': False,
                        'api': True
                    }
                }, {
                    'index': 2,
                    'key': 'name',
                    'data_info': {
                        'storage_type': 'TEXT',
                        'primary_key': False,
                        'unique': True,
                        'unique_validation': {
                            'table': 'subcategories',
                            'key': 'name'
                        },
                        'unique_generator': None,
                        'not_null': True,
                        'boolean': False,
                        'password': False,
                        'json': False,
						'date': False,
                        'api': True
                    }
                }
            ],
            'defaults': [
                {
                    'id': 0,
                    'category_id': 0,
                    'name': 'Family',
                }, {
                    'id': 1,
                    'category_id': 0,
                    'name': 'Friend',
                }, {
                    'id': 2,
                    'category_id': 0,
                    'name': 'Coworker',
                }, {
                    'id': 3,
                    'category_id': 1,
                    'name': 'Mountains',
                }, {
                    'id': 4,
                    'category_id': 1,
                    'name': 'Ocean',
                }, {
                    'id': 5,
                    'category_id': 1,
                    'name': 'Lake',
                }, {
                    'id': 6,
                    'category_id': 1,
                    'name': 'Beach',
                }, {
                    'id': 7,
                    'category_id': 1,
                    'name': 'Forest',
                }, {
                    'id': 8,
                    'category_id': 1,
                    'name': 'Desert',
                }, {
                    'id': 9,
                    'category_id': 2,
                    'name': 'Home',
                }, {
                    'id': 10,
                    'category_id': 2,
                    'name': 'Work',
                }, {
                    'id': 11,
                    'category_id': 3,
                    'name': 'Personal',
                }, {
                    'id': 12,
                    'category_id': 3,
                    'name': 'Renaissance',
                }, {
                    'id': 13,
                    'category_id': 3,
                    'name': 'Modern',
                }
            ],
            'children': []
        }, {
            'index': 10,
            'type': 'tag',
            'table': 'tags',
            'db_object': 'DbTag',
            'db_type': 'standard',
            'queries': {
                'create': 'CREATE TABLE tags (' \
                    '    image_id       INTEGER REFERENCES images (id) ON DELETE CASCADE' \
                    '                                                  ON UPDATE CASCADE' \
                    '                                                  MATCH SIMPLE NOT DEFERRABLE INITIALLY IMMEDIATE' \
                    '                           NOT NULL ON CONFLICT ROLLBACK,' \
                    '    category_id    INTEGER REFERENCES categories (id) ON DELETE CASCADE' \
                    '                                                      ON UPDATE CASCADE' \
                    '                                                      MATCH SIMPLE NOT DEFERRABLE INITIALLY IMMEDIATE' \
                    '                           NOT NULL ON CONFLICT ROLLBACK,' \
                    '    subcategory_id INTEGER REFERENCES subcategories (id) ON DELETE CASCADE' \
                    '                                                         ON UPDATE CASCADE' \
                    '                                                         MATCH SIMPLE DEFERRABLE' \
                    ');',
                'default_sort': 'ORDER BY image_id ASC'
            },
            'columns': [
                {
                    'index': 0,
                    'key': 'image_id',
                    'data_info': {
                        'storage_type': 'INTEGER',
                        'primary_key': False,
                        'unique': False,
                        'not_null': True,
                        'boolean': False,
                        'password': False,
                        'json': False,
						'date': False,
                        'api': True
                    }
                }, {
                    'index': 1,
                    'key': 'category_id',
                    'data_info': {
                        'storage_type': 'INTEGER',
                        'primary_key': False,
                        'unique': False,
                        'not_null': True,
                        'boolean': False,
                        'password': False,
                        'json': False,
						'date': False,
                        'api': True
                    }
                }, {
                    'index': 2,
                    'key': 'subcategory_id',
                    'data_info': {
                        'storage_type': 'INTEGER',
                        'primary_key': False,
                        'unique': False,
                        'not_null': True,
                        'boolean': False,
                        'password': False,
                        'json': False,
						'date': False,
                        'api': True
                    }
                }
            ],
            'defaults': [],
            'children': []
        }, {
            'index': 11,
            'type': 'info',
            'table': 'infos',
            'db_object': 'DbInfo',
            'db_type': 'standard',
            'queries': {
                'create': 'CREATE TABLE infos (' \
                    '    collected               NUMERIC NOT NULL ON CONFLICT ROLLBACK,' \
                    '    temperature_celcius     REAL    NOT NULL ON CONFLICT ROLLBACK,' \
                    '    temperature_fahrenheit  REAL    NOT NULL ON CONFLICT ROLLBACK,' \
                    '    cpu_load_one_minute     REAL    NOT NULL ON CONFLICT ROLLBACK,' \
                    '    cpu_load_five_minute    REAL    NOT NULL ON CONFLICT ROLLBACK,' \
                    '    cpu_load_fifteen_minute REAL    NOT NULL ON CONFLICT ROLLBACK,' \
                    '    ram_used                INTEGER NOT NULL ON CONFLICT ROLLBACK,' \
                    '    ram_total               INTEGER NOT NULL ON CONFLICT ROLLBACK,' \
                    '    originals_count         INTEGER NOT NULL ON CONFLICT ROLLBACK,' \
                    '    originals_size          INTEGER NOT NULL ON CONFLICT ROLLBACK,' \
                    '    quantizations_count     INTEGER NOT NULL ON CONFLICT ROLLBACK,' \
                    '    quantizations_size      INTEGER NOT NULL ON CONFLICT ROLLBACK,' \
                    '    thumbnails_count        INTEGER NOT NULL ON CONFLICT ROLLBACK,' \
                    '    thumbnails_size         INTEGER NOT NULL ON CONFLICT ROLLBACK,' \
                    '    disk_used               INTEGER NOT NULL ON CONFLICT ROLLBACK,' \
                    '    disk_total              INTEGER NOT NULL ON CONFLICT ROLLBACK' \
                    ');',
                'default_sort': 'ORDER BY collected DESC'
            },
            'columns': [
                {
                    'index': 0,
                    'key': 'collected',
                    'data_info': {
                        'storage_type': 'NUMERIC',
                        'primary_key': False,
                        'unique': False,
                        'not_null': True,
                        'boolean': False,
                        'password': False,
                        'json': False,
						'date': True,
                        'api': True
                    }
                }, {
                    'index': 1,
                    'key': 'temperature_celcius',
                    'data_info': {
                        'storage_type': 'REAL',
                        'primary_key': False,
                        'unique': False,
                        'not_null': True,
                        'boolean': False,
                        'password': False,
                        'json': False,
						'date': False,
                        'api': True
                    }
                }, {
                    'index': 2,
                    'key': 'temperature_fahrenheit',
                    'data_info': {
                        'storage_type': 'REAL',
                        'primary_key': False,
                        'unique': False,
                        'not_null': True,
                        'boolean': False,
                        'password': False,
                        'json': False,
						'date': False,
                        'api': True
                    }
                }, {
                    'index': 3,
                    'key': 'cpu_load_one_minute',
                    'data_info': {
                        'storage_type': 'REAL',
                        'primary_key': False,
                        'unique': False,
                        'not_null': True,
                        'boolean': False,
                        'password': False,
                        'json': False,
						'date': False,
                        'api': True
                    }
                }, {
                    'index': 4,
                    'key': 'cpu_load_five_minute',
                    'data_info': {
                        'storage_type': 'REAL',
                        'primary_key': False,
                        'unique': False,
                        'not_null': True,
                        'boolean': False,
                        'password': False,
                        'json': False,
						'date': False,
                        'api': True
                    }
                }, {
                    'index': 5,
                    'key': 'cpu_load_fifteen_minute',
                    'data_info': {
                        'storage_type': 'REAL',
                        'primary_key': False,
                        'unique': False,
                        'not_null': True,
                        'boolean': False,
                        'password': False,
                        'json': False,
						'date': False,
                        'api': True
                    }
                }, {
                    'index': 6,
                    'key': 'ram_used',
                    'data_info': {
                        'storage_type': 'INTEGER',
                        'primary_key': False,
                        'unique': False,
                        'not_null': True,
                        'boolean': False,
                        'password': False,
                        'json': False,
						'date': False,
                        'api': True
                    }
                }, {
                    'index': 7,
                    'key': 'ram_total',
                    'data_info': {
                        'storage_type': 'INTEGER',
                        'primary_key': False,
                        'unique': False,
                        'not_null': True,
                        'boolean': False,
                        'password': False,
                        'json': False,
						'date': False,
                        'api': True
                    }
                }, {
                    'index': 8,
                    'key': 'originals_count',
                    'data_info': {
                        'storage_type': 'INTEGER',
                        'primary_key': False,
                        'unique': False,
                        'not_null': True,
                        'boolean': False,
                        'password': False,
                        'json': False,
						'date': False,
                        'api': True
                    }
                }, {
                    'index': 9,
                    'key': 'originals_size',
                    'data_info': {
                        'storage_type': 'INTEGER',
                        'primary_key': False,
                        'unique': False,
                        'not_null': True,
                        'boolean': False,
                        'password': False,
                        'json': False,
						'date': False,
                        'api': True
                    }
                }, {
                    'index': 10,
                    'key': 'quantizations_count',
                    'data_info': {
                        'storage_type': 'INTEGER',
                        'primary_key': False,
                        'unique': False,
                        'not_null': True,
                        'boolean': False,
                        'password': False,
                        'json': False,
						'date': False,
                        'api': True
                    }
                }, {
                    'index': 11,
                    'key': 'quantizations_size',
                    'data_info': {
                        'storage_type': 'INTEGER',
                        'primary_key': False,
                        'unique': False,
                        'not_null': True,
                        'boolean': False,
                        'password': False,
                        'json': False,
						'date': False,
                        'api': True
                    }
                }, {
                    'index': 12,
                    'key': 'thumbnails_count',
                    'data_info': {
                        'storage_type': 'INTEGER',
                        'primary_key': False,
                        'unique': False,
                        'not_null': True,
                        'boolean': False,
                        'password': False,
                        'json': False,
						'date': False,
                        'api': True
                    }
                }, {
                    'index': 13,
                    'key': 'thumbnails_size',
                    'data_info': {
                        'storage_type': 'INTEGER',
                        'primary_key': False,
                        'unique': False,
                        'not_null': True,
                        'boolean': False,
                        'password': False,
                        'json': False,
						'date': False,
                        'api': True
                    }
                }, {
                    'index': 14,
                    'key': 'disk_used',
                    'data_info': {
                        'storage_type': 'INTEGER',
                        'primary_key': False,
                        'unique': False,
                        'not_null': True,
                        'boolean': False,
                        'password': False,
                        'json': False,
						'date': False,
                        'api': True
                    }
                }, {
                    'index': 15,
                    'key': 'disk_total',
                    'data_info': {
                        'storage_type': 'INTEGER',
                        'primary_key': False,
                        'unique': False,
                        'not_null': True,
                        'boolean': False,
                        'password': False,
                        'json': False,
						'date': False,
                        'api': True
                    }
                }
            ],
            'defaults': [],
            'children': []
        }, {
            'index': 12,
            'type': 'task',
            'table': 'tasks',
            'db_object': 'DbTask',
            'db_type': 'standard',
            'queries': {
                'create': 'CREATE TABLE tasks (' \
                    '    name        TEXT    PRIMARY KEY ASC ON CONFLICT ROLLBACK' \
                    '                        UNIQUE ON CONFLICT ROLLBACK' \
                    '                        NOT NULL ON CONFLICT ROLLBACK,' \
                    '    description TEXT,' \
                    '    method      TEXT    NOT NULL ON CONFLICT ROLLBACK,' \
                    '    endpoint    TEXT    NOT NULL ON CONFLICT ROLLBACK,' \
                    '    delay       NUMERIC NOT NULL ON CONFLICT ROLLBACK' \
                    '                        DEFAULT (15.0),' \
                    '    last        NUMERIC NOT NULL ON CONFLICT ROLLBACK' \
                    '                        DEFAULT (0.0),' \
                    '    status      TEXT' \
                    ');',
                'default_sort': 'ORDER BY delay ASC'
            },
            'columns': [
                {
                    'index': 0,
                    'key': 'name',
                    'data_info': {
                        'storage_type': 'TEXT',
                        'primary_key': True,
                        'unique': True,
                        'unique_validation': {
                            'table': 'tasks',
                            'key': 'name'
                        },
                        'unique_generator': None,
                        'not_null': True,
                        'boolean': False,
                        'password': False,
                        'json': False,
						'date': False,
                        'api': True
                    }
                }, {
                    'index': 1,
                    'key': 'description',
                    'data_info': {
                        'storage_type': 'TEXT',
                        'primary_key': False,
                        'unique': False,
                        'not_null': False,
                        'boolean': False,
                        'password': False,
                        'json': False,
						'date': False,
                        'api': True
                    }
                }, {
                    'index': 2,
                    'key': 'method',
                    'data_info': {
                        'storage_type': 'TEXT',
                        'primary_key': False,
                        'unique': False,
                        'not_null': True,
                        'boolean': False,
                        'password': False,
                        'json': False,
						'date': False,
                        'api': True
                    }
                }, {
                    'index': 3,
                    'key': 'endpoint',
                    'data_info': {
                        'storage_type': 'TEXT',
                        'primary_key': False,
                        'unique': False,
                        'not_null': True,
                        'boolean': False,
                        'password': False,
                        'json': False,
						'date': False,
                        'api': True
                    }
                }, {
                    'index': 4,
                    'key': 'delay',
                    'data_info': {
                        'storage_type': 'NUMERIC',
                        'primary_key': False,
                        'unique': False,
                        'not_null': True,
                        'boolean': False,
                        'password': False,
                        'json': False,
						'date': False,
                        'api': True
                    }
                }, {
                    'index': 5,
                    'key': 'last',
                    'data_info': {
                        'storage_type': 'NUMERIC',
                        'primary_key': False,
                        'unique': False,
                        'not_null': True,
                        'boolean': False,
                        'password': False,
                        'json': False,
						'date': True,
                        'api': True
                    }
                }, {
                    'index': 6,
                    'key': 'status',
                    'data_info': {
                        'storage_type': 'TEXT',
                        'primary_key': False,
                        'unique': False,
                        'not_null': False,
                        'boolean': False,
                        'password': False,
                        'json': False,
						'date': False,
                        'api': True
                    }
                }
            ],
            'defaults': [
                {
                    'name': 'Rotate Images',
                    'description': 'Displays next image in queue.',
                    'method': 'POST',
                    'endpoint': '/api/images/display',
                    'delay': 1800.0,
                    'last': 0.0,
                    'status': 'not run'
                }, {
                    'name': 'Ingest Local',
                    'description': 'Ingests manually added files in "local" folder to DB.',
                    'method': 'POST',
                    'endpoint': '/api/maintenance/ingest',
                    'delay': 2700.0,
                    'last': 0.0,
                    'status': 'not run'
                }, {
                    'name': 'Server Info',
                    'description': 'Gets server statistics.',
                    'method': 'POST',
                    'endpoint': '/api/maintenance/info',
                    'delay': 3600.0,
                    'last': 0.0,
                    'status': 'not run'
                }, {
                    'name': 'Reap Tokens',
                    'description': 'Removes expired tokens from DB.',
                    'method': 'DELETE',
                    'endpoint': '/api/maintenance/tokens',
                    'delay': 14400.0,
                    'last': 0.0,
                    'status': 'not run'
                }, {
                    'name': 'Rotate Logs',
                    'description': 'Removes old entries from log files.',
                    'method': 'DELETE',
                    'endpoint': '/api/maintenance/logs',
                    'delay': 86400.0,
                    'last': 0.0,
                    'status': 'not run'
                }, {
                    'name': 'Clear Temp Files',
                    'description': 'Removes old files from temp folder.',
                    'method': 'DELETE',
                    'endpoint': '/api/maintenance/temp',
                    'delay': 86400.0,
                    'last': 0.0,
                    'status': 'not run'
                }
            ],
            'children': []
        }
    ]


    def __init__(self):
        """Initialize."""

        self.logFileKey = 'db_log'

        self.setPaths()
        self.initDB()

        self.log(self.logFileKey, 'DB.__init__', 'started.')


        return
    def setPaths(self):
        """Set local paths."""

        self.paths = {
            'root': {
                'type': 'directory',
                'path': os.path.dirname(
                    os.path.realpath(__file__)
                )
            },
            'data': {
                'type': 'directory',
                'path': os.path.join(
                    os.path.dirname(
                        os.path.realpath(__file__)
                    ),
                    'data'
                )
            },
            'temp': {
                'type': 'directory',
                'path': os.path.join(
                    os.path.dirname(
                        os.path.realpath(__file__)
                    ),
                    'temp'
                )
            },
            'local': {
                'type': 'directory',
                'path': os.path.join(
                    os.path.dirname(
                        os.path.realpath(__file__)
                    ),
                    'local'
                )
            },

            'images': {
                'type': 'directory',
                'path': os.path.join(
                    os.path.dirname(
                        os.path.realpath(__file__)
                    ),
                    'images'
                )
            },
            'original': {
                'type': 'directory',
                'path': os.path.join(
                    os.path.dirname(
                        os.path.realpath(__file__)
                    ),
                    'images',
                    'original'
                )
            },
            'quantization': {
                'type': 'directory',
                'path': os.path.join(
                    os.path.dirname(
                        os.path.realpath(__file__)
                    ),
                    'images',
                    'quantization'
                )
            },
            'thumbnail': {
                'type': 'directory',
                'path': os.path.join(
                    os.path.dirname(
                        os.path.realpath(__file__)
                    ),
                    'images',
                    'thumbnail'
                )
            },

            'backend_log': {
                'type': 'log',
                'path': os.path.join(
                    os.path.dirname(
                        os.path.realpath(__file__)
                    ),
                    'data',
                    '.'.join(
                        [
                            '_'.join(
                                [
                                    os.path.dirname(
                                        os.path.realpath(__file__)
                                    ).rsplit(os.sep, 1)[-1],
                                    'Backend'
                                ]
                            ),
                            'log'
                        ]
                    )
                )
            },
            'server_log': {
                'type': 'log',
                'path': os.path.join(
                    os.path.dirname(
                        os.path.realpath(__file__)
                    ),
                    'data',
                    '.'.join(
                        [
                            '_'.join(
                                [
                                    os.path.dirname(
                                        os.path.realpath(__file__)
                                    ).rsplit(os.sep, 1)[-1],
                                    'Server'
                                ]
                            ),
                            'log'
                        ]
                    )
                )
            },
            'db_log': {
                'type': 'log',
                'path': os.path.join(
                    os.path.dirname(
                        os.path.realpath(__file__)
                    ),
                    'data',
                    '.'.join(
                        [
                            '_'.join(
                                [
                                    os.path.dirname(
                                        os.path.realpath(__file__)
                                    ).rsplit(os.sep, 1)[-1],
                                    'DB'
                                ]
                            ),
                            'log'
                        ]
                    )
                )
            },
            'display_log': {
                'type': 'log',
                'path': os.path.join(
                    os.path.dirname(
                        os.path.realpath(__file__)
                    ),
                    'data',
                    '.'.join(
                        [
                            '_'.join(
                                [
                                    os.path.dirname(
                                        os.path.realpath(__file__)
                                    ).rsplit(os.sep, 1)[-1],
                                    'Display'
                                ]
                            ),
                            'log'
                        ]
                    )
                )
            },
            'scissor_log': {
                'type': 'log',
                'path': os.path.join(
                    os.path.dirname(
                        os.path.realpath(__file__)
                    ),
                    'data',
                    '.'.join(
                        [
                            'Scissor',
                            'log'
                        ]
                    )
                )
            },
            'pencil_log': {
                'type': 'log',
                'path': os.path.join(
                    os.path.dirname(
                        os.path.realpath(__file__)
                    ),
                    'data',
                    '.'.join(
                        [
                            'Pencil',
                            'log'
                        ]
                    )
                )
            },

            'db': {
                'type': 'db',
                'path': os.path.join(
                    os.path.dirname(
                        os.path.realpath(__file__)
                    ),
                    'data',
                    'paper.db'
                )
            },
            'api_credentials': {
                'type': 'json',
                'path': os.path.join(
                    os.path.dirname(
                        os.path.realpath(__file__)
                    ),
                    'data',
                    'api_credentials.json'
                )
            }
        }


        for path in self.paths.keys():

            if self.paths[path]['type'] == 'directory':

                if os.path.exists(self.paths[path]['path']) == False:

                    try:

                        os.mkdir(self.paths[path]['path'])

                    except Exception as e:

                        print(
                            '.'.join(
                                [
                                    str(self.__class__.__name__),
                                    str(sys._getframe().f_code.co_name)
                                ]
                            ),
                            'Could not create required directory.',
                            str(e)
                        )
                        sys.exit(1)


        return
    def initDB(self):
        """Initialize database."""

        try:

            dbConnection = sqlite3.connect(
                self.paths['db']['path'],
                check_same_thread=False
            )
            dbCursor = dbConnection.cursor()


            activeTables = []

            dbCursor.execute(
                'SELECT name FROM sqlite_master WHERE type = \'table\';'
            )

            queryValues = dbCursor.fetchall()

            if isinstance(queryValues, list):

                for queryValue in queryValues:

                    if not queryValue is None:

                        activeTables.append(queryValue[0])


            for info in sorted(self.dbObjectInfo, key=lambda i: i['index']):

                if not info['table'] in activeTables:

                    dbCursor.execute(
                        info['queries']['create']
                    )

                    dbConnection.commit()


            if not 'settings' in activeTables:

                info = [
                    info
                    for info in self.dbObjectInfo
                    if info['type'] == 'settings'
                ][0]

                if info['defaults'][0]['cypher'] is None:

                    info['defaults'][0]['cypher'] = {}

                    info['defaults'][0]['cypher']['key'] = os.environ.get(
                        'PAPER_DB_KEY',
                        None
                    )
                    info['defaults'][0]['cypher']['salt'] = os.environ.get(
                        'PAPER_DB_SALT',
                        None
                    )

                    if info['defaults'][0]['cypher']['key'] is None:

                        info['defaults'][0]['cypher']['key'] = Fernet.generate_key().decode('utf-8')

                        os.environ['PAPER_DB_KEY'] = info['defaults'][0]['cypher']['key']

                    if info['defaults'][0]['cypher']['salt'] is None:

                        info['defaults'][0]['cypher']['salt'] = ''.join(
                            [
                                choice(
                                    'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789`~!@#$%^&*()-_=+,.<>/?|[];'
                                )
                                for c in range(64)
                            ]
                        )

                        os.environ['PAPER_DB_SALT'] = info['defaults'][0]['cypher']['salt']


                dbCursor.execute(
                    info['queries']['insert'] % {
                        'table': info['table'],
                        'columns': ', '.join(
                            [
                                column['key']
                                for column in sorted(info['columns'], key=lambda c: c['index'])
                            ]
                        ),
                        'value_placeholders': ', '.join(
                            [
                                '?'
                                for column in info['columns']
                            ]
                        )
                    },
                    tuple(
                        [
                            bytes(
                                json.dumps(
                                    info['defaults'][0][column['key']]
                                ),
                                'utf-8'
                            ) if column['data_info']['json'] == True else (
                                (
                                    '\'%(string)s\'' % {
                                        'string': (
                                            info['defaults'][0][column['key']]
                                        ) if column['data_info']['password'] == False else (
                                            self.cypherText(
                                                text=info['defaults'][0][column['key']],
                                                encrypt=True
                                            )
                                        )
                                    }
                                ) if isinstance(info['defaults'][0][column['key']], str) else (
                                    'NULL' if info['defaults'][0][column['key']] is None else str(info['defaults'][0][column['key']])
                                )
                            )
                            for column in sorted(info['columns'], key=lambda c: c['index'])
                        ]
                    )
                )

                dbConnection.commit()

                activeTables.append('settings')


            if not hasattr(self, 'settings'):

                self.settings = DbSettings(
                    self,
                    [
                        info
                        for info in self.dbObjectInfo
                        if info['type'] == 'settings'
                    ][0]
                )


            if not 'users' in activeTables:

                apiUserData = {
                    'id': 0,
                    'username': 'scissor_api',
                    'given_name': 'Scissor',
                    'family_name': 'API',
                    'password': ''.join(
                        [
                            choice(
                                'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789`~!@#$%^&*()-_=+,.<>?|[];'
                            )
                            for c in range(64)
                        ]
                    )
                }

                dbApiUser = self.new(
                    'user',
                    apiUserData
                )

                del dbApiUser
                del apiUserData

                info = [
                    info
                    for info in self.dbObjectInfo
                    if info['type'] == 'user'
                ][0]

                for default in info['defaults']:

                    dbUser = self.new(
                        'user',
                        default
                    )

                    del dbUser

                activeTables.append('users')


            for info in sorted(self.dbObjectInfo, key=lambda i: i['index']):

                if not info['table'] in activeTables:

                    for default in info['defaults']:

                        dbDefault = self.new(
                            info['type'],
                            default
                        )

                        del dbDefault


            if not dbCursor is None: dbCursor.close()
            if not dbConnection is None: dbConnection.close()

        except Exception as e:

            self.log(
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


    def get(self, dbObjectType, match=None):
        """Get DbObject(s) from DB."""

        dbResults = None

        try:

            for info in [i for i in self.dbObjectInfo if i['db_type'] == 'standard']:

                if info['type'] == dbObjectType:

                    dbConnection = sqlite3.connect(
                        self.paths['db']['path'],
                        check_same_thread=False
                    )
                    dbCursor = dbConnection.cursor()


                    dbCursor.execute(
                        (
                            info['queries']['select'] % {
                                'match': '' if match is None else (
                                    match if isinstance(match, str) else (
                                        ' WHERE ' + ' AND '.join(
                                            [
                                                '%(key)s = %(value)s' % {
                                                    'key': key,
                                                    'value': 'NULL' if match[key] is None else (
                                                        '\'%s\'' % (match[key], ) if isinstance(match[key], str) else str(match[key])
                                                    )
                                                }
                                                for key in match.keys()
                                            ]
                                        )
                                    )
                                )
                            }
                        ) if 'select' in info['queries'].keys() else (
                            'SELECT %(columns)s FROM %(table)s%(match)s;' % {
                                'table': info['table'],
                                'columns': ', '.join(
                                    [
                                        column['key']
                                        for column in sorted(info['columns'], key=lambda c: c['index'])
                                    ]
                                ),
                                'match': ' ' + info['queries']['default_sort'] if match is None else (
                                    match if isinstance(match, str) else (
                                        ' WHERE ' + ' AND '.join(
                                            [
                                                '%(key)s = %(value)s' % {
                                                    'key': key,
                                                    'value': 'NULL' if match[key] is None else (
                                                        '\'%s\'' % (match[key], ) if isinstance(match[key], str) else str(match[key])
                                                    )
                                                }
                                                for key in match.keys()
                                            ]
                                        )
                                    )
                                )
                            }
                        )
                    )

                    rawResults = [
                        dict(
                            [
                                (
                                    sorted(info['columns'], key=lambda c: c['index'])[column]['key'],
                                    rawResult[column]
                                )
                                for column in range(len(info['columns']))
                            ]
                        )
                        for rawResult in dbCursor.fetchall()
                    ]

                    if not dbCursor is None: dbCursor.close()
                    if not dbConnection is None: dbConnection.close()


                    if len(rawResults) > 0:

                        ObjectClass = globals()[info['db_object']]
                        objectResults = []

                        for r in range(len(rawResults)):

                            for child in info['children']:

                                rawResults[r][child['key']] = self.get(
                                    child['type'],
                                    match=' WHERE %(key)s = %(value)s' % {
                                        'key': child['foreign_key'],
                                        'value': (
                                            '\'%s\'' % (
                                                rawResults[r][child['local_key']], 
                                            )
                                        ) if isinstance(rawResults[r][child['local_key']], str) else str(rawResults[r][child['local_key']])
                                    }
                                )

                                if child['relationship'] in ['one_to_many', 'many_to_many']:

                                    if not isinstance(rawResults[r][child['key']], list):
                                        
                                        if rawResults[r][child['key']] is None:

                                            rawResults[r][child['key']] = []
                                            
                                        else:
                                            
                                            rawResults[r][child['key']] = [rawResults[r][child['key']]]


                            objectResult = ObjectClass(
                                self,
                                info
                            )
                            objectResult.new(
                                rawResults[r],
                                fromDb=True
                            )

                            objectResults.append(
                                objectResult
                            )

                        dbResults = objectResults[0] if len(objectResults) == 1 else objectResults


                    break

        except Exception as e:

            self.log(
                self.logFileKey,
                '.'.join(
                    [
                        str(self.__class__.__name__),
                        str(sys._getframe().f_code.co_name)
                    ]
                ),
                ' '.join(
                    [
                        str(dbObjectType),
                        str(match),
                        str(e)
                    ]
                )
            )


        return dbResults
    def new(self, dbObjectType, objectValues):
        """Creates new DbObject(s) in DB."""

        dbResult = None

        try:

            if isinstance(objectValues, dict):

                for info in [i for i in self.dbObjectInfo if i['db_type'] == 'standard']:

                    if info['type'] == dbObjectType:

                        ObjectClass = globals()[info['db_object']]


                        objectResult = ObjectClass(
                            self,
                            info
                        )
                        objectResult.new(
                            objectValues=objectValues,
                            fromDb=False
                        )

                        dbResult = objectResult

                        break

        except Exception as e:

            self.log(
                self.logFileKey,
                '.'.join(
                    [
                        str(self.__class__.__name__),
                        str(sys._getframe().f_code.co_name)
                    ]
                ),
                str(e)
            )


        return dbResult
    def delete(self, dbObjectType, match=None, children=True):
        """Deletes DbObject(s) from DB."""

        try:

            if not match is None:

                dbResults = self.get(
                    dbObjectType=dbObjectType,
                    match=match
                )

                if not dbResults is None:

                    if not isinstance(dbResults, list):

                        dbResults = [dbResults]

                    for dbResult in dbResults:

                        dbResult.delete(
                            children=children,
                            parentCursor=None
                        )

        except Exception as e:

            self.log(
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


    def cypherText(self, text, encrypt=True):
        """Text encrypt/decrypt."""

        result = None

        try:

            if isinstance(text, str):

                if len(text) > 0:

                    cypherSettings = self.settings.get('cypher')


                    cypher = Fernet(
                        bytes(
                            cypherSettings['key'],
                            encoding='utf-8'
                        )
                    )

                    if encrypt == True:

                        result = cypher.encrypt(
                            bytes(
                                str(text + cypherSettings['salt']),
                                encoding='utf-8'
                            )
                        ).decode('utf-8')

                    else:

                        result = cypher.decrypt(
                            bytes(
                                text,
                                encoding='utf-8'
                            )
                        ).decode('utf-8')[:-len(cypherSettings['salt'])]

                else:

                    raise DbValueException('Invalid text.')

            else:

                raise DbValueException('Invalid text.')

        except Exception as e:

            self.log(
                self.logFileKey,
                '.'.join(
                    [
                        str(self.__class__.__name__),
                        str(sys._getframe().f_code.co_name)
                    ]
                ),
                str(e)
            )


        return result
    def getPasswordRegex(self):
        """Gets password regex based on current password settings."""

        passwordRegex = r''

        try:

            passwordSettings = self.settings.get('password')


            passwordRegexOptions = {
                'template': r'^%(upper)s%(lower)s%(number)s%(special)s.{%(length)i,}$',
                'upper': r'(?=.*?[A-Z])', 
                'lower': r'(?=.*?[a-z])',
                'number': r'(?=.*?[0-9])',
                'special': r'(?=.*?[^A-Za-z0-9])'
            }

            passwordRegex = passwordRegexOptions['template'] % {
                'upper': passwordRegexOptions['upper'] if passwordSettings['upper'] == True else r'',
                'lower': passwordRegexOptions['lower'] if passwordSettings['lower'] == True else r'',
                'number': passwordRegexOptions['number'] if passwordSettings['number'] == True else r'',
                'special': passwordRegexOptions['special'] if passwordSettings['special'] == True else r'',
                'length': passwordSettings['length']
            }

        except Exception as e:

            self.log(
                self.logFileKey,
                '.'.join(
                    [
                        str(self.__class__.__name__),
                        str(sys._getframe().f_code.co_name)
                    ]
                ),
                str(e)
            )


        return passwordRegex


    def log(self, logFileKey, source, status):
        """Write log."""

        try:

            with open(self.paths[logFileKey]['path'], 'a', encoding='utf-8') as f:

                f.write(
                    '%s | %s : %s\n' % (
                        str(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S.%f'))[0:-3],
                        source,
                        status.replace('\r', '').replace('\n', '\\n')
                    )
                )

        except:

            print(
                'Could not open',
                logFileKey,
                source,
                status
            )


        return


class DbValueException(Exception): pass


class DbObjectBase:
    def __init__(self, db, info):
        """Initialize."""

        self.db = db
        self.info = info
        self.exists = False


        return


class DbObjectConfig(DbObjectBase):
    def get(self, key):
        """Get single value."""

        setting = None

        try:

            if key in [column['key'] for column in self.info['columns']]:

                dbConnection = sqlite3.connect(
                    self.db.paths['db']['path'],
                    check_same_thread=False
                )
                dbCursor = dbConnection.cursor()


                dbCursor.execute(
                    'SELECT %(column)s FROM %(table)s WHERE id = 0;' % {
                        'table': self.info['table'],
                        'column': key
                    }
                )


                blobResult = dbCursor.fetchone()

                if not blobResult is None:

                    if len(blobResult) > 0:

                        setting = json.loads(
                            blobResult[0].decode('utf-8')
                        )


                if not dbCursor is None: dbCursor.close()
                if not dbConnection is None: dbConnection.close()

            else:

                raise DbValueException('Key not found.')

        except Exception as e:

            self.db.log(
                self.db.logFileKey,
                '.'.join(
                    [
                        str(self.__class__.__name__),
                        str(sys._getframe().f_code.co_name)
                    ]
                ),
                str(e)
            )


        return setting
    def set(self, key, value):
        """Sets single value."""

        try:

            if key in [column['key'] for column in self.info['columns']]:

                dbConnection = sqlite3.connect(
                    self.db.paths['db']['path'],
                    check_same_thread=False
                )
                dbCursor = dbConnection.cursor()


                dbCursor.execute(
                    'UPDATE %(table)s SET %(column)s = ? WHERE id = 0;' % {
                        'table': self.info['table'],
                        'column': key
                    },
                    (
                        bytes(
                            json.dumps(
                                value
                            ),
                            'utf-8'
                        ),
                    )
                )


                dbConnection.commit()


                if not dbCursor is None: dbCursor.close()
                if not dbConnection is None: dbConnection.close()

            else:

                raise DbValueException('Key not found.')

        except Exception as e:

            self.db.log(
                self.db.logFileKey,
                '.'.join(
                    [
                        str(self.__class__.__name__),
                        str(sys._getframe().f_code.co_name)
                    ]
                ),
                str(e)
            )


        return

class DbSettings(DbObjectConfig):
    def generateMediaQueue(self, currentId=None):
        """Generates new media queue."""

        try:

            imageSettings = self.get('image')


            images = self.db.get(
                dbObjectType='image',
                match=None
            )

            filteredImageIds = []

            if isinstance(images, list):

                if len(images) > 0:

                    filteredImageIds = [
                        image.working['id']
                        for image in images
                        if image.available(imageSettings['filters']) == True
                    ]


                    imageSettings['queue'] = []

                    for x in range(3):

                        temp = filteredImageIds.copy()

                        for c in range(len(filteredImageIds)):

                            index = choice(
                                range(
                                    len(temp)
                                )
                            )
                            imageSettings['queue'].append(
                                temp[index]
                            )
                            temp.pop(index)


                    if not currentId is None:

                        if currentId in imageSettings['queue']:

                            for i in range(imageSettings['queue'].index(currentId) + 1):

                                imageSettings['queue'].append(
                                    imageSettings['queue'].pop(0)
                                )

                        else:

                            raise DbValueException('Specified image id unavailable.')

                    imageSettings['current'] = imageSettings['queue'][-1]


                    self.set(
                        'image',
                        imageSettings
                    )

        except Exception as e:

            self.db.log(
                self.db.logFileKey,
                '.'.join(
                    [
                        str(self.__class__.__name__),
                        str(sys._getframe().f_code.co_name)
                    ]
                ),
                str(e)
            )


        return
    def rotateMediaQueue(self, forward=True):
        """Rotates media queue and changes current."""

        try:

            imageSettings = self.get('image')


            if len(imageSettings['queue']) == 0:

                self.generateMediaQueue()
                imageSettings = self.get('image')


            if forward == True:

                if len(imageSettings['queue']) > 0:

                    nextMedia = imageSettings['queue'].pop(0)

                    imageSettings['queue'].append(
                        nextMedia
                    )
                    imageSettings['current'] = nextMedia

            else:

                if len(imageSettings['queue']) > 0:

                    displaying = imageSettings['queue'].pop(-1)

                    imageSettings['queue'].insert(
                        0,
                        displaying
                    )
                    imageSettings['current'] = imageSettings['queue'][-1]


            self.set(
                'image',
                imageSettings
            )

        except Exception as e:

            self.db.log(
                self.db.logFileKey,
                '.'.join(
                    [
                        str(self.__class__.__name__),
                        str(sys._getframe().f_code.co_name)
                    ]
                ),
                str(e)
            )


        return


class DbObjectStandard(DbObjectBase):
    def new(self, objectValues, fromDb=True):
        """Creates new object instance."""

        if fromDb == True:
 
            if not hasattr(self, 'working'):

                self.working = {}

            if not hasattr(self, 'raw'):

                self.raw = objectValues

            else:

                for key in objectValues.keys():

                    self.raw[key] = objectValues[key]

        else:

            if not hasattr(self, 'raw'):

                self.raw = {}

            if not hasattr(self, 'working'):

                self.working = objectValues

            else:

                for key in objectValues.keys():

                    self.working[key] = objectValues[key]


        try:

            if isinstance(objectValues, dict):

                for column in sorted(self.info['columns'], key=lambda c: c['index']):

                    validated = None

                    if column['key'] in objectValues.keys():

                        validated = self.validate(
                            objectValues[column['key']],
                            column['data_info'],
                            fromDb=fromDb
                        )

                    else:

                        validated = self.validate(
                            None,
                            column['data_info'],
                            fromDb=fromDb
                        )

                    if not validated is None:

                        if validated['valid'] == True:

                            self.working[column['key']] = validated['working']
                            self.raw[column['key']] = validated['raw']

                        else:

                            raise DbValueException('Validation error.')

                    else:

                        raise DbValueException('Validation error.')


                for child in self.info['children']:

                    if child['key'] in objectValues.keys():

                        self.working[child['key']] = objectValues[child['key']]

                    else:

                        if child['relationship'] in ['one_to_many', 'many_to_many']:

                            self.working[child['key']] = []

                        else:

                            self.working[child['key']] = None
                            

                if fromDb == True:
                    
                    self.exists = True
                    self.stored = self.raw.copy()
                    
                else:
                    
                    self.save()

            else:

                raise DbValueException('Invalid object values.')

        except Exception as e:

            self.db.log(
                self.db.logFileKey,
                '.'.join(
                    [
                        str(self.__class__.__name__),
                        str(sys._getframe().f_code.co_name)
                    ]
                ),
                str(e)
            )


        return
    def save(self, children=True, parentConnection=None, parentCursor=None):
        """Saves object to DB."""

        try:

            workingValidation = [
                {
                    'key': column['key'],
                    'result': self.validate(
                        self.working[column['key']],
                        column['data_info'],
                        fromDb=False
                    )
                }
                for column in sorted(self.info['columns'], key=lambda c: c['index'])
            ]

            if all([validation['result']['valid'] for validation in workingValidation]) == True:

                self.raw = dict(
                    [
                        (
                            validation['key'],
                            validation['result']['raw']
                        )
                        for validation in workingValidation
                    ]
                )

                self.working = dict(
                    [
                        (
                            validation['key'],
                            validation['result']['working']
                        )
                        for validation in workingValidation
                    ]
                )


                if children == True:

                    for childKey in [child['key'] for child in self.info['children'] if child['modify_first'] == True]:

                        if childKey in self.working.keys():

                            if not self.working[childKey] is None:

                                if isinstance(self.working[childKey], list):

                                    for child in self.working[childKey]:

                                        child.save(
                                            children=children,
                                            parentConnection=parentConnection,
                                            parentCursor=parentCursor
                                        )

                                else:

                                    self.working[childKey].save(
                                        children=children,
                                        parentConnection=parentConnection,
                                        parentCursor=parentCursor
                                    )


                dbConnection = None
                dbCursor = None

                if (not parentConnection is None) and (not parentCursor is None):

                    dbConnection = parentConnection
                    dbCursor = parentCursor

                else:

                    dbConnection = sqlite3.connect(
                        self.db.paths['db']['path'],
                        check_same_thread=False
                    )
                    dbCursor = dbConnection.cursor()


                if self.exists == True:

                    matchKeys = [
                        column['key']
                        for column in self.info['columns']
                        if column['data_info']['primary_key'] == True
                    ]

                    if len(matchKeys) > 0:

                        dbCursor.execute(
                            'UPDATE %(table)s SET %(column_value)s WHERE %(match)s;' % {
                                'table': self.info['table'],
                                'column_value': ', '.join(
                                    [
                                        column['key'] + ' = ?'
                                        for column in sorted(self.info['columns'], key=lambda c: c['index'])
                                        if not column['key'] in matchKeys
                                    ]
                                ),
                                'match': ', '.join(
                                    [
                                        '%(key)s = %(value)s' % {
                                            'key': matchKey,
                                            'value': (
                                                '\'%s\'' % (self.raw[matchKey], )
                                            ) if isinstance(self.raw[matchKey], str) else self.raw[matchKey]
                                        }
                                        for matchKey in matchKeys
                                    ]
                                )
                            },
                            tuple(
                                [
                                    self.raw[column['key']]
                                    for column in sorted(self.info['columns'], key=lambda c: c['index'])
                                    if not column['key'] in matchKeys
                                ]
                            )
                        )

                else:

                    dbCursor.execute(
                        'INSERT OR REPLACE INTO %(table)s (%(columns)s) VALUES (%(values)s);' % {
                            'table': self.info['table'],
                            'columns': ', '.join(
                                [
                                    column['key']
                                    for column in sorted(self.info['columns'], key=lambda c: c['index'])
                                ]
                            ),
                            'values': ', '.join(
                                [
                                    '?'
                                    for column in self.info['columns']
                                ]
                            )
                        },
                        tuple(
                            [
                                self.raw[column['key']]
                                for column in sorted(self.info['columns'], key=lambda c: c['index'])
                            ]
                        )
                    )


                dbConnection.commit()


                if children == True:

                    for childKey in [child['key'] for child in self.info['children'] if child['modify_first'] == False]:

                        if childKey in self.working.keys():

                            if not self.working[childKey] is None:

                                if isinstance(self.working[childKey], list):

                                    for child in self.working[childKey]:

                                        child.save(
                                            children=children,
                                            parentConnection=parentConnection,
                                            parentCursor=parentCursor
                                        )

                                else:

                                    self.working[childKey].save(
                                        children=children,
                                        parentConnection=parentConnection,
                                        parentCursor=parentCursor
                                    )


                if (not parentConnection is None) and (not parentCursor is None):

                    if not dbCursor is None: dbCursor.close()
                    if not dbConnection is None: dbConnection.close()


                self.exists = True
                self.stored = self.raw.copy()

            else:

                raise DbValueException('Invalid data.')

        except Exception as e:

            self.db.log(
                self.db.logFileKey,
                '.'.join(
                    [
                        str(self.__class__.__name__),
                        str(sys._getframe().f_code.co_name)
                    ]
                ),
                str(e)
            )


        return
    def delete(self, children=True, parentConnection=None, parentCursor=None):
        """Deletes object from DB."""

        try:

            if self.exists == True:

                if children == True:

                    for childKey in [child['key'] for child in self.info['children'] if child['modify_first'] == True]:

                        if childKey in self.working.keys():

                            if not self.working[childKey] is None:

                                if isinstance(self.working[childKey], list):

                                    for child in self.working[childKey]:

                                        child.delete(
                                            children=children,
                                            parentConnection=parentConnection,
                                            parentCursor=parentCursor
                                        )

                                else:

                                    self.working[childKey].delete(
                                        children=children,
                                        parentConnection=parentConnection,
                                        parentCursor=parentCursor
                                    )


                dbConnection = None
                dbCursor = None

                if (not parentConnection is None) and (not parentCursor is None):

                    dbConnection = parentConnection
                    dbCursor = parentCursor

                else:

                    dbConnection = sqlite3.connect(
                        self.db.paths['db']['path'],
                        check_same_thread=False
                    )
                    dbCursor = dbConnection.cursor()


                dbCursor.execute(
                    'DELETE FROM %(table)s WHERE %(match)s' % {
                        'table': self.info['table'],
                        'match': ' AND '.join(
                            [
                                '%(key)s = %(value)s' % {
                                    'key': key,
                                    'value': 'NULL' if self.stored[key] is None else (
                                        '\'%s\'' % (self.stored[key], ) if isinstance(self.stored[key], str) else str(self.stored[key])
                                    )
                                }
                                for key in self.stored.keys()
                                if key in [column['key'] for column in self.info['columns']]
                            ]
                        )
                    }
                )


                dbConnection.commit()


                if children == True:

                    for childKey in [child['key'] for child in self.info['children'] if child['modify_first'] == False]:

                        if childKey in self.working.keys():

                            if not self.working[childKey] is None:

                                if isinstance(self.working[childKey], list):

                                    for child in self.working[childKey]:

                                        child.delete(
                                            children=children,
                                            parentConnection=parentConnection,
                                            parentCursor=parentCursor
                                        )

                                else:

                                    self.working[childKey].delete(
                                        children=children,
                                        parentConnection=parentConnection,
                                        parentCursor=parentCursor
                                    )


                if (not parentConnection is None) and (not parentCursor is None):

                    if not dbCursor is None: dbCursor.close()
                    if not dbConnection is None: dbConnection.close()


                self.exists = False
                self.working = {}
                self.raw = {}
                self.stored = {}

        except Exception as e:

            self.db.log(
                self.db.logFileKey,
                '.'.join(
                    [
                        str(self.__class__.__name__),
                        str(sys._getframe().f_code.co_name)
                    ]
                ),
                str(e)
            )


        return

    def validate(self, value, dataInfo, fromDb=True):
        """Validates and converts value."""

        # This is ugly and I hate it, but it works

        validation = {
            'valid': False,
            'raw': value if fromDb == True else None,
            'working': None if fromDb == True else value
        }

        try:

            if dataInfo['storage_type'] == 'INTEGER':

                if value is None:

                    if dataInfo['not_null'] == True:

                        if 'default' in dataInfo.keys():

                            validation['valid'] = True
                            validation['raw'] = dataInfo['default']

                            if dataInfo['boolean'] == True:

                                validation['working'] = True if validation['raw'] == 1 else False

                            else:

                                validation['working'] = value

                        else:

                            if not dataInfo['unique_generator'] is None:

                                uniqueGenerator = getattr(self, dataInfo['unique_generator'])

                                validation['valid'] = True
                                validation['raw'] = uniqueGenerator(**dataInfo['unique_generator_args']) if 'unique_generator_args' in dataInfo.keys() else uniqueGenerator()
                                validation['working'] = validation['raw']

                            else:

                                raise DbValueException('Invalid data type.')

                else:

                    if fromDb == True:

                        if isinstance(value, int):

                            validation['valid'] = True
                            validation['raw'] = value

                            if dataInfo['boolean'] == True:

                                validation['working'] = True if validation['raw'] == 1 else False

                            else:

                                validation['working'] = value

                        else:

                            raise DbValueException('Invalid data type.')

                    else:

                        if isinstance(value, int):

                            validation['valid'] = True
                            validation['raw'] = value
                            validation['working'] = value

                        elif isinstance(value, bool):

                            if dataInfo['boolean'] == True:

                                validation['valid'] = True
                                validation['working'] = value
                                validation['raw'] = 1 if value == True else False

                            else:

                                raise DbValueException('Invalid data type.')

                        else:

                            raise DbValueException('Invalid data type.')


            elif dataInfo['storage_type'] == 'TEXT':

                if value is None:

                    if dataInfo['not_null'] == True:

                        if 'default' in dataInfo.keys():

                            validation['valid'] = True
                            validation['raw'] = dataInfo['default']
                            validation['working'] = dataInfo['default']

                        else:

                            raise DbValueException('Invalid data type.')

                    else:

                        raise DbValueException('Invalid data type.')

                else:

                    if isinstance(value, str):

                        validation['valid'] = True

                        if dataInfo['password'] == True:

                            validation['raw'] = value if fromDb == True else self.db.cypherText(
                                value,
                                encrypt=True
                            )
                            validation['working'] = value if fromDb == False else self.db.cypherText(
                                value,
                                encrypt=False
                            )

                            validation['valid'] = self.validatePassword(
                                validation['working']
                            )

                        elif dataInfo['json'] == True:

                            validation['raw'] = value if fromDb == True else json.dumps(value)
                            validation['working'] = value if fromDb == False else json.loads(value)

                        else:

                            validation['raw'] = value
                            validation['working'] = value

                    else:

                        raise DbValueException('Invalid data type.')


            elif dataInfo['storage_type'] == 'NUMERIC':

                if isinstance(value, int) or isinstance(value, float):

                    validation['valid'] = True
                    validation['raw'] = value
                    validation['working'] = value

                else:

                    if dataInfo['not_null'] == True:

                        raise DbValueException('Invalid data type.')

                    else:

                        if value is None:

                            validation['valid'] = True
                            validation['raw'] = value
                            validation['working'] = value

                        else:

                            raise DbValueException('Invalid data type.')


            elif dataInfo['storage_type'] == 'REAL':

                if isinstance(value, int) or isinstance(value, float):

                    validation['valid'] = True
                    validation['raw'] = value
                    validation['working'] = value

                else:

                    if dataInfo['not_null'] == True:

                        raise DbValueException('Invalid data type.')

                    else:

                        if value is None:

                            validation['valid'] = True
                            validation['raw'] = value
                            validation['working'] = value

                        else:

                            raise DbValueException('Invalid data type.')


            elif dataInfo['storage_type'] == 'BLOB':

                validation['valid'] = True

                if dataInfo['json'] == True:

                    validation['raw'] = value if fromDb == True else (
                        bytes(
                            json.dumps(
                                value
                            ),
                            'utf-8'
                        )
                    )
                    validation['working'] = value if fromDb == False else (
                        json.loads(
                            value.decode('utf-8')
                        )
                    )

                else:

                    validation['raw'] = value if fromDb == True else (
                        bytes(
                            value,
                            'utf-8'
                        )
                    )
                    validation['working'] = value if fromDb == False else (
                        value.decode('utf-8')
                    )


            if validation['valid'] == True and dataInfo['unique'] == True and dataInfo['unique_generator'] is None:

                if not validation['raw'] is None:

                    unique = self.validateUnique(
                        table=dataInfo['unique_validation']['table'],
                        key=dataInfo['unique_validation']['key'],
                        value=validation['raw']
                    )

                    if unique == False:

                        raise DbValueException('Duplicate value.')

                else:

                    raise DbValueException('Null distinct value.')

        except Exception as e:

            validation['valid'] = False
            self.db.log(
                self.db.logFileKey,
                '.'.join(
                    [
                        str(self.__class__.__name__),
                        str(sys._getframe().f_code.co_name)
                    ]
                ),
                str(e)
            )


        return validation
    def validateUnique(self, table, key, value):
        """Checks if non-null value is unique."""

        isUnique = False

        try:

            dbConnection = sqlite3.connect(
                self.db.paths['db']['path'],
                check_same_thread=False
            )
            dbCursor = dbConnection.cursor()


            dbCursor.execute(
                'SELECT %(key)s FROM %(table)s WHERE %(key)s = ?;' % {
                    'key': key,
                    'table': table
                },
                (
                    value if isinstance(value, bytes) else (
                        'NULL' if value is None else (
                            '\'%s\'' % (value, ) if isinstance(value, str) else str(value)
                        )
                    ),
                )
            )


            activeValues = [
                queryValue[0]
                for queryValue in dbCursor.fetchall()
            ]

            if activeValues is None:

                isUnique = True

            if len(activeValues) == 0:

                isUnique = True


            if not dbCursor is None: dbCursor.close()
            if not dbConnection is None: dbConnection.close()

        except Exception as e:

            self.db.log(
                self.db.logFileKey,
                '.'.join(
                    [
                        str(self.__class__.__name__),
                        str(sys._getframe().f_code.co_name)
                    ]
                ),
                str(e)
            )


        return isUnique
    def validatePassword(self, password):
        """Checks if password meets requirements."""

        isValid = False

        try:

            passwordMatch = re.match(
                self.db.getPasswordRegex(),
                password
            )

            if not passwordMatch is None:

                isValid = True

        except Exception as e:

            self.db.log(
                self.db.logFileKey,
                '.'.join(
                    [
                        str(self.__class__.__name__),
                        str(sys._getframe().f_code.co_name)
                    ]
                ),
                str(e)
            )


        return isValid

    def generateUniqueInt(self, key, table):
        """Gets next available integer for table/key."""

        uniqueInt = None

        try:

            dbConnection = sqlite3.connect(
                self.db.paths['db']['path'],
                check_same_thread=False
            )
            dbCursor = dbConnection.cursor()


            dbCursor.execute(
                'SELECT %(key)s FROM %(table)s;' % {
                    'key': str(key),
                    'table': str(table)
                }
            )


            activeInts = [
                queryValue[0]
                for queryValue in dbCursor.fetchall()
            ]


            if not dbCursor is None: dbCursor.close()
            if not dbConnection is None: dbConnection.close()


            for i in range(sys.maxsize):

                if not i in activeInts:

                    uniqueInt = i

                    break

        except Exception as e:

            self.db.log(
                self.db.logFileKey,
                '.'.join(
                    [
                        str(self.__class__.__name__),
                        str(sys._getframe().f_code.co_name)
                    ]
                ),
                str(e)
            )


        return uniqueInt
    def generateTimestamp(self, addSeconds=0.0):
        """Generates epoch timestamp and adjusts if specified."""

        timestamp = (datetime.datetime.now() - datetime.datetime.fromtimestamp(0)).total_seconds()

        if isinstance(addSeconds, int) or isinstance(addSeconds, float):

            timestamp = timestamp + addSeconds


        return timestamp

    def getApiFormat(self):
        """Returns simplified dictionary of object's data, including children."""

        apiFormat = {}

        try:

            if hasattr(self, 'working'):

                apiTemp = dict(
                    [
                        (
                            column['key'],
                            self.working[column['key']]
                        )
                        for column in sorted(self.info['columns'], key=lambda c: c['index'])
                        if column['key'] in self.working.keys() and column['data_info']['api'] == True
                    ]
                )

                for column in sorted(self.info['columns'], key=lambda c: c['index']):

                    if column['key'] in apiTemp.keys() and column['data_info']['date'] == True:

                        if isinstance(apiTemp[column['key']], int | float):

                            apiTemp[column['key'] + '_date_formatted'] = str(datetime.datetime.fromtimestamp(apiTemp[column['key']]).strftime('%Y/%m/%d %H:%M:%S.%f'))[0:-3]

                for child in self.info['children']:

                    if child['key'] in self.working.keys():

                        if not self.working[child['key']] is None:

                            if isinstance(self.working[child['key']], list):

                                apiTemp[child['key']] = [
                                    childObject.getApiFormat()
                                    for childObject in self.working[child['key']]
                                ]

                            else:

                                apiTemp[child['key']] = self.working[child['key']].getApiFormat()

                apiFormat = apiTemp

        except Exception as e:

            self.db.log(
                self.db.logFileKey,
                '.'.join(
                    [
                        str(self.__class__.__name__),
                        str(sys._getframe().f_code.co_name)
                    ]
                ),
                str(e)
            )


        return apiFormat


class DbUser(DbObjectStandard): pass
class DbPermission(DbObjectStandard): pass
class DbUserPermission(DbObjectStandard): pass
class DbToken(DbObjectStandard):
    def new(self, objectValues, fromDb=True):
        """Overload to add timestamp with adjustment."""

        try:

            if isinstance(objectValues, dict):

                if fromDb == False:

                    tokenSettings = self.db.settings.get('token')

                    objectValues['token'] = self.generateUniqueToken(
                        'token',
                        'tokens'
                    )
                    objectValues['expires'] = self.generateTimestamp(
                        addSeconds=tokenSettings['duration']
                    )

        except Exception as e:

            self.db.log(
                self.db.logFileKey,
                '.'.join(
                    [
                        str(self.__class__.__name__),
                        str(sys._getframe().f_code.co_name)
                    ]
                ),
                str(e)
            )


        return super(DbToken, self).new(objectValues, fromDb)
    def generateUniqueToken(self, key, table):
        """Generate unique token for table/key."""

        uniqueToken = None

        try:

            tokenSettings = self.db.settings.get('token')


            dbConnection = sqlite3.connect(
                self.db.paths['db']['path'],
                check_same_thread=False
            )
            dbCursor = dbConnection.cursor()

            dbCursor.execute(
                'SELECT %(key)s FROM %(table)s;' % {
                    'key': str(key),
                    'table': str(table)
                }
            )

            activeTokens = [
                queryValue[0]
                for queryValue in dbCursor.fetchall()
            ]


            if not dbCursor is None: dbCursor.close()
            if not dbConnection is None: dbConnection.close()


            for i in range(sys.maxsize):

                testToken = ''.join(
                    [
                        choice(
                            tokenSettings['choices']
                        )
                        for c in range(tokenSettings['length'])
                    ]
                )

                if not testToken in activeTokens:

                    uniqueToken = testToken

                    break

        except Exception as e:

            self.db.log(
                self.db.logFileKey,
                '.'.join(
                    [
                        str(self.__class__.__name__),
                        str(sys._getframe().f_code.co_name)
                    ]
                ),
                str(e)
            )


        return uniqueToken


class DbObjectFile(DbObjectStandard):
    def delete(self, children=True, parentConnection=None, parentCursor=None):
        """Deletes file."""

        try:

            if self.exists == True:

                if hasattr(self, 'working'):

                    if 'path' in self.working.keys():

                        if os.path.exists(self.working['path']):

                            if os.path.isfile(self.working['path']):

                                os.remove(self.working['path'])

        except Exception as e:

            self.db.log(
                self.db.logFileKey,
                '.'.join(
                    [
                        str(self.__class__.__name__),
                        str(sys._getframe().f_code.co_name)
                    ]
                ),
                str(e)
            )


        return super(DbObjectFile, self).delete(children, parentConnection, parentCursor)

class DbImage(DbObjectFile):
    def new(self, objectValues, fromDb=True):
        """Overload to add timestamp."""

        try:

            if isinstance(objectValues, dict):

                if fromDb == False:

                    objectValues['ingested'] = self.generateTimestamp(
                        addSeconds=0.0
                    )

        except Exception as e:

            self.db.log(
                self.db.logFileKey,
                '.'.join(
                    [
                        str(self.__class__.__name__),
                        str(sys._getframe().f_code.co_name)
                    ]
                ),
                str(e)
            )


        return super(DbImage, self).new(objectValues, fromDb)
    def getFlattenedTags(self):
        """Provides concise, readable image child tags."""

        flattened = []

        try:

            if hasattr(self, 'working'):

                if 'tags' in self.working.keys():

                    for tag in self.working['tags']:

                        flattened.append(
                            tag.getFlattened()
                        )

        except Exception as e:

            self.db.log(
                self.db.logFileKey,
                '.'.join(
                    [
                        str(self.__class__.__name__),
                        str(sys._getframe().f_code.co_name)
                    ]
                ),
                str(e)
            )


        return flattened
    def available(self, filters=None):
        """Checks images tags against filters."""

        isAvailable = False

        try:

            if filters is None:

                filters = self.db.settings.get('image')['filters']

            if len(filters) == 0:

                isAvailable = True

            else:

                flattenedTags = self.getFlattenedTags()


                for includeFilter in [f for f in filters if f['type'] == 'include']:

                    for flattenedTag in flattenedTags:

                        if flattenedTag['category']['id'] == includeFilter['category']['id']:

                            if 'subcategory' in includeFilter.keys():

                                if flattenedTag['subcategory']['id'] == includeFilter['subcategory']['id']:

                                    isAvailable = True

                            else:

                                isAvailable = True


                for excludeFilter in [f for f in filters if f['type'] == 'include']:

                    for flattenedTag in flattenedTags:

                        if flattenedTag['category']['id'] == excludeFilter['category']['id']:

                            if 'subcategory' in excludeFilter.keys():

                                if flattenedTag['subcategory']['id'] == excludeFilter['subcategory']['id']:

                                    isAvailable = False

                            else:

                                isAvailable = False

        except Exception as e:

            self.db.log(
                self.db.logFileKey,
                '.'.join(
                    [
                        str(self.__class__.__name__),
                        str(sys._getframe().f_code.co_name)
                    ]
                ),
                str(e)
            )


        return isAvailable
class DbQuantization(DbObjectFile): pass
class DbThumbnail(DbObjectFile): pass


class DbCategory(DbObjectStandard): pass
class DbSubcategory(DbObjectStandard): pass
class DbTag(DbObjectStandard):
    def new(self, objectValues, fromDb=True):
        """Adds referenced objects."""

        super(DbTag, self).new(objectValues, fromDb)

        try:

            for referenceKey in ['category', 'subcategory']:

                self.working[referenceKey] = self.db.get(
                    dbObjectType=referenceKey,
                    match={
                        'id': self.working[referenceKey + '_id']
                    }
                )

        except Exception as e:

            self.db.log(
                self.db.logFileKey,
                '.'.join(
                    [
                        str(self.__class__.__name__),
                        str(sys._getframe().f_code.co_name)
                    ]
                ),
                str(e)
            )


        return
    def getApiFormat(self):
        """Override to include references."""

        apiFormat = self.getFlattened()


        return apiFormat
    def getFlattened(self):
        """Provides concise, readable references."""

        flattened = {}

        try:

            if hasattr(self, 'working'):

                flattened['image_id'] = self.working['image_id'] if 'image_id' in self.working.keys() else None

                for childKey in ['category', 'subcategory']:

                    if childKey in self.working.keys():

                        flattened[childKey] = {
                            'id': self.working[childKey].working['id'] if isinstance(self.working[childKey], DbObjectStandard) else None,
                            'name': self.working[childKey].working['name'] if isinstance(self.working[childKey], DbObjectStandard) else None
                        }

        except Exception as e:

            self.db.log(
                self.db.logFileKey,
                '.'.join(
                    [
                        str(self.__class__.__name__),
                        str(sys._getframe().f_code.co_name)
                    ]
                ),
                str(e)
            )


        return flattened

class DbInfo(DbObjectStandard): pass
class DbTask(DbObjectStandard): pass
