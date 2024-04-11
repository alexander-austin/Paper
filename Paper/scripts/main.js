/*
    Copyright (c) 2024, Alexander Austin
    All rights reserved.

    This source code is licensed under the BSD-style license found in the
    LICENSE file in the root directory of this source tree.
*/


function loaderShow() {

    const loader = document.getElementById('loader');

    if (!loader.classList.contains('active')) {

        loader.classList.add('active');

    }

}
function loaderHide() {

    const loader = document.getElementById('loader');

    if (loader.classList.contains('active')) {

        loader.classList.remove('active');

    }

}
function initModals() {

    const modals = document.getElementsByClassName('modal');

    for (const modal of modals) {

        modal.addEventListener(
            'click',
            function (e) {

                if (e.target.classList.contains('modal')) {

                    if (e.target.classList.contains('active')) {

                        e.target.classList.remove('active');

                    }

                }

            },
            false
        );

    }

}
function closeModals() {

    const modals = document.getElementsByClassName('modal');

    for (const modal of modals) {

        modal.classList.remove('active');

    }

}


function clearEventListenersById(elementId) {

    const originalElement = document.getElementById(elementId);
    const newElement = originalElement.cloneNode(true);
    originalElement.parentNode.replaceChild(newElement, originalElement);

}
function clearEventListenersByElement(element) {

    const newElement = element.cloneNode(true);
    element.parentNode.replaceChild(newElement, element);

}


var apiData = {};

var apiQueue = [];
var apiResponses = [
    {
        'data_key': 'image_data',
        'description': 'API image data',
        'request_types': [
            'image_data',
            'image_edit',
            'image_delete'
        ]
    }, {
        'data_key': 'image_settings',
        'description': 'API image settings',
        'request_types': [
            'image_display',
            'settings_get_image',
            'settings_set_image'
        ]
    }, {
        'data_key': 'password_settings',
        'description': 'API password settings',
        'request_types': [
            'settings_get_password',
            'settings_set_password'
        ]
    }, {
        'data_key': 'category_data',
        'description': 'API category data',
        'request_types': [
            'settings_get_category',
            'settings_set_category'
        ]
    }, {
        'data_key': 'task_data',
        'description': 'API task settings',
        'request_types': [
            'maintenance_get_task',
            'maintenance_set_task'
        ]
    }, {
        'data_key': 'user_data',
        'description': 'API user data',
        'request_types': [
            'settings_get_user',
            'settings_set_user',
            'settings_delete_user'
        ]
    }, {
        'data_key': 'permission_settings',
        'description': 'API permission settings',
        'request_types': [
            'settings_get_permission'
        ]
    }, {
        'data_key': 'log_data',
        'description': 'API log data',
        'request_types': [
            'maintenance_get_logs'
        ]
    }, {
        'data_key': 'server_data',
        'description': 'API server data',
        'request_types': [
            'maintenance_get_info'
        ]
    }
];


async function apiHandler(type, data) {

    const request = getApiRequest(type, data);


    if (request !== null) {

        let responseType = null;

        for (const apiResponse of apiResponses) {

            if (apiResponse.request_types.includes(type)) {

                responseType = apiResponse;

                break;

            }

        }

        if (responseType !== null) {

            updateStatus(
                'api',
                'start',
                {
                    'handler': responseType.data_key,
                    'text': responseType.description
                }
            );

            fetch(request)
                .then((response) => {

                    return response.json();

                }).then((responseData) => {

                    for (const responseKey of Object.keys(responseData)) {

                        apiData[responseKey] = responseData[responseKey];

                        for (const apiResponse of apiResponses) {

                            if (responseKey == apiResponse.data_key) {

                                document.dispatchEvent(
                                    new CustomEvent(apiResponse.data_key, {
                                        bubbles: true,
                                        detail: {
                                            value: responseData[responseKey]
                                        },
                                    }),
                                );

                                updateStatus(
                                    'api',
                                    'end',
                                    {
                                        'handler': apiResponse.data_key,
                                        'text': apiResponse.description
                                    }
                                );

                            }

                        }

                    }

                }).catch((error) => {

                    console.log(error);

                });

        }

    } else {

        console.log('Unknown API call', type);

    }

}
function getApiRequest(type, data) {

    let request = null;

    switch (type) {

        case 'image_data':

            request = new Request('/api/images/all', {
                method: 'GET',
                headers: new Headers({
                    'Accept': 'application/json'
                })
            });

            break;

        case 'image_display':

            request = new Request('/api/images/display', {
                method: 'POST',
                body: JSON.stringify(data),
                headers: new Headers({
                    'Accept': 'application/json',
                    'Content-Type': 'application/json; charset=UTF-8'
                })
            });

            break;

        case 'image_edit':

            request = new Request('/api/images/edit', {
                method: 'POST',
                body: JSON.stringify(data),
                headers: new Headers({
                    'Accept': 'application/json',
                    'Content-Type': 'application/json; charset=UTF-8'
                })
            });

            break;

        case 'image_delete':

            request = new Request('/api/images/delete', {
                method: 'DELETE',
                body: JSON.stringify(data),
                headers: new Headers({
                    'Accept': 'application/json',
                    'Content-Type': 'application/json; charset=UTF-8'
                })
            });

            break;

        case 'settings_get_image':

            request = new Request('/api/settings/image', {
                method: 'GET',
                headers: new Headers({
                    'Accept': 'application/json'
                })
            });

            break;

        case 'settings_set_image':

            request = new Request('/api/settings/image', {
                method: 'POST',
                body: JSON.stringify(data),
                headers: new Headers({
                    'Accept': 'application/json',
                    'Content-Type': 'application/json; charset=UTF-8'
                })
            });

            break;

        case 'settings_get_password':

            request = new Request('/api/settings/password', {
                method: 'GET',
                headers: new Headers({
                    'Accept': 'application/json'
                })
            });

            break;

        case 'settings_set_password':

            request = new Request('/api/settings/password', {
                method: 'POST',
                body: JSON.stringify(data),
                headers: new Headers({
                    'Accept': 'application/json',
                    'Content-Type': 'application/json; charset=UTF-8'
                })
            });

            break;

        case 'settings_get_category':

            request = new Request('/api/settings/category', {
                method: 'GET',
                headers: new Headers({
                    'Accept': 'application/json'
                })
            });

            break;

        case 'settings_set_category':

            request = new Request('/api/settings/category', {
                method: 'POST',
                body: JSON.stringify(data),
                headers: new Headers({
                    'Accept': 'application/json',
                    'Content-Type': 'application/json; charset=UTF-8'
                })
            });

            break;

        case 'maintenance_get_task':

            request = new Request('/api/maintenance/task', {
                method: 'GET',
                headers: new Headers({
                    'Accept': 'application/json'
                })
            });

            break;

        case 'maintenance_set_task':

            request = new Request('/api/maintenance/task', {
                method: 'POST',
                body: JSON.stringify(data),
                headers: new Headers({
                    'Accept': 'application/json',
                    'Content-Type': 'application/json; charset=UTF-8'
                })
            });

            break;

        case 'settings_get_user':

            request = new Request('/api/settings/user', {
                method: 'GET',
                headers: new Headers({
                    'Accept': 'application/json'
                })
            });

            break;

        case 'settings_set_user':

            request = new Request('/api/settings/user', {
                method: 'POST',
                body: JSON.stringify(data),
                headers: new Headers({
                    'Accept': 'application/json',
                    'Content-Type': 'application/json; charset=UTF-8'
                })
            });

            break;

        case 'settings_delete_user':

            request = new Request('/api/settings/user', {
                method: 'DELETE',
                body: JSON.stringify(data),
                headers: new Headers({
                    'Accept': 'application/json',
                    'Content-Type': 'application/json; charset=UTF-8'
                })
            });

            break;

        case 'settings_get_permission':

            request = new Request('/api/settings/permission', {
                method: 'GET',
                headers: new Headers({
                    'Accept': 'application/json'
                })
            });

            break;

        case 'maintenance_get_logs':

            request = new Request('/api/maintenance/logs', {
                method: 'GET',
                headers: new Headers({
                    'Accept': 'application/json'
                })
            });

            break;

        case 'maintenance_get_info':

            request = new Request('/api/maintenance/info', {
                method: 'GET',
                headers: new Headers({
                    'Accept': 'application/json'
                })
            });

            break;

        default:

            request = null;

    };


    return request;

}


var fileQueue = [];

function getChunkSize() {

    const chunkSizeElement = document.getElementById('chunk-size');

    const chunkSize = parseInt(chunkSizeElement.dataset.chunkSize);


    return chunkSize;

}
async function fileHandler(fileUploads) {

    const chunkSize = getChunkSize();

    let uploadInfo = [];

    for (const fileUpload of fileUploads) {

        let fileInfo = {};

        for (const uploadKey of Object.keys(fileUpload)) {

            if (uploadKey !== 'file') {

                fileInfo[uploadKey] = fileUpload[uploadKey];

            }

        }

        uploadInfo.push(fileInfo);

    }


    for (const fileUpload of fileUploads) {

        updateStatus(
            'file',
            'start',
            {
                'file': fileUpload.name,
                'total': fileUpload.chunks,
                'received': 0
            }
        );

        let chunkIndex = 0;
        let bytesStart = 0;

        while (bytesStart < fileUpload.size) {

            const chunkFormData = new FormData();

            chunkFormData.append(
                'info',
                JSON.stringify(
                    {
                        'info': uploadInfo,
                        'current': {
                            'index': fileUpload.index,
                            'chunk': chunkIndex
                        }
                    }
                )
            );
            chunkFormData.append(
                'file',
                fileUpload.file.slice(bytesStart, bytesStart + chunkSize)
            );

            chunkHandler(chunkFormData);


            bytesStart += chunkSize;
            chunkIndex += 1;

        }

    }

}
async function chunkHandler(chunkFormData, retries = 3) {

    try {

        const responseData = await fetch(
            '/api/images/upload',
            {
                method: 'POST',
                body: chunkFormData,
            }
        );

        const uploadResponse = await responseData.json();

        if (Object.keys(uploadResponse).includes('progress') && Object.keys(uploadResponse).includes('current_file')) {

            updateStatus(
                'file',
                'end',
                {
                    'file': uploadResponse.current_file
                }
            );


            let uploadComplete = true;

            if (uploadResponse.progress.length == 0) {

                uploadComplete = false;

            } else {

                for (const uploadProgress of uploadResponse.progress) {

                    if (uploadProgress.progress < 100.0) {

                        uploadComplete = false;

                    }

                }

            }


            if (uploadComplete == true) {

                apiHandler(
                    'image_data',
                    null
                );

            }

        }

    } catch (error) {

        if (retries > 0) {

            await uploadChunk(
                chunkFormData,
                retries - 1
            );

        } else {

            console.error('Chunk upload failed: ', info, error);

        }

    }

}


function updateStatus(updateType, status, info) {

    if (updateType == 'api') {

        if (status == 'start') {

            apiQueue.push(info);

        } else {

            for (var i = 0; i < apiQueue.length; i++) {

                if (info.handler == apiQueue[i].handler) {

                    apiQueue.splice(i, 1);

                    break;

                }

            }

        }

    } else if (updateType == 'file') {

        if (status == 'start') {

            fileQueue.push(info);

        } else {

            for (var i = 0; i < fileQueue.length; i++) {

                if (info.file == fileQueue[i].file) {

                    fileQueue[i].received = fileQueue[i].received + 1;

                    if (fileQueue[i].received == fileQueue[i].total) {

                        fileQueue.splice(i, 1);

                    }

                    break;

                }

            }

        }

    }


    const statusElement = document.getElementById('status');

    statusElement.innerHTML = '';


    let currentHandlers = [];

    for (const queueItem of apiQueue) {

        if (!currentHandlers.includes(queueItem.handler)) {

            currentHandlers.push(queueItem.handler);

            statusElement.insertAdjacentHTML('beforeend', `<span class="text">Waiting for ${queueItem.text}.</span>`);

        }

    }



    let currentFiles = [];

    for (const fileItem of fileQueue) {

        if (!currentFiles.includes(fileItem.file)) {

            currentFiles.push(fileItem.file);

            statusElement.insertAdjacentHTML('beforeend', `<span class="text">Waiting for ${fileItem.file}.</span>`);

        }

    }


    if (currentHandlers.length == 0 && currentFiles.length == 0) {

        statusElement.classList.remove('active');

        loaderHide();

    } else {

        if (!statusElement.classList.contains('active')) {

            statusElement.classList.add('active');

        }

        loaderShow();

    }

}
