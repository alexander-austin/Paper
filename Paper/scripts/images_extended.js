/*
    Copyright (c) 2024, Alexander Austin
    All rights reserved.

    This source code is licensed under the BSD-style license found in the
    LICENSE file in the root directory of this source tree.
*/


function initDisplayAdd() {

    const displayAdd = document.getElementById('display-add');

    displayAdd.addEventListener(
        'click',
        function () {

            const addImagesModalFileInput = document.getElementById('add-images-modal-file-input');

            addImagesModalFileInput.value = '';


            const addImagesModalPreviewContainer = document.getElementById('add-images-modal-preview-container');

            addImagesModalPreviewContainer.innerHTML = '';


            const addImagesModal = document.getElementById('add-images-modal');

            addImagesModal.classList.add('active');

        },
        true
    );


    const addImagesModalFileInput = document.getElementById('add-images-modal-file-input');

    addImagesModalFileInput.addEventListener(
        'change',
        function (e) {

            const addImagesModalFileInput = e.target;


            const addImagesModalPreviewContainer = document.getElementById('add-images-modal-preview-container');

            addImagesModalPreviewContainer.innerHTML = '';

            for (var i = 0; i < addImagesModalFileInput.files.length; i++) {

                let previewImgHtml = `<img id="add-images-modal-preview-img-${i}" alt="${addImagesModalFileInput.files[i].name}" />`;
                let previewNameHtml = `<span>${addImagesModalFileInput.files[i].name}</span>`;
                let previewDescriptionInputHtml = `<input id="add-images-modal-description-input" type="text" placeholder="Add image description..." value="" data-original-value="" autocomplete="off" autocorrect="off" maxlength="256" />`;
                let previewTagContainerHtml = `<div class="upload-preview-tag-container"><div id="add-images-modal-preview-tag-container-inner-${i}" class="upload-preview-tag-container-inner"></div></div>`;

                addImagesModalPreviewContainer.insertAdjacentHTML('beforeend', `<div class="upload-preview" data-file-name="${addImagesModalFileInput.files[i].name}">${previewImgHtml}${previewNameHtml}${previewDescriptionInputHtml}${previewTagContainerHtml}</div>`);


                const previewImage = document.getElementById(`add-images-modal-preview-img-${i}`);

                previewImage.src = URL.createObjectURL(addImagesModalFileInput.files[i]);

                previewImage.addEventListener(
                    'load',
                    function (e) {

                        URL.revokeObjectURL(e.target.src);

                    },
                    false
                );


                populateTags(`add-images-modal-preview-tag-container-inner-${i}`, imageTags = [], imageId = i);

            }

        },
        false
    );


    const addImagesModalFileButton = document.getElementById('add-images-modal-file-button');

    addImagesModalFileButton.addEventListener(
        'click',
        function () {

            const addImagesModalFileInput = document.getElementById('add-images-modal-file-input');

            addImagesModalFileInput.click();

        },
        true
    );


    const addImagesModalUploadButton = document.getElementById('add-images-modal-upload-button');

    addImagesModalUploadButton.addEventListener(
        'click',
        function () {

            const chunkSize = getChunkSize();

            let fileUploads = [];


            const addImagesModalFileInput = document.getElementById('add-images-modal-file-input');


            const addImagesModalPreviewContainer = document.getElementById('add-images-modal-preview-container');

            const uploadPreviews = addImagesModalPreviewContainer.querySelectorAll('.upload-preview');

            for (var i = 0; i < addImagesModalFileInput.files.length; i++) {

                let fileUpload = {
                    'index': i,
                    'name': addImagesModalFileInput.files[i].name,
                    'size': addImagesModalFileInput.files[i].size,
                    'chunks': Math.ceil(addImagesModalFileInput.files[i].size / chunkSize),
                    'file': addImagesModalFileInput.files[i]
                };

                for (const uploadPreview of uploadPreviews) {

                    if (uploadPreview.dataset.fileName == fileUpload.name) {

                        const descriptionInput = uploadPreview.querySelector('input');

                        if (descriptionInput.value.trim().length > 0) {

                            fileUpload['description'] = descriptionInput.value.trim();

                        }


                        const uploadPreviewTagContainerInner = uploadPreview.querySelector('.upload-preview-tag-container > .upload-preview-tag-container-inner');

                        const previewTags = getSelectedTags(uploadPreviewTagContainerInner.id);

                        if (previewTags.length > 0) {

                            fileUpload['tags'] = previewTags;

                        }

                        break;

                    }

                }

                fileUploads.push(fileUpload);

            }

            fileHandler(fileUploads);


            closeModals();

        },
        true
    );


    const addImagesModalCancelButton = document.getElementById('add-images-modal-cancel-button');

    addImagesModalCancelButton.addEventListener(
        'click',
        function () {

            closeModals();

        },
        false
    );

}

function initEditImageModalExtended() {

    const editImageModalSaveButton = document.getElementById('edit-image-modal-save-button');

    editImageModalSaveButton.addEventListener(
        'click',
        function () {

            if (Object.keys(apiData).includes('image_data') && Object.keys(apiData).includes('category_data')) {

                const imageIdCell = document.getElementById('edit-image-modal-attribute-table-id-cell');

                const imageId = parseInt(imageIdCell.innerText);

                apiHandler(
                    'image_edit',
                    {
                        'id': imageId,
                        'tags': getSelectedTags('edit-image-modal-tag-holder')
                    }
                );


                const editImageModalDescriptionInput = document.getElementById('edit-image-modal-description-input');

                if (editImageModalDescriptionInput.value.trim() !== editImageModalDescriptionInput.dataset.originalValue) {

                    apiHandler(
                        'image_edit',
                        {
                            'id': imageId,
                            'description': editImageModalDescriptionInput.value.trim()
                        }
                    );

                }

                closeModals();

            }

        },
        false
    );


    const editImageModalDeleteButton = document.getElementById('edit-image-modal-delete-button');

    editImageModalDeleteButton.addEventListener(
        'click',
        function () {

            if (Object.keys(apiData).includes('image_data')) {


                const imageIdCell = document.getElementById('edit-image-modal-attribute-table-id-cell');

                const imageId = parseInt(imageIdCell.innerText);

                if (window.confirm('Are you sure you want to permanently delete this image?')) {

                    apiHandler(
                        'image_delete',
                        {
                            'id': imageId
                        }
                    );

                    closeModals();

                }

            }

        },
        false
    );

}
