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

    if (window.initImageFilterAndSort) {

        initImageFilterAndSort();

    }

    if (window.initImageSizingAndOrientation) {

        initImageSizingAndOrientation();

    }

    if (window.initEditImageModal) {

        initEditImageModal();

    }

    if (window.initDisplayAdd) {

        initDisplayAdd();

    }

    if (window.initThumbnails) {

        initThumbnails();

    }

    if (window.initSearch) {

        initSearch();

    }


    
    apiHandler(
        'image_data',
        null
    );

    document.addEventListener(
        'settings_get_image',
        imageSettingsRefresh.received_handler,
        false
    );
    imageSettingsRefresh.poller_id = setInterval(imageSettingsRefresh.poller, imageSettingsRefresh.interval);
    apiHandler(
        'settings_get_image',
        null
    );

    apiHandler(
        'settings_get_category',
        null
    );

}

var imageSettingsRefresh = {
    'interval': 5000,
    'last': 0,
    'received_handler': function () {

        imageSettingsRefresh.last = Date.now();

        clearInterval(imageSettingsRefresh.poller_id);
        imageSettingsRefresh.poller_id = setInterval(imageSettingsRefresh.poller, imageSettingsRefresh.interval);

    },
    'poller_id': -1,
    'poller': function () {

        apiHandler(
            'settings_get_image',
            null,
            true
        );

    }
};


function initImageFilterAndSort() {

    const displayFilters = document.getElementById('display-filters');

    displayFilters.addEventListener(
        'click',
        function () {

            if (Object.keys(apiData).includes('image_settings') && Object.keys(apiData).includes('category_data')) {

                populateTags(
                    'filter-and-sort-images-modal-filter-include-container',
                    imageTags = null,
                    imageId = null,
                    tagFilters = apiData.image_settings.filters,
                    filterType = 'include'
                );
                populateTags(
                    'filter-and-sort-images-modal-filter-exclude-container',
                    imageTags = null,
                    imageId = null,
                    tagFilters = apiData.image_settings.filters,
                    filterType = 'exclude'
                );


                const filterAndSortImagesModal = document.getElementById('filter-and-sort-images-modal');

                filterAndSortImagesModal.classList.add('active');

            }

        },
        false
    );


    const filterAndSortImagesModalSortSelect = document.getElementById('filter-and-sort-images-modal-sort-select');

    const filterAndSortImagesModalSortSelectOptions = filterAndSortImagesModalSortSelect.querySelectorAll('.accordian-select-option');

    for (const filterAndSortImagesModalSortSelectOption of filterAndSortImagesModalSortSelectOptions) {

        filterAndSortImagesModalSortSelectOption.addEventListener(
            'click',
            function (e) {

                const accordianSelectOption = e.target;

                const accordianSelect = accordianSelectOption.parentElement;

                if (accordianSelectOption.classList.contains('active')) {

                    if (accordianSelect.classList.contains('active')) {

                        accordianSelect.classList.remove('active');

                    } else {

                        accordianSelect.classList.add('active');

                    }

                } else {

                    const siblingOptions = accordianSelect.querySelectorAll('.accordian-select-option');

                    for (const siblingOption of siblingOptions) {

                        siblingOption.classList.remove('active')

                    }

                    accordianSelectOption.classList.add('active');
                    accordianSelect.classList.remove('active');

                }

            },
            false
        );

    }


    const filterAndSortImagesModalFilterContainerIncludeButton = document.getElementById('filter-and-sort-images-modal-filter-container-include-button');

    filterAndSortImagesModalFilterContainerIncludeButton.addEventListener(
        'click',
        function () {

            const filterAndSortImagesModalFilterContainerIncludeButton = document.getElementById('filter-and-sort-images-modal-filter-container-include-button');

            if (!filterAndSortImagesModalFilterContainerIncludeButton.classList.contains('active')) {

                filterAndSortImagesModalFilterContainerIncludeButton.classList.add('active');

            }


            const filterAndSortImagesModalFilterIncludeContainer = document.getElementById('filter-and-sort-images-modal-filter-include-container');

            if (!filterAndSortImagesModalFilterIncludeContainer.classList.contains('active')) {

                filterAndSortImagesModalFilterIncludeContainer.classList.add('active');

            }


            const filterAndSortImagesModalFilterContainerExcludeButton = document.getElementById('filter-and-sort-images-modal-filter-container-exclude-button');

            if (filterAndSortImagesModalFilterContainerExcludeButton.classList.contains('active')) {

                filterAndSortImagesModalFilterContainerExcludeButton.classList.remove('active');

            }


            const filterAndSortImagesModalFilterExcludeContainer = document.getElementById('filter-and-sort-images-modal-filter-exclude-container');

            if (filterAndSortImagesModalFilterExcludeContainer.classList.contains('active')) {

                filterAndSortImagesModalFilterExcludeContainer.classList.remove('active');

            }

        },
        false
    );


    const filterAndSortImagesModalFilterContainerExcludeButton = document.getElementById('filter-and-sort-images-modal-filter-container-exclude-button');

    filterAndSortImagesModalFilterContainerExcludeButton.addEventListener(
        'click',
        function () {

            const filterAndSortImagesModalFilterContainerIncludeButton = document.getElementById('filter-and-sort-images-modal-filter-container-include-button');

            if (filterAndSortImagesModalFilterContainerIncludeButton.classList.contains('active')) {

                filterAndSortImagesModalFilterContainerIncludeButton.classList.remove('active');

            }


            const filterAndSortImagesModalFilterIncludeContainer = document.getElementById('filter-and-sort-images-modal-filter-include-container');

            if (filterAndSortImagesModalFilterIncludeContainer.classList.contains('active')) {

                filterAndSortImagesModalFilterIncludeContainer.classList.remove('active');

            }


            const filterAndSortImagesModalFilterContainerExcludeButton = document.getElementById('filter-and-sort-images-modal-filter-container-exclude-button');

            if (!filterAndSortImagesModalFilterContainerExcludeButton.classList.contains('active')) {

                filterAndSortImagesModalFilterContainerExcludeButton.classList.add('active');

            }


            const filterAndSortImagesModalFilterExcludeContainer = document.getElementById('filter-and-sort-images-modal-filter-exclude-container');

            if (!filterAndSortImagesModalFilterExcludeContainer.classList.contains('active')) {

                filterAndSortImagesModalFilterExcludeContainer.classList.add('active');

            }

        },
        false
    );


    const filterAndSortImagesModalCancelButton = document.getElementById('filter-and-sort-images-modal-cancel-button');

    filterAndSortImagesModalCancelButton.addEventListener(
        'click',
        function () {

            closeModals();

        },
        false
    );


    const filterAndSortImagesModalApplyButton = document.getElementById('filter-and-sort-images-modal-apply-button');

    filterAndSortImagesModalApplyButton.addEventListener(
        'click',
        function () {

            if (Object.keys(apiData).includes('image_data') && Object.keys(apiData).includes('category_data') && Object.keys(apiData).includes('image_settings')) {

                const includeTagsChanged = tagSelectionChanged('filter-and-sort-images-modal-filter-include-container');
                const excludeTagsChanged = tagSelectionChanged('filter-and-sort-images-modal-filter-exclude-container');

                if (includeTagsChanged == true || excludeTagsChanged == true) {

                    const includeTags = getSelectedTags('filter-and-sort-images-modal-filter-include-container');
                    const excludeTags = getSelectedTags('filter-and-sort-images-modal-filter-exclude-container');

                    const filters = includeTags.concat(excludeTags);

                    apiData.image_settings.filters = filters;

                    apiHandler(
                        'settings_set_image',
                        apiData.image_settings
                    );

                }

                filterAndSortThumbnails();


                closeModals();

            }

        },
        false
    );

}

function initImageSizingAndOrientation() {

    const displaySizingAndOrientation = document.getElementById('display-sizing-and-orientation');

    displaySizingAndOrientation.addEventListener(
        'click',
        function () {

            if (Object.keys(apiData).includes('image_settings')) {

                const imageSizingAndOrientationModal = document.getElementById('image-sizing-and-orientation-modal');

                imageSizingAndOrientationModal.classList.add('active');

            }

        },
        false
    );


    const imageSizingAndOrientationModalSizingOptionsContainer = document.getElementById('image-sizing-and-orientation-modal-sizing-options-container');
    const imageSizingAndOrientationModalSizingOptions = imageSizingAndOrientationModalSizingOptionsContainer.querySelectorAll('.image-sizing-and-orientation-modal-sizing-option');

    for (const imageSizingAndOrientationModalSizingOption of imageSizingAndOrientationModalSizingOptions) {

        imageSizingAndOrientationModalSizingOption.addEventListener(
            'click',
            function (e) {

                let sizingType = apiData.image_settings.sizing.type;
                let sizingFill = apiData.image_settings.sizing.fill;

                if (e.target.classList.contains('image-sizing-and-orientation-modal-sizing-option')) {
                    sizingType = e.target.dataset.sizingType;
                    sizingFill = e.target.dataset.sizingFill;
                } else if (e.target.nodeName == 'SPAN') {
                    sizingType = e.target.parentElement.dataset.sizingType;
                    sizingFill = e.target.parentElement.dataset.sizingFill;
                } else if (e.target.classList.contains('sizing-container')) {
                    sizingType = e.target.parentElement.dataset.sizingType;
                    sizingFill = e.target.parentElement.dataset.sizingFill;
                } else if (e.target.classList.contains('sizing-container-inner')) {
                    sizingType = e.target.parentElement.parentElement.dataset.sizingType;
                    sizingFill = e.target.parentElement.parentElement.dataset.sizingFill;
                } else {
                    sizingType = e.target.parentElement.parentElement.parentElement.dataset.sizingType;
                    sizingFill = e.target.parentElement.parentElement.parentElement.dataset.sizingFill;
                }

                closeModals();

                apiHandler(
                    'settings_set_image',
                    {
                        'sizing': {
                            'type': sizingType,
                            'fill': sizingFill
                        }
                    }
                );

            },
            true
        );

    }


    const imageSizingAndOrientationModalCancelButton = document.getElementById('image-sizing-and-orientation-modal-cancel-button');

    imageSizingAndOrientationModalCancelButton.addEventListener(
        'click',
        function () {

            closeModals();

        },
        false
    );


    document.addEventListener(
        'image_settings',
        function () {

            clearEventListenersById('image-sizing-and-orientation-modal-orientation-container');

            const imageSizingAndOrientationModalOrientationContainer = document.getElementById('image-sizing-and-orientation-modal-orientation-container');
            imageSizingAndOrientationModalOrientationContainer.classList.remove('manual');
            imageSizingAndOrientationModalOrientationContainer.classList.remove('auto');

            const imageSizingAndOrientationModalOrientationText = document.getElementById('image-sizing-and-orientation-modal-orientation-text');

            if (apiData.image_settings.orientation_control == 'manual') {

                imageSizingAndOrientationModalOrientationContainer.classList.add('manual');

                if (apiData.image_settings.orientation == 'landscape') {
                    imageSizingAndOrientationModalOrientationText.innerText = 'Landscape (manual)';
                } else {
                    imageSizingAndOrientationModalOrientationText.innerText = 'Portrait (manual)';
                }

                imageSizingAndOrientationModalOrientationContainer.addEventListener(
                    'click',
                    function () {

                        let orientationSettings = {
                            'orientation': 'landscape'
                        };

                        if (apiData.image_settings.orientation == 'landscape') {
                            orientationSettings.orientation = 'portrait';
                        }

                        closeModals();

                        apiHandler(
                            'settings_set_image',
                            orientationSettings
                        );

                    },
                    false
                );

            } else {

                imageSizingAndOrientationModalOrientationContainer.classList.add('auto');

                if (apiData.image_settings.orientation == 'landscape') {
                    imageSizingAndOrientationModalOrientationText.innerText = 'Landscape (auto)';
                } else {
                    imageSizingAndOrientationModalOrientationText.innerText = 'Portrait (auto)';
                }

            }


            const imageSizingAndOrientationModalSizingOptionsContainer = document.getElementById('image-sizing-and-orientation-modal-sizing-options-container');
            const imageSizingAndOrientationModalSizingOptions = imageSizingAndOrientationModalSizingOptionsContainer.querySelectorAll('.image-sizing-and-orientation-modal-sizing-option');

            for (const imageSizingAndOrientationModalSizingOption of imageSizingAndOrientationModalSizingOptions) {

                imageSizingAndOrientationModalSizingOption.classList.remove('active');

                if (apiData.image_settings.sizing['type'] == imageSizingAndOrientationModalSizingOption.dataset.sizingType) {
                    if (apiData.image_settings.sizing['type'] == 'fit') {
                        if (apiData.image_settings.sizing['fill'] == imageSizingAndOrientationModalSizingOption.dataset.sizingFill) {
                            imageSizingAndOrientationModalSizingOption.classList.add('active');
                        }
                    } else {
                        imageSizingAndOrientationModalSizingOption.classList.add('active');
                    }
                }

            }


            const sizingContainers = document.getElementsByClassName('sizing-container');

            for (const sizingContainer of sizingContainers) {

                sizingContainer.classList.remove('frame-landscape');
                sizingContainer.classList.remove('frame-portrait');

                if (apiData.image_settings.orientation == 'landscape') {
                    sizingContainer.classList.add('frame-landscape');
                } else {
                    sizingContainer.classList.add('frame-portrait');
                }

                if (!sizingContainer.classList.contains('static-sizing')) {

                    sizingContainer.classList.remove('sizing-fit-blur');
                    sizingContainer.classList.remove('sizing-fit-blank');
                    sizingContainer.classList.remove('sizing-cover');

                    if (apiData.image_settings.sizing['type'] == 'fit') {
                        if (apiData.image_settings.sizing['fill'] == 'blur') {
                            sizingContainer.classList.add('sizing-fit-blur');
                        } else {
                            sizingContainer.classList.add('sizing-fit-blank');
                        }
                    } else if (apiData.image_settings.sizing['type'] == 'cover') {
                        sizingContainer.classList.add('sizing-cover');
                    }

                }

            }

        },
        false
    );

}

function initEditImageModal() {

    const editImageModalShowButton = document.getElementById('edit-image-modal-show-button');

    editImageModalShowButton.addEventListener(
        'click',
        function () {

            if (Object.keys(apiData).includes('image_data')) {

                const imageIdCell = document.getElementById('edit-image-modal-attribute-table-id-cell');

                const imageId = parseInt(imageIdCell.innerText);

                apiHandler(
                    'image_display',
                    {
                        'action': 'set',
                        'id': imageId
                    }
                );

                closeModals();

            }

        },
        false
    );


    const editImageModalCancelButton = document.getElementById('edit-image-modal-cancel-button');

    editImageModalCancelButton.addEventListener(
        'click',
        function () {

            closeModals();

        },
        false
    );


    if (window.initEditImageModalExtended) {

        initEditImageModalExtended();

    }

}
function displayEditImageModal(imageId) {

    if (Object.keys(apiData).includes('image_data')) {

        for (const imageData of apiData.image_data) {

            if (imageData.id == imageId) {

                const editImageModalAttributeTableBody = document.getElementById('edit-image-modal-attribute-table-body');

                const attributeCells = editImageModalAttributeTableBody.querySelectorAll('tr > td');

                for (const attributeCell of attributeCells) {

                    attributeCell.innerText = imageData[attributeCell.dataset.key];

                }


                const editImageModalImageHolder = document.getElementById('edit-image-modal-image-holder');

                editImageModalImageHolder.innerHTML = '';

                let originalImgHtml = `<img class="active" data-index="1" src="${imageData.url}" alt="${imageData.file}" />`;

                editImageModalImageHolder.insertAdjacentHTML('beforeend', originalImgHtml);

                quantizationProfiles = [
                    'landscape_fit_blur',
                    'portrait_fit_blur',
                    'landscape_fit_blank',
                    'portrait_fit_blank',
                    'landscape_cover',
                    'portrait_cover'
                ];

                for (var i = 0; i < quantizationProfiles.length; i++) {

                    for (const imageDataQuantization of imageData.quantizations) {

                        if (imageDataQuantization.url.includes(quantizationProfiles[i])) {

                            let quantizationImgHtml = `<img data-index="${i + 2}" src="${imageDataQuantization.url}" alt="${imageData.file}" />`;

                            editImageModalImageHolder.insertAdjacentHTML('beforeend', quantizationImgHtml);

                        }

                    }

                }


                const editImageModalDescriptionInput = document.getElementById('edit-image-modal-description-input');

                editImageModalDescriptionInput.value = imageData.description;
                editImageModalDescriptionInput.dataset.originalValue = imageData.description;


                const editImageModalImageHolderImgs = editImageModalImageHolder.querySelectorAll('img');

                for (const editImageModalImageHolderImg of editImageModalImageHolderImgs) {

                    editImageModalImageHolderImg.addEventListener(
                        'click',
                        function (e) {

                            let nextIndex = parseInt(e.target.dataset.index) + 1;

                            const editImageModalImageHolder = document.getElementById('edit-image-modal-image-holder');

                            const editImageModalImageHolderImgs = editImageModalImageHolder.querySelectorAll('img');

                            if (nextIndex > editImageModalImageHolderImgs.length) {

                                nextIndex = 0;

                            }

                            for (const editImageModalImageHolderImg of editImageModalImageHolderImgs) {

                                editImageModalImageHolderImg.classList.remove('active');

                                if (parseInt(editImageModalImageHolderImg.dataset.index) == nextIndex) {

                                    editImageModalImageHolderImg.classList.add('active');

                                }

                            }

                        },
                        false
                    );

                }


                populateTags(
                    'edit-image-modal-tag-holder',
                    imageTags = imageData.tags,
                    imageId = imageData.id
                );


                const editImageModal = document.getElementById('edit-image-modal');
                editImageModal.classList.add('active');


                break;

            }

        }

    }

}

function populateTags(parentId, imageTags = null, imageId = null, tagFilters = null, filterType = null) {

    if (Object.keys(apiData).includes('category_data')) {

        const parent = document.getElementById(parentId);

        parent.innerHTML = '';


        for (const categoryData of apiData.category_data) {

            let checkState = 0;
            let tagAttribute = '';

            if (imageTags !== null && imageId !== null) {

                tagAttribute = ` data-image-id="${imageId}"`;

                for (const imageTag of imageTags) {

                    if (imageTag.category.id == categoryData.id) {

                        if (Object.keys(imageTag).includes('subcategory')) {

                            checkState = 2;

                        } else {

                            checkState = 1;

                        }

                        break;

                    }

                }

            } else if (tagFilters !== null && filterType !== null) {

                tagAttribute = ` data-type="${filterType}"`;

                for (const tagFilter of tagFilters) {

                    if (tagFilter.category.id == categoryData.id && tagFilter.type == filterType) {

                        if (Object.keys(tagFilter).includes('subcategory')) {

                            checkState = 2;

                        } else {

                            checkState = 1;

                        }

                        break;

                    }

                }

            }


            let tagHtml = `<div class="tag category" data-value="${checkState}" data-original-value="${checkState}"${tagAttribute} data-category-id="${categoryData.id}" data-category-name="${categoryData.name}"><div class="checkbox" data-value="${checkState}"></div><span>${categoryData.name}</span></div>`;

            parent.insertAdjacentHTML('beforeend', tagHtml);


            if (Object.keys(categoryData).includes('subcategories')) {

                for (const subcategoryData of categoryData.subcategories) {

                    checkState = 0;

                    if (imageTags !== null && imageId !== null) {

                        for (const imageTag of imageTags) {

                            if (imageTag.category.id == categoryData.id) {

                                if (Object.keys(imageTag).includes('subcategory')) {

                                    if (imageTag.subcategory.id == subcategoryData.id) {

                                        checkState = 1;

                                        break;

                                    }

                                }

                            }

                        }

                    } else if (tagFilters !== null && filterType !== null) {

                        for (const tagFilter of tagFilters) {

                            if (tagFilter.category.id == categoryData.id && tagFilter.type == filterType) {

                                if (Object.keys(tagFilter).includes('subcategory')) {

                                    if (tagFilter.subcategory.id == subcategoryData.id) {

                                        checkState = 1;

                                        break;

                                    }

                                }

                            }

                        }

                    }

                    tagHtml = `<div class="tag subcategory" data-value="${checkState}" data-original-value="${checkState}"${tagAttribute} data-category-id="${categoryData.id}" data-category-name="${categoryData.name}" data-subcategory-id="${subcategoryData.id}" data-subcategory-name="${subcategoryData.name}"><div class="checkbox" data-value="${checkState}"></div><span>${categoryData.name} > ${subcategoryData.name}</span></div>`;

                    parent.insertAdjacentHTML('beforeend', tagHtml);

                }

            }

        }


        const tags = parent.querySelectorAll('.tag');

        for (const tag of tags) {

            tag.addEventListener(
                'click',
                function (e) {

                    if (e.target.classList.contains('tag')) {

                        const tag = e.target;

                        const originalValue = parseInt(tag.dataset.value);

                        let newValue = 1;

                        if (originalValue == 1) {

                            newValue = 0;

                        }

                        tag.dataset.value = newValue;

                        const tagCheckbox = tag.querySelector('.checkbox');

                        tagCheckbox.dataset.value = newValue;


                        if (tag.classList.contains('category')) {

                            const subcategories = tag.parentElement.querySelectorAll(`.tag.subcategory[data-category-id="${tag.dataset.categoryId}"]`);

                            for (const subcategory of subcategories) {

                                subcategory.dataset.value = newValue;

                                const subcategoryCheckbox = subcategory.querySelector('.checkbox');

                                subcategoryCheckbox.dataset.value = newValue;

                            }

                        } else {

                            let categoryValue = newValue;

                            const subcategories = tag.parentElement.querySelectorAll(`.tag.subcategory[data-category-id="${tag.dataset.categoryId}"]`);

                            for (const subcategory of subcategories) {

                                if (parseInt(subcategory.dataset.value) !== newValue) {

                                    categoryValue = 2;

                                    break;

                                }

                            }

                            const category = tag.parentElement.querySelector(`.tag.category[data-category-id="${tag.dataset.categoryId}"]`);

                            category.dataset.value = categoryValue;

                            const categoryCheckbox = category.querySelector('.checkbox');

                            categoryCheckbox.dataset.value = categoryValue;

                        }

                    } else {

                        e.target.parentElement.click();

                    }

                },
                false
            );

        }

    }

}
function tagSelectionChanged(parentId) {

    let selectionChanged = false;

    const parent = document.getElementById(parentId);

    const tags = parent.querySelectorAll('.tag');

    for (const tag of tags) {

        if (tag.dataset.value !== tag.dataset.originalValue) {

            selectionChanged = true;

            break;

        }

    }


    return selectionChanged;

}
function getSelectedTags(parentId) {

    let selectedTags = [];

    const parent = document.getElementById(parentId);

    const tags = parent.querySelectorAll('.tag');


    let returnFormat = null;

    if (tags.length > 0) {

        if (tags[0].hasAttribute('data-image-id')) {

            returnFormat = 'tag';

        } else if (tags[0].hasAttribute('data-image-id')) {

            returnFormat = 'filter';

        }

    }


    let selectedCategoryIds = [];

    if (returnFormat !== null) {

        for (const tag of tags) {

            if (tag.classList.contains('category')) {

                if (parseInt(tag.dataset.value) == 1) {

                    if (returnFormat == 'tag') {

                        selectedTags.push(
                            {
                                'image_id': parseInt(tag.dataset.imageId),
                                'category_id': parseInt(tag.dataset.categoryId)
                            }
                        );

                    } else if (returnFormat == 'filter') {

                        selectedTags.push(
                            {
                                'type': parseInt(tag.dataset.type),
                                'category': {
                                    'id': parseInt(tag.dataset.categoryId),
                                    'name': parseInt(tag.dataset.categoryName)
                                }
                            }
                        );

                    }

                    selectedCategoryIds.push(parseInt(tag.dataset.categoryId));

                }

            } else if (tag.classList.contains('subcategory')) {

                if (!selectedCategoryIds.includes(parseInt(tag.dataset.categoryId))) {

                    if (parseInt(tag.dataset.value) == 1) {

                        if (returnFormat == 'tag') {

                            selectedTags.push(
                                {
                                    'image_id': parseInt(tag.dataset.imageId),
                                    'category_id': parseInt(tag.dataset.categoryId),
                                    'subcategory_id': parseInt(tag.dataset.subcategoryId)
                                }
                            );

                        } else if (returnFormat == 'filter') {

                            selectedTags.push(
                                {
                                    'type': parseInt(tag.dataset.type),
                                    'category': {
                                        'id': parseInt(tag.dataset.categoryId),
                                        'name': parseInt(tag.dataset.categoryName)
                                    },
                                    'subcategory': {
                                        'id': parseInt(tag.dataset.subcategoryId),
                                        'name': parseInt(tag.dataset.subcategoryName)
                                    }
                                }
                            );

                        }

                    }

                }

            }

        }

    }


    return selectedTags;

}

function initThumbnails() {

    document.addEventListener(
        'image_data',
        populateThumbnails,
        false
    );

    document.addEventListener(
        'image_settings',
        populateThumbnails,
        false
    );

}
function populateThumbnails() {

    if (Object.keys(apiData).includes('image_data')) {

        const imageGallery = document.getElementById('image-gallery');

        imageGallery.innerHTML = '';

        for (const imageData of apiData.image_data) {

            let sortedThumbs = imageData.thumbnails.sort(
                function (a, b) {
                    return ((a.width < b.width) ? -1 : ((a.width > b.width) ? 1 : 0));
                }
            );

            let thumbSrcset = [];
            let thumbSizes = [];
            let thumbSrc = '';

            for (var i = 0; i < sortedThumbs.length; i++) {

                thumbSrcset.push(
                    `${sortedThumbs[i].url} ${sortedThumbs[i].width}w`
                );

                if (i == (sortedThumbs.length - 1)) {

                    thumbSizes.push(
                        `${sortedThumbs[i].width}px`
                    );

                } else {

                    thumbSizes.push(
                        `(max-width: ${sortedThumbs[i].width}px) ${sortedThumbs[i].width}px`
                    );

                }

                thumbSrc = sortedThumbs[i].url;

            }

            let thumbnailHtml = `<div class="thumbnail" data-id="${imageData.id}" data-created="${imageData.created}" data-ingested="${imageData.ingested}" data-file="${imageData.file}"><img srcset="${thumbSrcset.join(', ')}" sizes="${thumbSizes.join(', ')}" src="${thumbSrc}" alt="${imageData.file}" /></div>`;

            imageGallery.insertAdjacentHTML('beforeend', thumbnailHtml);

        }


        setThumbnailEventListeners();

    }


    filterAndSortThumbnails();

}
function filterAndSortThumbnails() {

    const imageGallery = document.getElementById('image-gallery');

    const thumbnails = imageGallery.querySelectorAll('.thumbnail');


    /* Filter */

    if (Object.keys(apiData).includes('image_settings') && Object.keys(apiData).includes('image_data')) {

        for (const thumbnail of thumbnails) {

            thumbnail.classList.remove('available');

            const imageId = parseInt(thumbnail.dataset.id);


            if (imageId == apiData.image_settings.current) {

                thumbnail.classList.add('current');

            }


            if (apiData.image_settings.filters.length == 0) {

                thumbnail.classList.add('available');

            } else {

                for (const imageData of apiData.image_data) {

                    if (imageData.id == imageId) {

                        let thumbnailAvailable = false;

                        for (const includeFilter of apiData.image_settings.filters) {

                            if (includeFilter.type == 'include') {

                                for (const imageTag of imageData.tags) {

                                    if (Object.keys(includeFilter).includes('subcategory')) {

                                        if (Object.keys(imageTag).includes('subcategory')) {

                                            if (imageTag.category.id == includeFilter.category.id && imageTag.subcategory.id == includeFilter.subcategory.id) {

                                                thumbnailAvailable = true;

                                            }

                                        }

                                    } else {

                                        if (!Object.keys(imageTag).includes('subcategory')) {

                                            if (imageTag.category.id == includeFilter.category.id) {

                                                thumbnailAvailable = true;

                                            }

                                        }

                                    }

                                }

                            }

                        }

                        if (thumbnailAvailable == true) {

                            for (const excludeFilter of apiData.image_settings.filters) {

                                if (includeFilter.type == 'exclude') {

                                    for (const imageTag of imageData.tags) {

                                        if (Object.keys(excludeFilter).includes('subcategory')) {

                                            if (Object.keys(imageTag).includes('subcategory')) {

                                                if (imageTag.category.id == excludeFilter.category.id && imageTag.subcategory.id == excludeFilter.subcategory.id) {

                                                    thumbnailAvailable = false;

                                                }

                                            }

                                        } else {

                                            if (imageTag.category.id == excludeFilter.category.id) {

                                                thumbnailAvailable = false;

                                            }

                                        }

                                    }

                                }

                            }

                        }


                        if (thumbnailAvailable == true) {

                            thumbnail.classList.add('available');

                        }

                        break;

                    }

                }

            }

        }

    }


    /* Sort */

    if (Object.keys(apiData).includes('image_data')) {

        let sortKey = null;
        let sortDirection = null;

        const filterAndSortImagesModalSortSelect = document.getElementById('filter-and-sort-images-modal-sort-select');

        const filterAndSortImagesModalSortSelectOptions = filterAndSortImagesModalSortSelect.querySelectorAll('.accordian-select-option');

        for (const filterAndSortImagesModalSortSelectOption of filterAndSortImagesModalSortSelectOptions) {

            if (filterAndSortImagesModalSortSelectOption.classList.contains('active')) {

                sortKey = filterAndSortImagesModalSortSelectOption.dataset.key;
                sortDirection = filterAndSortImagesModalSortSelectOption.dataset.direction;

                break;

            }

        }


        if (sortKey !== null && sortDirection !== null) {

            let thumbnails = Array.from(imageGallery.children);

            let thumbnailsSorted = thumbnails.sort(function (a, b) {
                return +a.dataset[sortKey] - +b.dataset[sortKey]
            });

            if (sortDirection == 'desc') {

                thumbnailsSorted = thumbnailsSorted.reverse();

            }

            imageGallery.innerHTML = '';

            thumbnailsSorted.forEach(element => imageGallery.append(element));

            setThumbnailEventListeners();

        }

    }

}
function setThumbnailEventListeners() {

    const imageGallery = document.getElementById('image-gallery');

    const thumbnails = imageGallery.querySelectorAll('.thumbnail');

    for (const thumbnail of thumbnails) {

        clearEventListenersByElement(thumbnail.querySelector('img'));

        const thumbnailImg = thumbnail.querySelector('img');

        thumbnailImg.addEventListener(
            'click',
            function (e) {

                const thumbnail = e.target.parentElement;

                displayEditImageModal(
                    parseInt(thumbnail.dataset.id)
                );

            },
            true
        );

    }

}

function initSearch() {

    const searchButton = document.getElementById('search-button');

    searchButton.addEventListener(
        'click',
        function () {

            const searchResults = document.getElementById('search-images-modal-results');

            searchResults.innerHTML = '';


            const searchInput = document.getElementById('search-images-modal-input');

            searchInput.value = '';


            const searchImagesModal = document.getElementById('search-images-modal');

            searchImagesModal.classList.add('active');


            searchInput.focus();

        },
        false
    );


    const searchInput = document.getElementById('search-images-modal-input');

    searchInput.addEventListener(
        'keyup',
        function () {
            searchImages();
        },
        false
    );


    const searchCancel = document.getElementById('search-images-modal-cancel');

    searchCancel.addEventListener(
        'click',
        function () {
            closeModals();
        },
        false
    );

}
function searchImages() {

    if (Object.keys(apiData).includes('image_data')) {

        const searchResults = document.getElementById('search-images-modal-results');
        searchResults.innerHTML = '';

        const searchInput = document.getElementById('search-images-modal-input');

        const searchValue = searchInput.value;

        if (searchValue.length > 0) {

            let imageSearch = [];

            for (const imageData of apiData.image_data) {

                let sortedThumbs = imageData.thumbnails.sort(
                    function (a, b) {
                        return ((a.width < b.width) ? -1 : ((a.width > b.width) ? 1 : 0));
                    }
                );

                let imageInfo = {
                    'id': imageData.id,
                    'thumbnail': sortedThumbs[0].url,

                    'description': imageData.description,
                    'description_distance': levenshteinDistance(searchValue, imageData.description),

                    'file': imageData.file,
                    'file_distance': levenshteinDistance(searchValue, imageData.file),

                    'tag': '',
                    'tag_distance': 5000
                };

                let tagDistances = [];

                for (const imageTag of imageData.tags) {

                    let tagDistance = {
                        'tag': '',
                        'distance': 5000
                    };

                    if (Object.keys(imageTag).includes('subcategory')) {

                        tagDistance.tag = imageTag.subcategory.name;
                        tagDistance.distance = levenshteinDistance(searchValue, imageTag.subcategory.name);

                    } else if (Object.keys(imageTag).includes('category')) {

                        tagDistance.tag = imageTag.category.name;
                        tagDistance.distance = levenshteinDistance(searchValue, imageTag.category.name);

                    }

                    tagDistances.push(tagDistance);

                }

                for (const tagDistance of tagDistances) {

                    if (tagDistance.distance < imageInfo.tag_distance) {

                        imageInfo.tag = tagDistance.tag;
                        imageInfo.tag_distance = tagDistance.distance;

                    }

                }

                imageSearch.push(imageInfo);

            }


            const resultsOfTypeCount = 3;

            let searchDescriptions = imageSearch.sort(
                function (a, b) {
                    return ((a.description_distance < b.description_distance) ? -1 : ((a.description_distance > b.description_distance) ? 1 : 0));
                }
            );
            let searchResultsHtml = '';
            for (var i = 0; i < resultsOfTypeCount; i++) {

                if (i < imageSearch.length) {

                    if (searchDescriptions[i].description.length > 0) {

                        searchResultsHtml = searchResultsHtml + `<div class="image-search-result" data-image-id="${searchDescriptions[i].id}"><div class="image-search-result-thumb" style="background-image: url('${searchDescriptions[i].thumbnail}');"></div><span>${searchDescriptions[i].description}</span></div>`;

                    }

                }

            }
            if (searchResultsHtml.length > 0) {
                searchResults.insertAdjacentHTML('beforeend', '<span>Description results...</span>');
                searchResults.insertAdjacentHTML('beforeend', searchResultsHtml);
            }

            if (imageSearch.length > 0) {
                searchResults.insertAdjacentHTML('beforeend', '<span>File name results...</span>');
            }
            let searchFiles = imageSearch.sort(
                function (a, b) {
                    return ((a.file_distance < b.file_distance) ? -1 : ((a.file_distance > b.file_distance) ? 1 : 0));
                }
            );
            for (var i = 0; i < resultsOfTypeCount; i++) {

                if (i < imageSearch.length) {

                    let searchResultHtml = `<div class="image-search-result" data-image-id="${searchFiles[i].id}"><div class="image-search-result-thumb" style="background-image: url('${searchFiles[i].thumbnail}');"></div><span>${searchFiles[i].file}</span></div>`;
                    searchResults.insertAdjacentHTML('beforeend', searchResultHtml);

                }

            }

            let searchTags = searchDescriptions.sort(
                function (a, b) {
                    return ((a.tag_distance < b.tag_distance) ? -1 : ((a.tag_distance > b.tag_distance) ? 1 : 0));
                }
            );
            searchResultsHtml = '';
            for (var i = 0; i < resultsOfTypeCount; i++) {

                if (i < imageSearch.length) {

                    if (searchTags[i].tag.length > 0) {

                        searchResultsHtml = searchResultsHtml + `<div class="image-search-result" data-image-id="${searchTags[i].id}"><div class="image-search-result-thumb" style="background-image: url('${searchTags[i].thumbnail}');"></div><span>${searchTags[i].tag}</span></div>`;

                    }

                }

            }
            if (searchResultsHtml.length > 0) {
                searchResults.insertAdjacentHTML('beforeend', '<span>Tag results...</span>');
                searchResults.insertAdjacentHTML('beforeend', searchResultsHtml);
            }


            const searchResultItems = searchResults.querySelectorAll('.image-search-result');

            for (const searchResultItem of searchResultItems) {

                searchResultItem.addEventListener(
                    'click',
                    function (e) {

                        closeModals();

                        let imageId = -1;

                        if (e.target.classList.contains('image-search-result')) {

                            imageId = e.target.dataset.imageId;

                        } else {

                            imageId = e.target.parentElement.dataset.imageId;

                        }

                        displayEditImageModal(imageId);

                    },
                    false
                );

            }

        }

    }

}
function levenshteinDistance(s0, s1) {

    if (!s0.length) return s1.length;
    if (!s1.length) return s0.length;

    const arr = [];

    for (let i = 0; i <= s1.length; i++) {

        arr[i] = [i];

        for (let j = 1; j <= s0.length; j++) {

            if (i === 0) {

                arr[i][j] = j;

            } else {

                arr[i][j] = Math.min(
                    arr[i - 1][j] + 1,
                    arr[i][j - 1] + 1,
                    arr[i - 1][j - 1] + (s0[j - 1] === s1[i - 1] ? 0 : 1)
                );

            }

        }

    }

    return arr[s1.length][s0.length];

}
