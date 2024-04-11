/*
    Copyright (c) 2024, Alexander Austin
    All rights reserved.

    This source code is licensed under the BSD-style license found in the
    LICENSE file in the root directory of this source tree.
*/


window.onload = function () {

    if (window.initModals) {

        initModals();

    }

    if (window.initSettingsSections) {

        initSettingsSections();

    }

    if (window.initPasswordSection) {

        initPasswordSection();

    }

    if (window.initTaskSection) {

        initTaskSection();

    }

    if (window.initCategorySection) {

        initCategorySection();

    }

    if (window.initInfoSection) {

        initInfoSection();

    }

    if (window.initLogsSection) {

        initLogsSection();

    }

}


function initSettingsSections() {

    const settingsSections = document.getElementsByClassName('settings-section');

    for (const settingsSection of settingsSections) {

        settingsSection.classList.remove('active');

        const settingsSectionTitle = settingsSection.querySelector('.settings-section-title');

        settingsSectionTitle.addEventListener(
            'click',
            function (e) {

                const parentSection = e.target.parentElement;

                const parentState = parentSection.classList.contains('active');

                const settingsSections = document.getElementsByClassName('settings-section');

                for (const settingsSection of settingsSections) {

                    settingsSection.classList.remove('active');

                }


                if (parentState == false) {

                    parentSection.classList.add('active');

                }

            },
            true
        );

    }

}


function initPasswordSection() {

    const passwordSettingsOptions = document.getElementsByClassName('password-settings-option');

    for (const passwordSettingsOption of passwordSettingsOptions) {

        if (passwordSettingsOption.dataset.valueType == 'boolean') {

            passwordSettingsOption.addEventListener(
                'click',
                function (e) {

                    if (e.target.classList.contains('password-settings-option')) {

                        const passwordSettingsOptionCheckbox = e.target.querySelector('.checkbox');

                        if (e.target.dataset.value == 'true') {

                            e.target.dataset.value = 'false';
                            passwordSettingsOptionCheckbox.dataset.value = '0';

                        } else {

                            e.target.dataset.value = 'true';
                            passwordSettingsOptionCheckbox.dataset.value = '1';

                        }

                    } else {

                        const passwordSettingsOption = e.target.parentElement;

                        const passwordSettingsOptionCheckbox = passwordSettingsOption.querySelector('.checkbox');

                        if (passwordSettingsOption.dataset.value == 'true') {

                            passwordSettingsOption.dataset.value = 'false';
                            passwordSettingsOptionCheckbox.dataset.value = '0';

                        } else {

                            passwordSettingsOption.dataset.value = 'true';
                            passwordSettingsOptionCheckbox.dataset.value = '1';

                        }

                    }

                },
                true
            );

        } else if (passwordSettingsOption.dataset.valueType == 'integer') {

            const numberPicker = passwordSettingsOption.querySelector('.number-picker');

            const numberPickerButtons = numberPicker.querySelectorAll('.number-picker-button');

            for (const numberPickerButton of numberPickerButtons) {

                numberPickerButton.addEventListener(
                    'click',
                    function (e) {

                        if (e.target.classList.contains('number-picker-button')) {

                            const numberPickerDisplay = e.target.parentElement.querySelector('.number-picker-display');

                            const passwordSettingsOption = e.target.parentElement.parentElement;

                            const previousValues = {
                                'value': parseInt(passwordSettingsOption.dataset.value),
                                'min': parseInt(passwordSettingsOption.dataset.min),
                                'max': parseInt(passwordSettingsOption.dataset.max)
                            };

                            let newValue = previousValues.value;

                            if (e.target.classList.contains('up')) {

                                newValue = newValue + 1;

                            } else {

                                newValue = newValue - 1;

                            }

                            if (newValue < previousValues.min) {

                                newValue = previousValues.min;

                            }
                            if (newValue > previousValues.max) {

                                newValue = previousValues.max;

                            }


                            passwordSettingsOption.dataset.value = newValue;
                            numberPickerDisplay.innerText = newValue;

                        }

                    },
                    false
                );

            }

        }

    }


    const passwordSettingsRevertButton = document.getElementById('password-settings-revert-button');

    passwordSettingsRevertButton.addEventListener(
        'click',
        populatePasswordSection,
        true
    );


    const passwordSettingsSaveButton = document.getElementById('password-settings-save-button');

    passwordSettingsSaveButton.addEventListener(
        'click',
        function () {

            if (Object.keys(apiData).includes('password_settings')) {

                let newPasswordSettings = {
                    'upper': false,
                    'lower': false,
                    'number': false,
                    'special': false,
                    'length': 8
                };

                const passwordSettingsOptions = document.getElementsByClassName('password-settings-option');

                for (const passwordSettingsOption of passwordSettingsOptions) {

                    if (passwordSettingsOption.dataset.valueType == 'boolean') {

                        let optionKey = passwordSettingsOption.dataset.key;
                        let optionValue = false;

                        if (passwordSettingsOption.dataset.value === true) {

                            optionValue = true;

                        }

                        newPasswordSettings[optionKey] = optionValue

                    } else if (passwordSettingsOption.dataset.valueType == 'integer') {

                        let optionKey = passwordSettingsOption.dataset.key;
                        let optionValue = parseInt(passwordSettingsOption.dataset.value);

                        newPasswordSettings[optionKey] = optionValue

                    }

                }


                apiHandler(
                    'settings_set_password',
                    newPasswordSettings
                );

            }

        },
        true
    );


    document.addEventListener(
        'password_settings',
        populatePasswordSection,
        false
    );


    apiHandler(
        'settings_get_password',
        null
    );

}
function populatePasswordSection() {

    if (Object.keys(apiData).includes('password_settings')) {

        const passwordSettingsOptions = document.getElementsByClassName('password-settings-option');

        for (const passwordSettingsOption of passwordSettingsOptions) {

            for (const passwordKey of Object.keys(apiData.password_settings)) {

                if (passwordKey == passwordSettingsOption.dataset.key) {

                    passwordSettingsOption.dataset.value = apiData.password_settings[passwordKey];

                    if (passwordSettingsOption.dataset.valueType == 'boolean') {

                        const passwordSettingsOptionCheckbox = passwordSettingsOption.querySelector('.checkbox');

                        if (apiData.password_settings[passwordKey] == true) {

                            passwordSettingsOptionCheckbox.dataset.value = 1;

                        } else {

                            passwordSettingsOptionCheckbox.dataset.value = 0;

                        }

                    } else if (passwordSettingsOption.dataset.valueType == 'integer') {

                        const numberPicker = passwordSettingsOption.querySelector('.number-picker');

                        const numberPickerDisplay = numberPicker.querySelector('.number-picker-display');

                        numberPickerDisplay.innerText = apiData.password_settings[passwordKey];

                    }

                    break;

                }

            }

        }

    }

}


function initTaskSection() {

    const taskSettingsRevertButton = document.getElementById('task-settings-revert-button');

    taskSettingsRevertButton.addEventListener(
        'click',
        populateTaskSection,
        true
    );


    const taskSettingsSaveButton = document.getElementById('task-settings-save-button');

    taskSettingsSaveButton.addEventListener(
        'click',
        function () {

            if (Object.keys(apiData).includes('task_data')) {

                const durationPickers = document.getElementsByClassName('duration-picker');

                for (const durationPicker of durationPickers) {

                    for (var i = 0; i < apiData.task_data.length; i++) {

                        if (apiData.task_data[i].name == durationPicker.dataset.taskName) {

                            apiData.task_data[i].delay = parseInt(durationPicker.dataset.value);

                            break;

                        }

                    }

                }

                apiHandler(
                    'maintenance_set_task',
                    apiData.task_data
                );

            }

        },
        true
    );


    document.addEventListener(
        'task_data',
        populateTaskSection,
        false
    );


    apiHandler(
        'maintenance_get_task',
        null
    );

}
function populateTaskSection() {

    if (Object.keys(apiData).includes('task_data')) {

        const taskDurationPickerContainer = document.getElementById('task-duration-picker-container');

        taskDurationPickerContainer.innerHTML = '';

        const hmsNumberPickerData = [
            {
                'label': 'HH',
                'step': 3600,
                'coefficient': 3600
            },
            {
                'label': 'MM',
                'step': 60,
                'coefficient': 60,
                'modulo': 3600
            },
            {
                'label': 'SS',
                'step': 5,
                'coefficient': 1,
                'modulo': 60
            }
        ];

        let hmsNumberPickerHtml = '';

        for (var i = 0; i < hmsNumberPickerData.length; i++) {

            let hmsNumberPickerDataset = '';

            for (const hmsNumberPickerVarKey of Object.keys(hmsNumberPickerData[i])) {

                if (hmsNumberPickerVarKey !== 'label') {

                    hmsNumberPickerDataset = hmsNumberPickerDataset + ` data-${hmsNumberPickerVarKey}="${hmsNumberPickerData[i][hmsNumberPickerVarKey]}"`;

                }

            }

            hmsNumberPickerHtml = hmsNumberPickerHtml + `<div class="number-picker vertical"${hmsNumberPickerDataset}><div class="number-picker-label">${hmsNumberPickerData[i].label}</div><div class="number-picker-button up">></div><div class="number-picker-display">00</div><div class="number-picker-button down">></div></div>`;

            if (i < (hmsNumberPickerData.length - 1)) {

                hmsNumberPickerHtml = hmsNumberPickerHtml + '<div class="duration-picker-divider">:</div>';

            }

        }


        for (const taskData of apiData.task_data) {

            let durationPickerHtml = `<div class="duration-picker" data-task-name="${taskData.name}" data-value="${taskData.value}" data-min="15" data-max="86400"><div class="duration-picker-text-container"><span class="duration-picker-name text text-bold">${taskData.name}</span><span class="duration-picker-description text">${taskData.description}</span><span class="duration-picker-last text-small">Last: ${taskData.last_date_formatted}</span><span class="duration-picker-status text-small">Status: ${taskData.status}</span></div><div class="duration-picker-items-container">${hmsNumberPickerHtml}</div></div>`;

            taskDurationPickerContainer.insertAdjacentHTML('beforeend', durationPickerHtml);

        }


        const durationPickers = document.getElementsByClassName('duration-picker');

        for (const durationPicker of durationPickers) {

            for (const taskData of apiData.task_data) {

                if (taskData.name == durationPicker.dataset.taskName) {

                    durationPicker.dataset.value = taskData.delay;

                    const durationPickerItemsContainer = durationPicker.querySelector('.duration-picker-items-container');

                    const durationPickerNumberPickers = durationPickerItemsContainer.querySelectorAll('.number-picker');

                    for (const durationPickerNumberPicker of durationPickerNumberPickers) {

                        const durationPickerNumberPickerDisplay = durationPickerNumberPicker.querySelector('.number-picker-display');

                        if (!durationPickerNumberPicker.hasAttribute('data-modulo')) {

                            durationPickerNumberPickerDisplay.innerText = ('0' + Math.floor(taskData.delay / parseInt(durationPickerNumberPicker.dataset.coefficient))).slice(-2);

                        } else {

                            durationPickerNumberPickerDisplay.innerText = ('0' + Math.floor((taskData.delay % parseInt(durationPickerNumberPicker.dataset.modulo)) / parseInt(durationPickerNumberPicker.dataset.coefficient))).slice(-2);

                        }


                        const durationPickerNumberPickerButtons = durationPickerNumberPicker.querySelectorAll('.number-picker-button');

                        for (const durationPickerNumberPickerButton of durationPickerNumberPickerButtons) {

                            durationPickerNumberPickerButton.addEventListener(
                                'click',
                                function (e) {

                                    const durationPickerNumberPickerButton = e.target;

                                    const durationPickerNumberPicker = durationPickerNumberPickerButton.parentElement;

                                    const durationPicker = durationPickerNumberPicker.parentElement.parentElement;

                                    let newValue = parseInt(durationPicker.dataset.value);
                                    console.log('original', newValue);
                                    if (durationPickerNumberPickerButton.classList.contains('up')) {

                                        newValue = newValue + parseInt(durationPickerNumberPicker.dataset.step);

                                    } else {

                                        newValue = newValue - parseInt(durationPickerNumberPicker.dataset.step);

                                    }

                                    if (newValue < parseInt(durationPicker.dataset.min)) {

                                        newValue = parseInt(durationPicker.dataset.min);

                                    }
                                    if (newValue > parseInt(durationPicker.dataset.max)) {

                                        newValue = parseInt(durationPicker.dataset.max);

                                    }


                                    durationPicker.dataset.value = newValue;

                                    const durationPickerItemsContainer = durationPicker.querySelector('.duration-picker-items-container');

                                    const durationPickerNumberPickers = durationPickerItemsContainer.querySelectorAll('.number-picker');

                                    for (const durationPickerNumberPicker of durationPickerNumberPickers) {

                                        const durationPickerNumberPickerDisplay = durationPickerNumberPicker.querySelector('.number-picker-display');

                                        if (!durationPickerNumberPicker.hasAttribute('data-modulo')) {

                                            durationPickerNumberPickerDisplay.innerText = ('0' + Math.floor(newValue / parseInt(durationPickerNumberPicker.dataset.coefficient))).slice(-2);

                                        } else {

                                            durationPickerNumberPickerDisplay.innerText = ('0' + Math.floor((newValue % parseInt(durationPickerNumberPicker.dataset.modulo)) / parseInt(durationPickerNumberPicker.dataset.coefficient))).slice(-2);

                                        }

                                    }

                                },
                                false
                            );

                        }

                    }

                    break;

                }

            }

        }

    }

}


function initCategorySection() {

    document.addEventListener(
        'category_data',
        populateCategorySection,
        false
    );


    apiHandler(
        'settings_get_category',
        null
    );

}
function populateCategorySection() {

    populateNewCategorySection();

    populateEditCategorySection();

}
function populateNewCategorySection() {

    if (Object.keys(apiData).includes('category_data')) {

        clearEventListenersById('new-category-dropdown');

        const newCategoryDropdown = document.getElementById('new-category-dropdown');


        const newCategoryDropdownInput = newCategoryDropdown.querySelector('.dropdown-with-text-input');

        newCategoryDropdownInput.value = '';


        const newCategoryDropdownPlaceholder = newCategoryDropdown.querySelector('.dropdown-with-text-placeholder');

        newCategoryDropdownPlaceholder.dataset.id = -2;
        newCategoryDropdownPlaceholder.dataset.value = -2;
        newCategoryDropdownPlaceholder.dataset.name = 'Select/Create Category';
        newCategoryDropdownPlaceholder.innerText = 'Select/Create Category';

        const newCategoryDropdownHandle = newCategoryDropdown.querySelector('.dropdown-with-text-handle');

        for (const newCategoryDropdownItem of [newCategoryDropdownPlaceholder, newCategoryDropdownHandle]) {

            newCategoryDropdownItem.addEventListener(
                'click',
                function (e) {

                    const dropdown = e.target.parentElement;

                    if (dropdown.classList.contains('active')) {

                        dropdown.classList.remove('active');

                    } else {

                        dropdown.classList.add('active');

                    }
                },
                false
            );

        }


        const newCategoryDropdownOptionsContainer = newCategoryDropdown.querySelector('.dropdown-with-text-options');

        newCategoryDropdownOptionsContainer.innerHTML = '';
        newCategoryDropdownOptionsContainer.insertAdjacentHTML('beforeend', '<div class="dropdown-with-text-option" data-value="-1" data-id="-1" data-name="* Create New Category *">* Create New Category *</div>');

        for (const categoryData of apiData.category_data) {

            let categoryOptionHtml = `<div class="dropdown-with-text-option" data-value="${categoryData.id}" data-id="${categoryData.id}" data-name="${categoryData.name}">${categoryData.name}</div>`;

            newCategoryDropdownOptionsContainer.insertAdjacentHTML('beforeend', categoryOptionHtml);

        }


        const newCategoryDropdownOptions = newCategoryDropdownOptionsContainer.querySelectorAll('.dropdown-with-text-option');

        for (const newCategoryDropdownOption of newCategoryDropdownOptions) {

            newCategoryDropdownOption.addEventListener(
                'click',
                function (e) {

                    const newCategoryDropdown = e.target.parentElement.parentElement;

                    const newCategoryDropdownPlaceholder = newCategoryDropdown.querySelector('.dropdown-with-text-placeholder');

                    newCategoryDropdownPlaceholder.dataset.value = e.target.dataset.id;
                    newCategoryDropdownPlaceholder.dataset.id = e.target.dataset.id;
                    newCategoryDropdownPlaceholder.dataset.name = e.target.dataset.name;
                    newCategoryDropdownPlaceholder.innerText = e.target.dataset.name;


                    const newSubcategoryInput = document.getElementById('new-subcategory-input');

                    newSubcategoryInput.value = '';
                    newSubcategoryInput.classList.remove('hidden');


                    const newCategoryDropdownInput = newCategoryDropdown.querySelector('.dropdown-with-text-input');

                    newCategoryDropdownInput.focus();

                    newCategoryDropdown.classList.remove('active');

                },
                false
            );

        }


        clearEventListenersById('new-category-subcategory-settings-revert-button');

        const newCategorySubcategorySettingsRevertButton = document.getElementById('new-category-subcategory-settings-revert-button');

        newCategorySubcategorySettingsRevertButton.addEventListener(
            'click',
            populateNewCategorySection,
            false
        );


        clearEventListenersById('new-category-subcategory-settings-save-button');

        const newCategorySubcategorySettingsSaveButton = document.getElementById('new-category-subcategory-settings-save-button');

        newCategorySubcategorySettingsSaveButton.addEventListener(
            'click',
            function () {

                const newCategoryDropdown = document.getElementById('new-category-dropdown');

                const newCategoryDropdownPlaceholder = newCategoryDropdown.querySelector('.dropdown-with-text-placeholder');

                const newCategoryId = parseInt(newCategoryDropdownPlaceholder.dataset.id);

                if (newCategoryId !== -2) {

                    if (newCategoryId == -1) {

                        const newCategoryDropdownInput = newCategoryDropdown.querySelector('.dropdown-with-text-input');

                        const newCategoryName = newCategoryDropdownInput.value;

                        const newSubcategoryInput = document.getElementById('new-subcategory-input');

                        const newSubcategoryName = newSubcategoryInput.value;

                        if (newCategoryName.trim().length > 0) {

                            if (newSubcategoryName.trim().length > 0) {

                                apiHandler(
                                    'settings_set_category',
                                    {
                                        'action': 'add_category_with_subcategory',
                                        'category_name': newCategoryName.trim(),
                                        'subcategory_name': newSubcategoryName.trim()
                                    }
                                );

                            } else {

                                apiHandler(
                                    'settings_set_category',
                                    {
                                        'action': 'add_category',
                                        'category_name': newCategoryName.trim()
                                    }
                                );

                            }

                        }

                    } else {

                        const existingCategoryId = parseInt(newCategoryDropdownPlaceholder.dataset.id);

                        const newSubcategoryInput = document.getElementById('new-subcategory-input');

                        const newSubcategoryName = newSubcategoryInput.value;

                        if (newSubcategoryName.trim().length > 0) {

                            apiHandler(
                                'settings_set_category',
                                {
                                    'action': 'add_subcategory',
                                    'category_id': existingCategoryId,
                                    'subcategory_name': newSubcategoryName.trim()
                                }
                            );

                        }

                    }

                }

            },
            false
        );

    }

}
function populateEditCategorySection() {

    if (Object.keys(apiData).includes('category_data')) {

        const categorySettingsEditContainer = document.getElementById('category-settings-edit-container');

        categorySettingsEditContainer.innerHTML = '';

        for (const categoryData of apiData.category_data) {

            let categoryEditorHtml = `<div class="category-editor category" data-category-id="${categoryData.id}" data-category-name="${categoryData.name}"><input class="category-editor-name" type="text" placeholder="Edit Category..." value="${categoryData.name}" autocomplete="off" autocorrect="off" maxlength="128"><div class="revert-button"></div><div class="delete-button"></div></div>`;

            categorySettingsEditContainer.insertAdjacentHTML('beforeend', categoryEditorHtml);

            if (Object.keys(categoryData).includes('subcategories')) {

                for (const subcategoryData of categoryData.subcategories) {

                    let subcategoryEditorHtml = `<div class="category-editor subcategory" data-category-id="${categoryData.id}" data-category-name="${categoryData.name}" data-subcategory-id="${subcategoryData.id}" data-subcategory-name="${subcategoryData.name}"><input class="category-editor-name" type="text" placeholder="Edit Category..." value="${subcategoryData.name}" autocomplete="off" autocorrect="off" maxlength="128"><div class="revert-button"></div><div class="delete-button"></div></div>`;

                    categorySettingsEditContainer.insertAdjacentHTML('beforeend', subcategoryEditorHtml);

                }

            }

        }


        const categoryEditors = categorySettingsEditContainer.querySelectorAll('.category-editor');

        for (const categoryEditor of categoryEditors) {

            const categoryEditorRevertButton = categoryEditor.querySelector('.revert-button');

            categoryEditorRevertButton.addEventListener(
                'click',
                function (e) {

                    const categoryEditor = e.target.parentElement;

                    categoryEditor.classList.remove('delete');

                    const categoryEditorName = categoryEditor.querySelector('.category-editor-name');

                    if (categoryEditor.classList.contains('category')) {

                        categoryEditorName.value = categoryEditor.dataset.categoryName;

                    } else {

                        categoryEditorName.value = categoryEditor.dataset.subcategoryName;

                    }

                },
                false
            );


            const categoryEditorDeleteButton = categoryEditor.querySelector('.delete-button');

            categoryEditorDeleteButton.addEventListener(
                'click',
                function (e) {

                    const categoryEditor = e.target.parentElement;

                    if (categoryEditor.classList.contains('category')) {

                        const subcategoryEditors = categoryEditor.parentElement.querySelectorAll(`.category-editor.subcategory[data-category-id="${categoryEditor.dataset.categoryId}"]`);

                        for (const subcategoryEditor of subcategoryEditors) {

                            if (categoryEditor.classList.contains('delete')) {

                                subcategoryEditor.classList.remove('delete');

                            } else {

                                subcategoryEditor.classList.add('delete');

                            }

                        }

                    }

                    if (categoryEditor.classList.contains('delete')) {

                        categoryEditor.classList.remove('delete');

                    } else {

                        categoryEditor.classList.add('delete');

                    }

                },
                false
            );

        }


        clearEventListenersById('category-settings-edit-revert-button');

        const categorySettingsEditRevertButton = document.getElementById('category-settings-edit-revert-button');

        categorySettingsEditRevertButton.addEventListener(
            'click',
            populateEditCategorySection,
            true
        );


        clearEventListenersById('category-settings-edit-save-button');

        const categorySettingsEditSaveButton = document.getElementById('category-settings-edit-save-button');

        categorySettingsEditSaveButton.addEventListener(
            'click',
            function () {

                if (Object.keys(apiData).includes('category_data')) {

                    let categoryActions = [];
                    let categoryDeleteIds = [];

                    const categorySettingsEditContainer = document.getElementById('category-settings-edit-container');

                    const categoryEditors = categorySettingsEditContainer.querySelectorAll('.category-editor');

                    for (const categoryEditor of categoryEditors) {

                        if (categoryEditor.classList.contains('delete')) {

                            if (categoryEditor.classList.contains('category')) {

                                categoryDeleteIds.push(parseInt(categoryEditor.dataset.categoryId));

                                categoryActions.push(
                                    {
                                        'action': 'delete_category',
                                        'category_id': parseInt(categoryEditor.dataset.categoryId)
                                    }
                                );

                            } else {

                                if (!categoryDeleteIds.includes(parseInt(categoryEditor.dataset.categoryId))) {

                                    categoryActions.push(
                                        {
                                            'action': 'delete_subcategory',
                                            'subcategory_id': parseInt(categoryEditor.dataset.subcategoryId)
                                        }
                                    );

                                }

                            }

                        } else {

                            if (categoryEditor.classList.contains('category')) {

                                const categoryEditorName = categoryEditor.querySelector('.category-editor-name');

                                if (categoryEditorName.value !== categoryEditor.dataset.categoryName) {

                                    categoryActions.push(
                                        {
                                            'action': 'edit_category',
                                            'category_name': categoryEditorName.value.trim(),
                                            'category_id': parseInt(categoryEditor.dataset.categoryId)
                                        }
                                    );

                                }

                            } else {

                                const categoryEditorName = categoryEditor.querySelector('.category-editor-name');

                                if (categoryEditorName.value !== categoryEditor.dataset.subcategoryName) {

                                    categoryActions.push(
                                        {
                                            'action': 'edit_subcategory',
                                            'subcategory_name': categoryEditorName.value.trim(),
                                            'subcategory_id': parseInt(categoryEditor.dataset.subcategoryId)
                                        }
                                    );

                                }

                            }

                        }

                    }


                    if (categoryActions.length > 0) {

                        apiHandler(
                            'settings_set_category',
                            categoryActions
                        );

                    }

                }

            },
            true
        );

    }

}


function initInfoSection() {

    document.addEventListener(
        'server_data',
        populateInfoSection,
        false
    );


    apiHandler(
        'maintenance_get_info',
        null
    );

}
function populateInfoSection() {

    if (Object.keys(apiData).includes('server_data')) {

        if (apiData.server_data.length > 0) {

            const infoTableHeader = document.getElementById('info-table-header');

            infoTableHeader.innerHTML = '';
            console.log('here', apiData.server_data);
            for (const serverKey of Object.keys(apiData.server_data[0])) {
                console.log('here 2');
                let columnName = [];

                for (const keyWord of serverKey.split('_')) {

                    columnName.push(keyWord.charAt(0).toUpperCase() + keyWord.slice(1));

                }
                console.log(`<th scope="col">${columnName.join(' ')}</th>`);
                infoTableHeader.insertAdjacentHTML('beforeend', `<th scope="col">${columnName.join(' ')}</th>`);

            }


            const infoTableBody = document.getElementById('info-table-body');

            infoTableBody.innerHTML = '';

            for (const serverData of apiData.server_data) {

                let serverRowHtml = '<tr>';

                for (const serverKey of Object.keys(apiData.server_data[0])) {

                    serverRowHtml = serverRowHtml + `<td>${serverData[serverKey]}</td>`;

                }

                serverRowHtml = serverRowHtml + '</tr>';

                infoTableBody.insertAdjacentHTML('beforeend', serverRowHtml);

            }

        }

    }

}


function initLogsSection() {

    document.addEventListener(
        'log_data',
        populateLogsSection,
        false
    );


    apiHandler(
        'maintenance_get_logs',
        null
    );

}
function populateLogsSection() {

    if (Object.keys(apiData).includes('log_data')) {

        const logTableBody = document.getElementById('log-table-body');

        logTableBody.innerHTML = '';


        for (const logData of apiData.log_data.logs) {

            let logRowHtml = `<tr><th>${logData.date}</th><td>${logData.source}</td><td>${logData.entry}</td></tr>`;

            logTableBody.insertAdjacentHTML('beforeend', logRowHtml);

        }

    }

}
