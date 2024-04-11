/*
    Copyright (c) 2024, Alexander Austin
    All rights reserved.

    This source code is licensed under the BSD-style license found in the
    LICENSE file in the root directory of this source tree.
*/


window.onload = function () {

    if (window.initCurrentUser) {

        initCurrentUser();

    }

    if (window.initAllUsers) {

        initAllUsers();

    }

    if (window.initNewUser) {

        initNewUser();

    }

}


function initCurrentUser() {

    const currentUserHeader = document.getElementById('current-user-header');

    currentUserHeader.addEventListener(
        'click',
        function () {

            const currentUserSection = document.getElementById('current-user-section');

            currentUserSection.classList.toggle('active');


            const otherUserSections = document.querySelectorAll('.user-section:not(#current-user-section)');

            for (const otherUserSection of otherUserSections) {

                otherUserSection.classList.remove('active');

            }

        },
        false
    );


    const currentUserRevertButton = document.getElementById('current-user-revert-button');

    currentUserRevertButton.addEventListener(
        'click',
        function () {

            const currentUserSection = document.getElementById('current-user-section');

            const currentUserItems = currentUserSection.querySelectorAll('.current-user-item');

            for (const currentUserItem of currentUserItems) {

                const currentUserInput = currentUserItem.querySelector('.user-input');

                currentUserInput.value = currentUserInput.dataset.originalValue;

            }

        },
        false
    );


    const currentUserSaveButton = document.getElementById('current-user-save-button');

    currentUserSaveButton.addEventListener(
        'click',
        function () {

            const currentUserHeader = document.getElementById('current-user-header');

            let editedCurrentUserData = {
                'id': parseInt(currentUserHeader.dataset.currentUserId)
            };


            const currentUserSection = document.getElementById('current-user-section');

            const currentUserItems = currentUserSection.querySelectorAll('.current-user-item');

            for (const currentUserItem of currentUserItems) {

                const currentUserInput = currentUserItem.querySelector('.user-input');

                if (currentUserInput.value !== currentUserInput.dataset.originalValue) {

                    if (currentUserInput.value.length > 0) {

                        editedCurrentUserData[currentUserInput.dataset.key] = currentUserInput.value;

                    }

                }

            }


            if (Object.keys(editedCurrentUserData).length > 1) {

                apiHandler(
                    'settings_set_user',
                    editedCurrentUserData
                );

            }

        },
        false
    );

}
