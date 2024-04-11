/*
    Copyright (c) 2024, Alexander Austin
    All rights reserved.

    This source code is licensed under the BSD-style license found in the
    LICENSE file in the root directory of this source tree.
*/


function initAllUsers() {

    const allUsersHeader = document.getElementById('all-users-header');

    allUsersHeader.addEventListener(
        'click',
        function () {

            const allUsersSection = document.getElementById('all-users-section');

            allUsersSection.classList.toggle('active');


            const otherUserSections = document.querySelectorAll('.user-section:not(#all-users-section)');

            for (const otherUserSection of otherUserSections) {

                otherUserSection.classList.remove('active');

            }

        },
        false
    );


    const allUsersRevertButton = document.getElementById('all-users-revert-button');

    allUsersRevertButton.addEventListener(
        'click',
        function () {

            if (Object.keys(apiData).includes('user_data') && Object.keys(apiData).includes('permission_settings')) {

                const allUsersItemContainer = document.getElementById('all-users-item-container');

                const allUserItems = allUsersItemContainer.querySelectorAll('.all-users-item');

                for (const allUserItem of allUserItems) {

                    allUserItem.classList.remove('delete');

                    const allUserItemInputs = allUserItem.querySelectorAll('.user-input');

                    for (const allUserItemInput of allUserItemInputs) {

                        allUserItemInput.value = allUserItemInput.dataset.originalValue;

                    }


                    const allUsersPermissionCheckboxes = allUserItem.querySelectorAll('.permission-item > .checkbox');

                    for (const allUsersPermissionCheckbox of allUsersPermissionCheckboxes) {

                        allUsersPermissionCheckbox.dataset.value = allUsersPermissionCheckbox.dataset.originalValue;

                    }

                }

            }

        },
        false
    );


    const allUsersSaveButton = document.getElementById('all-users-save-button');

    allUsersSaveButton.addEventListener(
        'click',
        function () {

            if (Object.keys(apiData).includes('user_data') && Object.keys(apiData).includes('permission_settings')) {

                const allUsersItemContainer = document.getElementById('all-users-item-container');

                const allUserItems = allUsersItemContainer.querySelectorAll('.all-users-item');

                for (const allUserItem of allUserItems) {

                    if (allUserItem.classList.contains('delete')) {

                        apiHandler(
                            'settings_delete_user',
                            {
                                'id': parseInt(allUserItem.dataset.userId)
                            }
                        );

                    } else {

                        let editedUserData = {
                            'id': parseInt(allUserItem.dataset.userId)
                        };


                        const allUserItemInputs = allUserItem.querySelectorAll('.user-input');

                        for (const allUserItemInput of allUserItemInputs) {

                            if (allUserItemInput.value !== allUserItemInput.dataset.originalValue) {

                                if (allUserItemInput.value.length > 0) {

                                    editedUserData[allUserItemInput.dataset.key] = allUserItemInput.value;

                                }

                            }

                        }


                        let permissionsModified = false;
                        let permissions = [];

                        const allUsersPermissionCheckboxes = allUserItem.querySelectorAll('.permission-item > .checkbox');

                        for (const allUsersPermissionCheckbox of allUsersPermissionCheckboxes) {

                            if (allUsersPermissionCheckbox.dataset.value == '1') {

                                permissions.push(
                                    {
                                        'permission_id': parseInt(allUsersPermissionCheckbox.dataset.id)
                                    }
                                );

                            }

                            if (allUsersPermissionCheckbox.dataset.value !== allUsersPermissionCheckbox.dataset.originalValue) {

                                permissionsModified = true;

                            }

                        }

                        if (permissionsModified == true) {

                            editedUserData.user_permissions = permissions;

                        }


                        if (Object.keys(editedUserData).length > 1) {

                            apiHandler(
                                'settings_set_user',
                                editedUserData
                            );

                        }

                    }

                }

            }

        },
        false
    );


    document.addEventListener(
        'permission_settings',
        populateAllUsers,
        false
    );

    document.addEventListener(
        'user_data',
        populateAllUsers,
        false
    );


    apiHandler(
        'settings_get_permission',
        null
    );

    apiHandler(
        'settings_get_user',
        null
    );

}
function populateAllUsers() {

    if (Object.keys(apiData).includes('user_data') && Object.keys(apiData).includes('permission_settings')) {

        if (Array.isArray(apiData.user_data)) {

            const allUsersItemContainer = document.getElementById('all-users-item-container');

            allUsersItemContainer.innerHTML = '';

            for (const userData of apiData.user_data) {

                let allUsersItemHtml = `<div class="all-users-item" data-user-id="${userData.id}"></div>`;

                allUsersItemContainer.insertAdjacentHTML('beforeend', allUsersItemHtml);


                const allUsersItem = allUsersItemContainer.lastChild;

                for (const userKeyTitle of [['username', 'User Name:'], ['given_name', 'Given Name:'], ['family_name', 'Family Name:']]) {

                    let userLabelHtml = `<span class="user-label text">${userKeyTitle[1]}</span>`;

                    allUsersItem.insertAdjacentHTML('beforeend', userLabelHtml);


                    let userInputHtml = `<input class="user-input" type="text" value="${userData[userKeyTitle[0]]}" data-original-value="${userData[userKeyTitle[0]]}" data-key="${userKeyTitle[0]}" placeholder="Enter ${userKeyTitle[1]}..." autocomplete="off" autocorrect="off" maxlength="256" />`;

                    allUsersItem.insertAdjacentHTML('beforeend', userInputHtml);

                }

                allUsersItem.insertAdjacentHTML('beforeend', '<span class="user-label text">Password:</span>');
                allUsersItem.insertAdjacentHTML('beforeend', '<input class="user-input" type="password" value="" data-original-value="" data-key="password" placeholder="Enter new password..." autocomplete="off" autocorrect="off" maxlength="128" />');
                allUsersItem.insertAdjacentHTML('beforeend', '<span class="text">Permissions</span><br />');


                let userPermissionIds = [];

                for (const userPermission of userData.user_permissions) {

                    userPermissionIds.push(userPermission.permission_id);

                }


                for (const permissionData of apiData.permission_settings) {

                    let permissionItemLabelHtml = `<span class="user-label text">${permissionData.name}:</span>`;
                    let permissionItemCheckboxHtml = `<div class="checkbox" data-id="${permissionData.id}" data-value="${(userPermissionIds.includes(permissionData.id)) ? 1 : 0}" data-original-value="${(userPermissionIds.includes(permissionData.id)) ? 1 : 0}"></div>`;
                    let permissionItemDescriptionHtml = `<span class="permission-description">${permissionData.description}</span>`;

                    let permissionItemHtml = `<div class="permission-item"><span class="permission-info">i</span>${permissionItemLabelHtml}${permissionItemCheckboxHtml}${permissionItemDescriptionHtml}</div>`;

                    allUsersItem.insertAdjacentHTML('beforeend', permissionItemHtml);

                }

                allUsersItem.insertAdjacentHTML('beforeend', '<div class="delete-button"></div></div>');

            }


            const allUserItems = allUsersItemContainer.querySelectorAll('.all-users-item');

            for (const allUserItem of allUserItems) {

                const allUsersPermissionInfos = allUserItem.querySelectorAll('.permission-item > .permission-info');

                for (const allUsersPermissionInfo of allUsersPermissionInfos) {

                    allUsersPermissionInfo.addEventListener(
                        'click',
                        function (e) {

                            const allUsersPermissionInfoParent = e.target.parentElement;

                            const allUsersPermissionDescription = allUsersPermissionInfoParent.querySelector('.permission-description');

                            allUsersPermissionDescription.classList.toggle('active');

                        },
                        false
                    );

                }


                const allUsersPermissionDescriptions = allUserItem.querySelectorAll('.permission-item > .permission-description');

                for (const allUsersPermissionDescription of allUsersPermissionDescriptions) {

                    allUsersPermissionDescription.addEventListener(
                        'click',
                        function (e) {

                            e.target.classList.toggle('active');

                        },
                        false
                    );
                }


                const allUsersPermissionCheckboxes = allUserItem.querySelectorAll('.permission-item > .checkbox');

                for (const allUsersPermissionCheckbox of allUsersPermissionCheckboxes) {

                    allUsersPermissionCheckbox.addEventListener(
                        'click',
                        function (e) {

                            if (e.target.dataset.value == '0') {

                                e.target.dataset.value = '1';

                            } else {

                                e.target.dataset.value = '0';

                            }

                        },
                        false
                    );

                }


                const allUsersDeleteSingleButton = allUserItem.querySelector('.delete-button');

                allUsersDeleteSingleButton.addEventListener(
                    'click',
                    function (e) {

                        e.target.parentElement.classList.toggle('delete');

                    },
                    false
                );

            }


            const allUsersHeader = document.getElementById('all-users-header');

            allUsersHeader.classList.remove('hidden');


            const allUsersSection = document.getElementById('all-users-section');

            allUsersSection.classList.remove('hidden');

        } else {

            apiHandler(
                'settings_get_user',
                null
            );

        }

    }

}

function initNewUser() {

    const newUserHeader = document.getElementById('new-user-header');

    newUserHeader.addEventListener(
        'click',
        function () {

            const newUserSection = document.getElementById('new-user-section');

            newUserSection.classList.toggle('active');


            const otherUserSections = document.querySelectorAll('.user-section:not(#new-user-section)');

            for (const otherUserSection of otherUserSections) {

                otherUserSection.classList.remove('active');

            }

        },
        false
    );


    const newUserRevertButton = document.getElementById('new-user-revert-button');

    newUserRevertButton.addEventListener(
        'click',
        function () {

            if (Object.keys(apiData).includes('permission_settings')) {

                const newUserSection = document.getElementById('new-user-section');

                const newUserItems = newUserSection.querySelectorAll('.new-user-item');

                for (const newUserItem of newUserItems) {

                    const newUserInput = newUserItem.querySelector('.user-input');

                    newUserInput.value = newUserInput.dataset.originalValue;

                }

                const newUserPermissionContainer = document.getElementById('new-user-permission-container');

                const newUserPermissionItems = newUserPermissionContainer.querySelectorAll('.permission-item');

                for (const newUserPermissionItem of newUserPermissionItems) {

                    const newUserPermissionCheckbox = newUserPermissionItem.querySelector('.checkbox');

                    newUserPermissionCheckbox.dataset.value = newUserPermissionCheckbox.dataset.originalValue;

                }

            }

        },
        false
    );


    const newUserSaveButton = document.getElementById('new-user-save-button');

    newUserSaveButton.addEventListener(
        'click',
        function () {

            if (Object.keys(apiData).includes('permission_settings')) {

                let newUserData = {};


                const newUserSection = document.getElementById('new-user-section');

                const newUserItems = newUserSection.querySelectorAll('.new-user-item');

                for (const newUserItem of newUserItems) {

                    const newUserInput = newUserItem.querySelector('.user-input');

                    if (newUserInput.value !== newUserInput.dataset.originalValue) {

                        if (newUserInput.value.trim().length > 0) {

                            newUserData[newUserInput.dataset.key] = newUserInput.value.trim();

                        }

                    }

                }


                let newUserPermissions = [];


                const newUserPermissionContainer = document.getElementById('new-user-permission-container');

                const newUserPermissionItems = newUserPermissionContainer.querySelectorAll('.permission-item');

                for (const newUserPermissionItem of newUserPermissionItems) {

                    const newUserPermissionCheckbox = newUserPermissionItem.querySelector('.checkbox');

                    if (newUserPermissionCheckbox.dataset.value == '1') {

                        newUserPermissions.push(
                            {
                                'permission_id': parseInt(newUserPermissionCheckbox.dataset.id)
                            }
                        );

                    }

                }

                if (newUserPermissions.length > 0) {

                    newUserData['user_permissions'] = newUserPermissions;

                }


                if (Object.keys(newUserData).length > 0) {

                    if (Object.keys(newUserData).includes('username') && Object.keys(newUserData).includes('password')) {

                        apiHandler(
                            'settings_set_user',
                            newUserData
                        );

                    }

                }

            }

        },
        false
    );


    apiHandler(
        'settings_get_permission',
        null
    );


    document.addEventListener(
        'permission_settings',
        populateNewUser,
        false
    );

}
function populateNewUser() {

    if (Object.keys(apiData).includes('permission_settings')) {

        const newUserPermissionContainer = document.getElementById('new-user-permission-container');

        newUserPermissionContainer.innerHTML = '';

        newUserPermissionContainer.insertAdjacentHTML('beforeend', '<span class="text">Permissions</span><br />');

        for (const permissionData of apiData.permission_settings) {

            let permissionItemHtml = `<div class="permission-item"><span class="permission-info">i</span><span class="user-label text">${permissionData.name}:</span><div class="checkbox" data-id="${permissionData.id}" data-value="0" data-original-value="0"></div><span class="permission-description">${permissionData.description}</span></div>`;

            newUserPermissionContainer.insertAdjacentHTML('beforeend', permissionItemHtml);

        }


        const newUserPermissionItems = newUserPermissionContainer.querySelectorAll('.permission-item');

        for (const newUserPermissionItem of newUserPermissionItems) {

            const newUserPermissionInfo = newUserPermissionItem.querySelector('.permission-info');

            newUserPermissionInfo.addEventListener(
                'click',
                function (e) {

                    const newUserPermissionInfoParent = e.target.parentElement;

                    const newUserPermissionDescription = newUserPermissionInfoParent.querySelector('.permission-description');

                    newUserPermissionDescription.classList.toggle('active');

                },
                false
            );


            const newUserPermissionDescription = newUserPermissionItem.querySelector('.permission-description');

            newUserPermissionInfo.addEventListener(
                'click',
                function (e) {

                    e.target.classList.toggle('active');

                },
                false
            );


            const newUserPermissionCheckbox = newUserPermissionItem.querySelector('.checkbox');

            newUserPermissionCheckbox.addEventListener(
                'click',
                function (e) {

                    if (e.target.dataset.value == '0') {

                        e.target.dataset.value = '1';

                    } else {

                        e.target.dataset.value = '0';

                    }

                },
                false
            );

        }


        const newUserHeader = document.getElementById('new-user-header');

        newUserHeader.classList.remove('hidden');


        const newUserSection = document.getElementById('new-user-section');

        newUserSection.classList.remove('hidden');

    }

}
