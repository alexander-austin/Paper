#  Copyright (c) 2024, Alexander Austin
#  All rights reserved.
#
#  This source code is licensed under the BSD-style license found in the
#  LICENSE file in the root directory of this source tree.


#!/usr/bin/python3.12
# -*- coding: utf-8 -*-


import base64, datetime, glob, json, os, subprocess, sys
from Paper.DB import DB, DbCategory, DbImage, DbInfo, DbPermission, DbTask, DbToken, DbUser, DbUserPermission
from Paper.Display import Display
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import pillow_avif
from pillow_heif import register_heif_opener


class Backend:


    def __init__(self):
        """Initialize."""

        self.logFileKey = 'backend_log'
        self.db = DB()

        self.generatePalette()

        self.display = Display()


        return
    def generatePalette(self):
        """Generate quantization palette."""

        try:

            imageSettings = self.db.settings.get('image')
            
            paletteSettings = imageSettings['palette']

            paletteRgb = [
                paletteSettings[colorKey]
                for colorKey in paletteSettings.keys()
            ]


            self.palette = Image.new(
                'P',
                (1, 1)
            )
            self.palette.putpalette(
                tuple(
                    [
                        val
                        for color in paletteRgb
                        for val in color
                    ] + [0, 0, 0] * (
                        256 - len(paletteRgb)
                    )
                )
            )

        except Exception as e:

            self.db.log(
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


    def ingestLocalImages(self):
        """Ingest manually transferred images in temp path."""

        statusMessage = {'error': 'Server error'}
        statusCode = 500

        try:

            dbImages = self.db.get(
                dbObjectType='image',
                match=None
            )


            dbImagePaths = []

            if not dbImages is None:

                if isinstance(dbImages, DbImage):

                    dbImagePaths = [
                        dbImages.working['path']
                    ]

                if isinstance(dbImages, list):

                    dbImagePaths = [
                        dbImage.working['path']
                        for dbImage in dbImages
                    ]
                    
            del dbImages


            localImages = glob.glob(
                os.path.join(
                    self.db.paths['local']['path'],
                    '*'
                )
            )


            newImages = []

            for localImage in localImages:

                if not localImage in dbImagePaths:

                    newImages.append(
                        self.ingestImage(
                            imagePath=localImage,
                            tags=[],
                            description=''
                        )
                    )


            if len(newImages) > 0:

                self.db.settings.generateMediaQueue()


            del dbImagePaths
            del localImages
            del newImages

            statusMessage = {'status': 'ok'}
            statusCode = 200

        except Exception as e:

            self.db.log(
                self.logFileKey,
                '.'.join(
                    [
                        str(self.__class__.__name__),
                        str(sys._getframe().f_code.co_name)
                    ]
                ),
                str(e)
            )


        return statusMessage, statusCode
    def processUploadChunk(self, fileInfo, fileBytes):
        """Process uploaded file chunks."""

        uploadProgress = {'error': 'Bad request'}
        statusCode = 400

        try:

            if isinstance(fileInfo, dict):

                if 'info' in fileInfo.keys() and 'current' in fileInfo.keys():

                    if 'index' in fileInfo['current'] and 'chunk' in fileInfo['current']:

                        overallProgress = []
                        currentFileName = None

                        for i in range(len(fileInfo['info'])):

                            if all([infoKey in fileInfo['info'][i].keys() for infoKey in ['index', 'name', 'size', 'chunks']]) == True:

                                storageNames = self.getStorageNames(
                                    fileInfo['info'][i]['name'],
                                    fileInfo['info'][i]['chunks']
                                )

                                if fileInfo['info'][i]['index'] == fileInfo['current']['index']:

                                    currentFileName = fileInfo['info'][i]['name']

                                    fileBytes.save(
                                        storageNames['chunks'][fileInfo['current']['chunk']] if fileInfo['info'][i]['chunks'] > 1 else storageNames['temp']
                                    )


                                fileProgress = {
                                    'index': fileInfo['info'][i]['index'],
                                    'name': fileInfo['info'][i]['name'],
                                    'size': fileInfo['info'][i]['size'],
                                    'chunks': fileInfo['info'][i]['chunks'],
                                    'progress': 0.0
                                }

                                if os.path.exists(storageNames['original']):

                                    fileProgress['progress'] = 100.0

                                else:

                                    existingChunks = [
                                        chunkPath
                                        for chunkPath in storageNames['chunks']
                                        if os.path.exists(chunkPath)
                                    ]

                                    if len(existingChunks) == fileInfo['info'][i]['chunks']:

                                        fileProgress['progress'] = 100.0

                                        if fileInfo['info'][i]['index'] == fileInfo['current']['index']:

                                            if fileInfo['info'][i]['chunks'] > 1:

                                                with open(storageNames['temp'], 'wb') as wF:

                                                    for c in range(len(storageNames['chunks'])):

                                                        if os.path.exists(storageNames['chunks'][c]):

                                                            with open(storageNames['chunks'][c], 'rb') as rF:

                                                                wF.write(rF.read())

                                                            try: os.remove(storageNames['chunks'][c])
                                                            except: pass

                                            self.ingestImage(
                                                storageNames['temp'],
                                                tags=[] if not 'tags' in fileInfo['info'][i].keys() else fileInfo['info'][i]['tags'],
                                                description='' if not 'description' in fileInfo['info'][i].keys() else fileInfo['info'][i]['description']
                                            )

                                    else:

                                        fileProgress['progress'] = (len(existingChunks) / fileInfo['info'][i]['chunks']) * 100.0


                                overallProgress.append(fileProgress)


                        uploadProgress = {
                            'progress': overallProgress,
                            'current_file': currentFileName
                        }
                        statusCode = 200

        except Exception as e:

            self.db.log(
                self.logFileKey,
                '.'.join(
                    [
                        str(self.__class__.__name__),
                        str(sys._getframe().f_code.co_name)
                    ]
                ),
                str(e)
            )


        return uploadProgress, statusCode
    def getStorageNames(self, uploadName, chunks):
        """Gets server safe storage names."""

        storageNames = {
            'upload': uploadName,
            'temp': None,
            'original': None,
            'chunks': [],
        }

        if isinstance(uploadName, str):

            workingName = uploadName

            for c in workingName:

                if not c in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-()':

                    workingName = workingName.replace(c, '_')

            while workingName[0] in '.-_' or workingName[-1] in '.-_':

                workingName = workingName.strip('.').strip('-').strip('_')

            while '..' in workingName:

                workingName = workingName.replace('..', '.')

            for c in workingName:

                if not c in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-()':

                    workingName = workingName.replace(c, '_')


            if len(workingName) > 3 and '.' in workingName:

                storageNames['temp'] = os.path.join(
                    self.db.paths['temp']['path'],
                    workingName
                )

                storageNames['original'] = os.path.join(
                    self.db.paths['original']['path'],
                    workingName
                )

                storageNames['chunks'] = [
                    os.path.join(
                        self.db.paths['temp']['path'],
                        '.'.join(
                            [
                                '_'.join(
                                    [
                                        workingName.rsplit('.', 1)[0],
                                        str('000' + str(c))[-3:]
                                    ]
                                ),
                                workingName.rsplit('.', 1)[-1]
                            ]
                        )
                    )
                    for c in range(chunks)
                ]


        return storageNames


    def ingestImage(self, imagePath, tags=[], description=''):
        """Ingest image."""

        dbImage = None

        try:

            if os.path.exists(imagePath):

                imageSettings = self.db.settings.get('image')


                imageWorking = {
                    'bytes': os.path.getsize(
                        imagePath
                    ),
                    'path': os.path.join(
                        self.db.paths['original']['path'],
                        imagePath.rsplit(os.sep, 1)[-1]
                    ),
                    'file': imagePath.rsplit(os.sep, 1)[-1],
                    'url': '/images/original/%s' % (
                        imagePath.rsplit(os.sep, 1)[-1],
                    ),
                    'created': min(
                        [
                            os.path.getctime(imagePath),
                            os.path.getmtime(imagePath)
                        ]
                    ),
                    'description': description
                }
                

                if os.path.exists(imageWorking['path']):

                    for i in range(sys.maxsize):

                        uniquePath = os.path.join(
                            imageWorking['path'].rsplit(os.sep, 1)[0],
                            '%(simple_name)s_%(number)i.%(extension)s' % {
                                'simple_name': imageWorking['path'].rsplit(os.sep, 1)[-1].rsplit('.', 1)[0],
                                'number': i,
                                'extension': '' if not '.' in imageWorking['path'].rsplit(os.sep, 1)[-1] else imageWorking['path'].rsplit(os.sep, 1)[-1].rsplit('.', 1)[-1]
                            }
                        )

                        if not os.path.exists(uniquePath):

                            imageWorking['path'] = uniquePath

                            break


                register_heif_opener()

                originalImage = Image.open(imagePath).convert('RGB')
                originalImage = ImageOps.exif_transpose(originalImage)

                imageWorking['width'] = originalImage.size[0]
                imageWorking['height'] = originalImage.size[1]


                with open(imageWorking['path'], 'wb') as wF:

                    with open(imagePath, 'rb') as rF:

                        wF.write(rF.read())

                try: os.remove(imagePath)
                except: pass


                dbImageTemp = self.db.new(
                    'image',
                    imageWorking
                )


                quantizationProfiles = [
                    {
                        'orientation': 'landscape',
                        'sizing': {
                            'type': 'fit',
                            'fill': 'blur'
                        }
                    }, {
                        'orientation': 'landscape',
                        'sizing': {
                            'type': 'fit',
                            'fill': 'blank'
                        }
                    }, {
                        'orientation': 'landscape',
                        'sizing': {
                            'type': 'cover'
                        }
                    }, {
                        'orientation': 'portrait',
                        'sizing': {
                            'type': 'fit',
                            'fill': 'blur'
                        }
                    }, {
                        'orientation': 'portrait',
                        'sizing': {
                            'type': 'fit',
                            'fill': 'blank'
                        }
                    }, {
                        'orientation': 'portrait',
                        'sizing': {
                            'type': 'cover'
                        }
                    }
                ]

                for quantizationProfile in quantizationProfiles:

                    self.db.new(
                        'quantization',
                        self.generateImageQuantization(
                            originalImage.copy(),
                            imageWorking['path'],
                            imageSettings,
                            quantizationProfile,
                            imageId=dbImageTemp.working['id']
                        )
                    )

                for thumbnailSize in imageSettings['thumbnail_sizes']:

                    self.db.new(
                        'thumbnail',
                        self.generateImageThumbnail(
                            originalImage.copy(),
                            imageWorking['path'],
                            imageSettings,
                            thumbnailSize,
                            imageId=dbImageTemp.working['id']
                        )
                    )

                for tag in tags:

                    self.db.new(
                        'tag',
                        {
                            'image_id': dbImageTemp.working['id'],
                            'category_id': tag['category_id'],
                            'subcategory_id': None if not 'subcategory_id' in tag.keys() else tag['subcategory_id'],
                        }
                    )



                dbImage = self.db.get(
                    'image',
                    match={
                        'id': dbImageTemp.working['id']
                    }
                )

                del originalImage
                del imageWorking
                del dbImageTemp

        except Exception as e:

            self.db.log(
                self.logFileKey,
                '.'.join(
                    [
                        str(self.__class__.__name__),
                        str(sys._getframe().f_code.co_name)
                    ]
                ),
                str(e)
            )


        return dbImage
    def generateImageQuantization(self, originalImage, originalPath, imageSettings, quantizationProfile, imageId=None):
        """Generates quantized image from original."""

        quantizationWorking = None

        try:

            destinationSize = [
                max(
                    [
                        imageSettings['size'][0],
                        imageSettings['size'][1]
                    ]
                ) if quantizationProfile['orientation'] == 'landscape' else min(
                    [
                        imageSettings['size'][0],
                        imageSettings['size'][1]
                    ]
                ),
                min(
                    [
                        imageSettings['size'][0],
                        imageSettings['size'][1]
                    ]
                ) if quantizationProfile['orientation'] == 'landscape' else max(
                    [
                        imageSettings['size'][0],
                        imageSettings['size'][1]
                    ]
                )
            ]

            imageSizing = self.getImageSizing(
                originalImage.size,
                destinationSize
            )

            quantizationInfo = {
                'width': destinationSize[0],
                'height': destinationSize[1],
                'path': os.path.join(
                    self.db.paths['quantization']['path'],
                    '%(file_name)s_%(orientation)s_%(sizing)s.%(extension)s' % {
                        'file_name': originalPath.rsplit(os.sep, 1)[-1].rsplit('.', 1)[0],
                        'orientation': quantizationProfile['orientation'],
                        'sizing': 'cover' if quantizationProfile['sizing']['type'] == 'cover' else '_'.join(
                            [
                                quantizationProfile['sizing']['type'],
                                quantizationProfile['sizing']['fill']
                            ]
                        ),
                        'extension': imageSettings['extension']
                    }
                ),
                'url': '/images/quantization/%(file_name)s_%(orientation)s_%(sizing)s.%(extension)s' % {
                    'file_name': originalPath.rsplit(os.sep, 1)[-1].rsplit('.', 1)[0],
                    'orientation': quantizationProfile['orientation'],
                    'sizing': 'cover' if quantizationProfile['sizing']['type'] == 'cover' else '_'.join(
                        [
                            quantizationProfile['sizing']['type'],
                            quantizationProfile['sizing']['fill']
                        ]
                    ),
                    'extension': imageSettings['extension']
                },
                'orientation': quantizationProfile['orientation']
            }

            if not imageId is None:

                quantizationInfo['image_id'] = imageId


            resizedImage = None

            if originalImage.size[0] == quantizationInfo['width'] and originalImage.size[1] == quantizationInfo['height']:

                resizedImage = originalImage

            elif (originalImage.size[0] / quantizationInfo['width']) == (originalImage.size[1] / quantizationInfo['height']):

                resizedImage = originalImage.resize(
                    (
                        quantizationInfo['width'],
                        quantizationInfo['height']
                    ),
                    Image.Resampling.LANCZOS
                )

            else:

                if quantizationProfile['sizing']['type'] == 'fit':

                    fgImage = originalImage.copy()
                    fgImage = fgImage.resize(
                        (
                            imageSizing['fit']['resize']['width'],
                            imageSizing['fit']['resize']['height']
                        ),
                        Image.Resampling.LANCZOS
                    )

                    if quantizationProfile['sizing']['fill'] == 'blank':

                        resizedImage = Image.new(
                            mode='RGB',
                            size=(
                                quantizationInfo['width'],
                                quantizationInfo['height']
                            ),
                            color=(255, 255, 255)
                        )

                    elif quantizationProfile['sizing']['fill'] == 'blur':

                        resizedImage = Image.new(
                            mode='RGB',
                            size=(
                                quantizationInfo['width'],
                                quantizationInfo['height']
                            ),
                            color=(255, 255, 255)
                        )

                        bgImage = originalImage.copy()
                        bgImage = bgImage.resize(
                            (
                                imageSizing['cover']['resize']['width'],
                                imageSizing['cover']['resize']['height']
                            ),
                            Image.Resampling.LANCZOS
                        )
                        bgImage = bgImage.crop(
                            (
                                imageSizing['cover']['crop']['x0'],
                                imageSizing['cover']['crop']['y0'],
                                imageSizing['cover']['crop']['x1'],
                                imageSizing['cover']['crop']['y1']
                            )
                        )
                        bgImage = bgImage.filter(
                            ImageFilter.GaussianBlur(
                                min(
                                    [
                                        2,
                                        int(
                                            max(
                                                [
                                                    quantizationInfo['width'],
                                                    quantizationInfo['height']
                                                ]
                                            ) / 32
                                        )
                                    ]
                                )
                            )
                        )
                        brightnessFilter = ImageEnhance.Brightness(bgImage)
                        bgImage = brightnessFilter.enhance(
                            imageSettings['blur_brightness']
                        )

                        resizedImage.paste(
                            bgImage,
                            (
                                0,
                                0,
                                quantizationInfo['width'],
                                quantizationInfo['height']
                            )
                        )

                        del bgImage


                    resizedImage.paste(
                        fgImage,
                        (
                            imageSizing['fit']['paste']['x0'],
                            imageSizing['fit']['paste']['y0'],
                            imageSizing['fit']['paste']['x1'],
                            imageSizing['fit']['paste']['y1']
                        )
                    )

                    del fgImage

                elif quantizationProfile['sizing']['type'] == 'cover':

                    resizedImage = Image.new(
                        mode='RGB',
                        size=(
                            quantizationInfo['width'],
                            quantizationInfo['height']
                        ),
                        color=(255, 255, 255)
                    )

                    fgImage = originalImage.copy()

                    fgImage = fgImage.resize(
                        (
                            imageSizing['cover']['resize']['width'],
                            imageSizing['cover']['resize']['height']
                        ),
                        Image.Resampling.LANCZOS
                    )
                    fgImage = fgImage.crop(
                        (
                            imageSizing['cover']['crop']['x0'],
                            imageSizing['cover']['crop']['y0'],
                            imageSizing['cover']['crop']['x1'],
                            imageSizing['cover']['crop']['y1']
                        )
                    )
                    fgImage = fgImage.filter(
                        ImageFilter.GaussianBlur(
                            min(
                                [
                                    2,
                                    int(
                                        max(
                                            [
                                                quantizationInfo['width'],
                                                quantizationInfo['height']
                                            ]
                                        ) / 32
                                    )
                                ]
                            )
                        )
                    )
                    brightnessFilter = ImageEnhance.Brightness(fgImage)
                    fgImage = brightnessFilter.enhance(
                        imageSettings['blur_brightness']
                    )

                    resizedImage.paste(
                        fgImage,
                        (
                            0,
                            0,
                            quantizationInfo['width'],
                            quantizationInfo['height']
                        )
                    )

                    del fgImage


            ditheredImage = resizedImage.quantize(
                palette=self.palette
            )
            ditheredImage.save(
                quantizationInfo['path']
            )


            quantizationInfo['bytes'] = os.path.getsize(
                quantizationInfo['path']
            )


            quantizationWorking = quantizationInfo

            del resizedImage
            del ditheredImage

        except Exception as e:

            self.db.log(
                self.logFileKey,
                '.'.join(
                    [
                        str(self.__class__.__name__),
                        str(sys._getframe().f_code.co_name)
                    ]
                ),
                ' '.join(
                    [
                        originalPath,
                        str(e)
                    ]
                )
            )

        del originalImage


        return quantizationWorking
    def generateImageThumbnail(self, originalImage, originalPath, imageSettings, thumbnailSize, imageId=None):
        """Generates thumbnail image from original."""

        thumbnailWorking = None

        try:

            imageSizing = self.getImageSizing(
                originalImage.size,
                [
                    thumbnailSize,
                    thumbnailSize
                ]
            )

            thumbnailInfo = {
                'width': thumbnailSize,
                'height': thumbnailSize,
                'path': os.path.join(
                    self.db.paths['thumbnail']['path'],
                    '%(file_name)s_%(size)i.%(extension)s' % {
                        'file_name': originalPath.rsplit(os.sep, 1)[-1].rsplit('.', 1)[0],
                        'size': thumbnailSize,
                        'extension': imageSettings['extension']
                    }
                ),
                'url': '/images/thumbnail/%(file_name)s_%(size)i.%(extension)s' % {
                    'file_name': originalPath.rsplit(os.sep, 1)[-1].rsplit('.', 1)[0],
                    'size': thumbnailSize,
                    'extension': imageSettings['extension']
                }
            }

            if not imageId is None:

                thumbnailInfo['image_id'] = imageId


            thumbnailImage = Image.new(
                mode='RGB',
                size=(
                    thumbnailSize,
                    thumbnailSize
                ),
                color=(255, 255, 255)
            )


            fgImage = originalImage.copy()
            fgImage = fgImage.resize(
                (
                    imageSizing['fit']['resize']['width'],
                    imageSizing['fit']['resize']['height']
                ),
                Image.Resampling.LANCZOS
            )


            bgImage = originalImage.copy()
            bgImage = bgImage.resize(
                (
                    imageSizing['cover']['resize']['width'],
                    imageSizing['cover']['resize']['height']
                ),
                Image.Resampling.LANCZOS
            )
            bgImage = bgImage.crop(
                (
                    imageSizing['cover']['crop']['x0'],
                    imageSizing['cover']['crop']['y0'],
                    imageSizing['cover']['crop']['x1'],
                    imageSizing['cover']['crop']['y1']
                )
            )
            bgImage = bgImage.filter(
                ImageFilter.GaussianBlur(
                    min(
                        [
                            2,
                            int(thumbnailSize / 32)
                        ]
                    )
                )
            )
            brightnessFilter = ImageEnhance.Brightness(bgImage)
            bgImage = brightnessFilter.enhance(
                imageSettings['blur_brightness']
            )


            thumbnailImage.paste(
                bgImage,
                (
                    0,
                    0,
                    thumbnailSize,
                    thumbnailSize
                )
            )
            thumbnailImage.paste(
                fgImage,
                (
                    imageSizing['fit']['paste']['x0'],
                    imageSizing['fit']['paste']['y0'],
                    imageSizing['fit']['paste']['x1'],
                    imageSizing['fit']['paste']['y1']
                )
            )


            thumbnailImage.save(
                thumbnailInfo['path']
            )


            thumbnailInfo['bytes'] = os.path.getsize(
                thumbnailInfo['path']
            )

            thumbnailInfo['blob'] = 'url(\'data:image/png;base64,%s\');' % (
                base64.b64encode(
                    open(
                        thumbnailInfo['path'],
                        'rb'
                    ).read()
                ).decode('utf-8'),
            )


            thumbnailWorking = thumbnailInfo

            del thumbnailImage
            del fgImage
            del bgImage

        except Exception as e:

            self.db.log(
                self.logFileKey,
                '.'.join(
                    [
                        str(self.__class__.__name__),
                        str(sys._getframe().f_code.co_name)
                    ]
                ),
                ' '.join(
                    [
                        originalPath,
                        str(e)
                    ]
                )
            )

        del originalImage


        return thumbnailWorking
    def getImageSizing(self, sourceSize, destinationSize):
        """Gets image resizing and cropping dimensions."""

        imageSizing = {
            'fit': {
                'resize': {
                    'width': 0,
                    'height': 0
                },
                'paste': {
                    'x0': 0,
                    'y0': 0,
                    'x1': 0,
                    'y1': 0
                }
            },
            'cover': {
                'resize': {
                    'width': 0,
                    'height': 0
                },
                'crop': {
                    'x0': 0,
                    'y0': 0,
                    'x1': 0,
                    'y1': 0
                }
            }
        }

        try:

            sWH = sourceSize[0] / sourceSize[1]
            dWH = destinationSize[0] / destinationSize[1]
            sdW = sourceSize[0] / destinationSize[0]
            sdH = sourceSize[1] / destinationSize[1]

            if (sourceSize[0] == destinationSize[0] and sourceSize[1] == destinationSize[1]) or (sWH == dWH):

                imageSizing['fit']['resize']['width'] = destinationSize[0]
                imageSizing['fit']['resize']['height'] = destinationSize[1]
                
                imageSizing['fit']['paste']['x0'] = 0
                imageSizing['fit']['paste']['y0'] = 0
                imageSizing['fit']['paste']['x1'] = destinationSize[0]
                imageSizing['fit']['paste']['y1'] = destinationSize[1]

                imageSizing['cover']['resize']['width'] = destinationSize[0]
                imageSizing['cover']['resize']['height'] = destinationSize[1]

                imageSizing['cover']['crop']['x0'] = 0
                imageSizing['cover']['crop']['y0'] = 0
                imageSizing['cover']['crop']['x1'] = destinationSize[0]
                imageSizing['cover']['crop']['y1'] = destinationSize[1]

            else:

                imageSizing['fit']['resize']['width'] = destinationSize[0] if sWH > dWH else int(
                    sourceSize[0] / sdH
                )
                imageSizing['fit']['resize']['height'] = destinationSize[1] if sWH < dWH else int(
                    sourceSize[1] / sdW
                )
                
                imageSizing['fit']['paste']['x0'] = 0 if sWH > dWH else int(
                    (
                        destinationSize[0] - imageSizing['fit']['resize']['width']
                    ) / 2.0
                )
                imageSizing['fit']['paste']['y0'] = 0 if sWH < dWH else int(
                    (
                        destinationSize[1] - imageSizing['fit']['resize']['height']
                    ) / 2.0
                )
                imageSizing['fit']['paste']['x1'] = destinationSize[0] if sWH > dWH else (
                    imageSizing['fit']['paste']['x0'] + imageSizing['fit']['resize']['width']
                )
                imageSizing['fit']['paste']['y1'] = destinationSize[1] if sWH < dWH else (
                    imageSizing['fit']['paste']['y0'] + imageSizing['fit']['resize']['height']
                )

                imageSizing['cover']['resize']['width'] = destinationSize[0] if sWH < dWH else int(
                    sourceSize[0] / sdH
                )
                imageSizing['cover']['resize']['height'] = destinationSize[1] if sWH > dWH else int(
                    sourceSize[1] / sdW
                )

                imageSizing['cover']['crop']['x0'] = 0 if sWH < dWH else int(
                    (
                        imageSizing['cover']['resize']['width'] - destinationSize[0]
                    ) / 2.0
                )
                imageSizing['cover']['crop']['y0'] = 0 if sWH > dWH else int(
                    (
                        imageSizing['cover']['resize']['height'] - destinationSize[1]
                    ) / 2.0
                )
                imageSizing['cover']['crop']['x1'] = destinationSize[0] if sWH < dWH else (
                    imageSizing['cover']['crop']['x0'] + destinationSize[0]
                )
                imageSizing['cover']['crop']['y1'] = destinationSize[1] if sWH > dWH else (
                    imageSizing['cover']['crop']['y0'] + destinationSize[1]
                )

        except Exception as e:

            self.db.log(
                self.logFileKey,
                '.'.join(
                    [
                        str(self.__class__.__name__),
                        str(sys._getframe().f_code.co_name)
                    ]
                ),
                str(e)
            )


        return imageSizing


    def getImageData(self, imageId):
        """Gets images for API use."""

        imageData = {
            'image_data': []
        }

        try:

            if isinstance(imageId, str):

                dbMatch = None

                if not imageId == 'all':

                    dbMatch = {
                        'id': int(imageId)
                    }


                dbImages = self.db.get(
                    dbObjectType='image',
                    match=dbMatch
                )


                if not dbImages is None:

                    if isinstance(dbImages, DbImage):

                        dbImages = [dbImages]


                    apiImages = [
                        dbImage.getApiFormat()
                        for dbImage in dbImages
                    ]


                    imageData['image_data'] = apiImages

                del dbImages

        except Exception as e:

            self.db.log(
                self.logFileKey,
                '.'.join(
                    [
                        str(self.__class__.__name__),
                        str(sys._getframe().f_code.co_name)
                    ]
                ),
                str(e)
            )


        return imageData
    def displayImage(self, imageInfo):
        """Displays an image."""

        statusMessage = {'error': 'Bad request'}
        statusCode = 400

        try:

            imageSettings = self.db.settings.get('image')

            if imageSettings['paused'] == True:

                statusMessage = {'status': 'ok'}
                statusCode = 200

            else:

                if isinstance(imageInfo, dict):

                    if 'action' in imageInfo.keys():

                        if imageInfo['action'] == 'preset':

                            imageSettings = self.db.settings.get('image')

                        elif imageInfo['action'] == 'generate':

                            self.db.settings.generateMediaQueue(
                                currentId=None
                            )

                            imageSettings = self.db.settings.get('image')

                        elif imageInfo['action'] == 'next':

                            self.db.settings.rotateMediaQueue(
                                forward=True
                            )

                            imageSettings = self.db.settings.get('image')

                        elif imageInfo['action'] == 'previous':

                            self.db.settings.rotateMediaQueue(
                                forward=False
                            )

                            imageSettings = self.db.settings.get('image')

                        elif imageInfo['action'] == 'set':

                            if 'id' in imageInfo.keys():

                                self.db.settings.generateMediaQueue(
                                    currentId=imageInfo['id']
                                )

                                imageSettings = self.db.settings.get('image')

                    else:

                        self.db.settings.rotateMediaQueue(
                            forward=True
                        )

                        imageSettings = self.db.settings.get('image')

                else:

                    self.db.settings.rotateMediaQueue(
                        forward=True
                    )

                    imageSettings = self.db.settings.get('image')


                if isinstance(imageSettings, dict):

                    if not imageSettings['current'] == -1:

                        dbQuantizations = self.db.get(
                            'quantization',
                            match={
                                'image_id': imageSettings['current']
                            }
                        )

                        if isinstance(dbQuantizations, list):

                            quantizationPath = None

                            profileString = '_%(orientation)s_%(sizing)s' % {
                                'orientation': imageSettings['orientation'],
                                'sizing': 'cover' if imageSettings['sizing']['type'] == 'cover' else '_'.join(
                                    [
                                        imageSettings['sizing']['type'],
                                        imageSettings['sizing']['fill']
                                    ]
                                )
                            }

                            for dbQuantization in dbQuantizations:

                                if profileString in dbQuantization.working['path']:

                                    quantizationPath = dbQuantization.working['path']

                                    break

                            del profileString


                            if not quantizationPath is None:

                                quantizedImage = Image.open(
                                    dbQuantization.working['path']
                                )

                                imageRaw = bytearray(
                                    quantizedImage.tobytes('raw')
                                )

                                imageBuffered = [
                                    (imageRaw[int(r * 2)] << 4) + imageRaw[int((r * 2) + 1)]
                                    for r in range(int((imageSettings['size'][0] * imageSettings['size'][1]) / 2))
                                ]


                                self.display.displayBytes(
                                    imageBuffered
                                )


                                del quantizedImage
                                del imageRaw
                                del imageBuffered


                                self.setTaskData(
                                    {
                                        'name': 'Rotate Images',
                                        'last': (datetime.datetime.now() - datetime.datetime.fromtimestamp(0)).total_seconds(),
                                        'status': 'ok'
                                    }
                                )

                                statusMessage = {'status': 'ok'}
                                statusCode = 200

                            else:

                                self.db.log(
                                    self.logFileKey,
                                    '.'.join(
                                        [
                                            str(self.__class__.__name__),
                                            str(sys._getframe().f_code.co_name)
                                        ]
                                    ),
                                    'Missing quantizations.'
                                )

                            del quantizationPath

                        else:

                            self.db.log(
                                self.logFileKey,
                                '.'.join(
                                    [
                                        str(self.__class__.__name__),
                                        str(sys._getframe().f_code.co_name)
                                    ]
                                ),
                                'Missing quantizations.'
                            )

                        del dbQuantizations

                    else:

                        self.db.log(
                            self.logFileKey,
                            '.'.join(
                                [
                                    str(self.__class__.__name__),
                                    str(sys._getframe().f_code.co_name)
                                ]
                            ),
                            'Empty queue.'
                        )

                else:

                    self.db.log(
                        self.logFileKey,
                        '.'.join(
                            [
                                str(self.__class__.__name__),
                                str(sys._getframe().f_code.co_name)
                            ]
                        ),
                        'Invalid action.'
                    )

            del imageSettings

        except Exception as e:

            self.db.log(
                self.logFileKey,
                '.'.join(
                    [
                        str(self.__class__.__name__),
                        str(sys._getframe().f_code.co_name)
                    ]
                ),
                str(e)
            )


        return statusMessage, statusCode
    def setImageTags(self, imageId, tags):
        """Sets tags for an image in DB."""

        try:

            if isinstance(tags, list):

                if isinstance(imageId, int):

                    self.db.delete(
                        'tag',
                        {
                            'image_id': imageId
                        }
                    )

                for tag in tags:

                    if isinstance(tag, dict):

                        if 'image_id' in tag.keys():

                            categoryId = None
                            subcategoryId = None

                            if 'category' in tag.keys():

                                if isinstance(tag['category'], dict):

                                    if 'id' in tag['category'].keys():

                                        categoryId = tag['category']['id']

                                if 'subcategory' in tag.keys():

                                    if isinstance(tag['subcategory'], dict):

                                        if 'id' in tag['subcategory'].keys():

                                            subcategoryId = tag['subcategory']['id']

                            elif 'category_id' in tag.keys():

                                categoryId = tag['category_id']

                                if 'subcategory_id' in tag.keys():

                                    subcategoryId = tag['subcategory_id']

                            if not categoryId is None:

                                dbTag = self.db.new(
                                    'tag',
                                    {
                                        'image_id': tag['image_id'],
                                        'category_id': categoryId,
                                        'subcategory_id': subcategoryId
                                    }
                                )

                                del dbTag

        except Exception as e:

            self.db.log(
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
    def setImageDescription(self, imageId, description):
        """Sets image description for an image in DB."""

        try:

            if isinstance(imageId, int):

                if isinstance(description, str):

                    dbImage = self.db.get(
                        'image',
                        match={
                            'id': imageId
                        }
                    )

                    if not dbImage is None:

                        if isinstance(dbImage, DbImage):

                            dbImage.working['description'] = description

                            dbImage.save()

                            del dbImage

        except Exception as e:

            self.db.log(
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
    def deleteImage(self, imageId):
        """Delete image from DB."""

        try:

            if isinstance(imageId, int):

                dbImage = self.db.get(
                    dbObjectType='image',
                    match={
                        'id': imageId
                    }
                )


                if not dbImage is None:

                    if isinstance(dbImage, DbImage):

                        dbImage.delete()

                        del dbImage

        except Exception as e:

            self.db.log(
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


    def getCategoryData(self):
        """Gets categories for API use."""

        categoryData = {
            'category_data': []
        }

        try:

            dbCategories = self.db.get(
                dbObjectType='category',
                match=None
            )


            if not dbCategories is None:

                if isinstance(dbCategories, DbCategory):

                    dbCategories = [dbCategories]


                apiCategories = [
                    dbCategory.getApiFormat()
                    for dbCategory in dbCategories
                ]


                categoryData['category_data'] = apiCategories

            del dbCategories

        except Exception as e:

            self.db.log(
                self.logFileKey,
                '.'.join(
                    [
                        str(self.__class__.__name__),
                        str(sys._getframe().f_code.co_name)
                    ]
                ),
                str(e)
            )


        return categoryData
    def setCategoryData(self, categoryData):
        """Sets category data from API."""

        try:

            if isinstance(categoryData, dict | list):

                if isinstance(categoryData, dict):

                    categoryData = [categoryData]


                for categoryAction in categoryData:

                    if 'action' in categoryAction.keys():

                        if categoryAction['action'] == 'add_category':

                            if 'category_name' in categoryAction.keys():

                                dbCategory = self.db.new(
                                    'category',
                                    {
                                        'name': categoryAction['category_name']
                                    }
                                )
                                del dbCategory

                        elif categoryAction['action'] == 'add_subcategory':

                            if 'category_id' in categoryAction.keys() and 'subcategory_name' in categoryAction.keys():

                                dbSubcategory = self.db.new(
                                    'subcategory',
                                    {
                                        'category_id': categoryAction['category_id'],
                                        'name': categoryAction['subcategory_name']
                                    }
                                )
                                del dbSubcategory

                        elif categoryAction['action'] == 'add_category_with_subcategory':

                            if 'category_name' in categoryAction.keys() and 'subcategory_name' in categoryAction.keys():

                                dbCategory = self.db.new(
                                    'category',
                                    {
                                        'name': categoryAction['category_name']
                                    }
                                )
                                dbSubcategory = self.db.new(
                                    'subcategory',
                                    {
                                        'category_id': dbCategory.working['id'],
                                        'name': categoryAction['subcategory_name']
                                    }
                                )
                                del dbSubcategory
                                del dbCategory

                        elif categoryAction['action'] == 'edit_category':

                            if 'category_id' in categoryAction.keys() and 'category_name' in categoryAction.keys():

                                dbCategory = self.db.get(
                                    'category',
                                    {
                                        'id': categoryAction['category_id']
                                    }
                                )

                                if not dbCategory is None:

                                    dbCategory.working['name'] = categoryAction['category_name']

                                    dbCategory.save()

                                del dbCategory

                        elif categoryAction['action'] == 'edit_subcategory':

                            if 'subcategory_id' in categoryAction.keys() and 'subcategory_name' in categoryAction.keys():

                                dbSubcategory = self.db.get(
                                    'subcategory',
                                    {
                                        'id': categoryAction['subcategory_id']
                                    }
                                )

                                if not dbSubcategory is None:

                                    dbSubcategory.working['name'] = categoryAction['subcategory_name']

                                    dbSubcategory.save()

                                del dbSubcategory

                        elif categoryAction['action'] == 'delete_category':

                            if 'category_id' in categoryAction.keys():

                                dbCategory = self.db.get(
                                    'category',
                                    {
                                        'id': categoryAction['category_id']
                                    }
                                )

                                if not dbCategory is None:

                                    dbCategory.delete()

                                del dbCategory

                        elif categoryAction['action'] == 'delete_subcategory':

                            if 'subcategory_id' in categoryAction.keys():

                                dbSubcategory = self.db.get(
                                    'subcategory',
                                    {
                                        'id': categoryAction['subcategory_id']
                                    }
                                )

                                if not dbSubcategory is None:

                                    dbSubcategory.delete()

                                del dbSubcategory

        except Exception as e:

            self.db.log(
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


    def getUserData(self, userId):
        """Gets users for API use."""

        userData = {
            'user_data': []
        }

        try:

            dbUsers = self.db.get(
                dbObjectType='user',
                match=None if (userId is None or userId == 'all') else (
                    {
                        'id': int(userId)
                    } if (isinstance(userId, str) and len(userId) > 0) else None
                )
            )


            if not dbUsers is None:

                if isinstance(dbUsers, DbUser):

                    dbUsers = [dbUsers]


                apiUsers = [
                    dbUser.getApiFormat()
                    for dbUser in dbUsers
                ]


                userData['user_data'] = apiUsers

            del dbUsers

        except Exception as e:

            self.db.log(
                self.logFileKey,
                '.'.join(
                    [
                        str(self.__class__.__name__),
                        str(sys._getframe().f_code.co_name)
                    ]
                ),
                str(e)
            )


        return userData
    def setUserData(self, userData):
        """Sets users from API."""

        try:

            if isinstance(userData, dict):

                if 'id' in userData.keys():

                    dbUser = self.db.get(
                        'user',
                        match={
                            'id': userData['id']
                        }
                    )


                    if isinstance(dbUser, DbUser):

                        childKeys = [
                            child['key']
                            for child in dbUser.info['children']
                        ]

                        for apiKey in userData.keys():

                            if apiKey in dbUser.working.keys():

                                if not apiKey in childKeys:

                                    dbUser.working[apiKey] = userData[apiKey]

                        dbUser.save(children=False)

                        if 'user_permissions' in userData.keys():

                            dbExistingUserPermissions = self.db.get(
                                'user_permission',
                                match={
                                    'user_id': userData['id']
                                }
                            )

                            if not dbExistingUserPermissions is None:

                                if isinstance(dbExistingUserPermissions, DbUserPermission):

                                    dbExistingUserPermissions.delete(children=False)

                                elif isinstance(dbExistingUserPermissions, list):

                                    for dbExistingUserPermission in dbExistingUserPermissions:

                                        dbExistingUserPermission.delete(children=False)

                            del dbExistingUserPermissions


                            for userPermission in userData['user_permissions']:

                                dbUserPermission = self.db.new(
                                    'user_permission',
                                    {
                                        'user_id': userData['id'],
                                        'permission_id': userPermission['id']
                                    }
                                )

                                del dbUserPermission

                        del dbUser

                else:

                    for info in self.db.dbObjectInfo:

                        if info['type'] == 'user':

                            requiredKeys = all(
                                [
                                    column['key'] in userData.keys()
                                    for column in info['columns']
                                    if column['data_info']['not_null'] == True and column['data_info']['primary_key'] == False
                                ]
                            )

                            if requiredKeys == True:

                                newUserValues = dict(
                                    [
                                        (
                                            column['key'],
                                            userData[column['key']]
                                        )
                                        for column in info['columns']
                                        if column['data_info']['not_null'] == True and column['data_info']['primary_key'] == False
                                    ]
                                )

                                dbUserTemp = self.db.new(
                                    'user',
                                    newUserValues
                                )

                                if 'user_permissions' in userData.keys():

                                    if isinstance(userData['user_permissions'], list):

                                        for userPermissionData in userData['user_permissions']:

                                            if isinstance(userPermissionData, dict):

                                                if 'permission_id' in userPermissionData.keys():

                                                    if isinstance(userPermissionData['permission_id'], int):

                                                        dbUserPermissionTemp = self.db.new(
                                                            'user_permission',
                                                            {
                                                                'user_id': dbUserTemp.working['id'],
                                                                'permission_id': userPermissionData['permission_id']
                                                            }
                                                        )

                                                        del dbUserPermissionTemp

                                del dbUserTemp

                            break

        except Exception as e:

            self.db.log(
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
    def deleteUser(self, userId):
        """Deletes user from DB."""

        try:

            if isinstance(userId, int):

                dbUser = self.db.get(
                    'user',
                    match={
                        'id': userId
                    }
                )

                if not dbUser is None:

                    if isinstance(dbUser, DbUser):

                        dbUser.delete()

                del dbUser

        except Exception as e:

            self.db.log(
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
    def getUserFromToken(self, token):
        """Gets DbUser object from given token string."""

        apiUser = None

        try:

            dbToken = self.db.get(
                'token',
                match={
                    'token': token
                }
            )

            if not dbToken is None:

                if isinstance(dbToken, DbToken):

                    dbUser = self.db.get(
                        'user',
                        match={
                            'id': dbToken.working['user_id']
                        }
                    )

                    if not dbUser is None:

                        if isinstance(dbUser, DbUser):

                            apiUser = dbUser.getApiFormat()

                    del dbUser

        except Exception as e:

            self.db.log(
                self.logFileKey,
                '.'.join(
                    [
                        str(self.__class__.__name__),
                        str(sys._getframe().f_code.co_name)
                    ]
                ),
                str(e)
            )


        return apiUser
    def getUserToken(self, username, password):
        """Gets token for successful login."""

        apiToken = None

        try:

            dbUser = self.db.get(
                'user',
                match={
                    'username': username
                }
            )

            if not dbUser is None:

                if password == dbUser.working['password']:

                    dbToken = None

                    timestamp = (datetime.datetime.now() - datetime.datetime.fromtimestamp(0)).total_seconds()

                    for token in dbUser.working['tokens']:

                        if token.working['expires'] > timestamp:

                            dbToken = token

                            break

                    if dbToken is None:

                        dbToken = self.db.new(
                            dbObjectType='token',
                            objectValues={
                                'user_id': dbUser.working['id']
                            }
                        )

                    apiToken = dbToken.getApiFormat()

                    del dbToken
                    del dbUser

        except Exception as e:

            self.db.log(
                self.logFileKey,
                '.'.join(
                    [
                        str(self.__class__.__name__),
                        str(sys._getframe().f_code.co_name)
                    ]
                ),
                str(e)
            )


        return apiToken
    def reapExpiredTokens(self):
        """Removes expired tokens from DB."""

        statusMessage = {'error': 'Server error'}
        statusCode = 500

        try:

            self.db.delete(
                'token',
                match=' WHERE expires < %(timestamp)f' % {
                    'timestamp': (datetime.datetime.now() - datetime.datetime.fromtimestamp(0)).total_seconds()
                },
                children=True
            )

            statusMessage = {'status': 'ok'}
            statusCode = 200

        except Exception as e:

            self.db.log(
                self.logFileKey,
                '.'.join(
                    [
                        str(self.__class__.__name__),
                        str(sys._getframe().f_code.co_name)
                    ]
                ),
                str(e)
            )


        return statusMessage, statusCode
    def exportApiUser(self):
        """Exports API user data for background process."""

        statusMessage = {'error': 'Server error'}
        statusCode = 500

        try:

            dbApiUser = self.db.get(
                'user',
                match={
                    'username': 'scissor_api'
                }
            )

            if isinstance(dbApiUser, DbUser):

                apiUserData = dict(
                    [
                        (
                            userKey,
                            dbApiUser.working[userKey]
                        )
                        for userKey in dbApiUser.working.keys()
                        if not userKey in [child['key'] for child in dbApiUser.info['children']]
                    ]
                )

                with open(self.db.paths['api_credentials']['path'], 'w', encoding='utf-8') as f:

                    f.write(
                        json.dumps(
                            apiUserData
                        )
                    )

                del dbApiUser
                del apiUserData

                statusMessage = {'status': 'ok'}
                statusCode = 200

        except Exception as e:

            self.db.log(
                self.logFileKey,
                '.'.join(
                    [
                        str(self.__class__.__name__),
                        str(sys._getframe().f_code.co_name)
                    ]
                ),
                str(e)
            )


        return statusMessage, statusCode


    def getSettingsData(self, path):
        """Gets settings data for API use."""

        settingsData = {}

        try:

            if isinstance(path, str):

                if path == 'image':

                    settingsData['image_settings'] = self.db.settings.get('image')

                elif path == 'password':

                    settingsData['password_settings'] = self.db.settings.get('password')

                elif path == 'category':

                    settingsData = self.getCategoryData()

                elif path == 'permission':

                    settingsData['permission_settings'] = []

                    dbPermissions = self.db.get(
                        'permission',
                        match=None
                    )

                    if not dbPermissions is None:

                        if isinstance(dbPermissions, DbPermission):

                            settingsData['permission_settings'].append(
                                dbPermissions.getApiFormat()
                            )

                        elif isinstance(dbPermissions, list):

                            for dbPermission in dbPermissions:

                                settingsData['permission_settings'].append(
                                    dbPermission.getApiFormat()
                                )

        except Exception as e:

            self.db.log(
                self.logFileKey,
                '.'.join(
                    [
                        str(self.__class__.__name__),
                        str(sys._getframe().f_code.co_name)
                    ]
                ),
                str(e)
            )


        return settingsData
    def setSettingsData(self, path, settingsData):
        """Sets settings data from API."""

        try:

            if isinstance(path, str):

                if path == 'image':

                    previousSettings = self.getSettingsData('image')['image_settings']

                    if 'paused' in settingsData.keys():

                        settingsData['paused'] = not previousSettings['paused'] # auto toggle


                    if 'filters' in settingsData.keys():

                        if not previousSettings['filters'] == settingsData['filters']:

                            self.displayImage(
                                {
                                    'action': 'generate'
                                }
                            )

                    for key in ['current', 'queue', 'orientation']:

                        if key in settingsData.keys() and (not settingsData[key] == previousSettings[key]):

                            self.displayImage(
                                {
                                    'action': 'next'
                                }
                            )

                            break

                    if 'sizing' in settingsData.keys():

                        if not previousSettings['sizing']['type'] == settingsData['sizing']['type']:

                            self.displayImage(
                                {
                                    'action': 'next'
                                }
                            )

                        else:

                            if 'fill' in settingsData['sizing'].keys():

                                if not previousSettings['sizing']['fill'] == settingsData['sizing']['fill']:

                                    self.displayImage(
                                        {
                                            'action': 'next'
                                        }
                                    )

                        if not 'fill' in settingsData['sizing'].keys():

                            settingsData['sizing']['fill'] = None

                    for key in previousSettings.keys():

                        if not key in settingsData.keys():

                            settingsData[key] = previousSettings[key]

                    self.db.settings.set(
                        'image',
                        settingsData
                    )

                elif path == 'password':

                    self.db.settings.set(
                        'password',
                        settingsData
                    )

                elif path == 'category':

                    self.setCategoryData(settingsData)

        except Exception as e:

            self.db.log(
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


    def getTaskData(self):
        """Gets task data for API use."""

        taskData = {
            'task_data': []
        }

        try:

            dbTasks = self.db.get(
                'task',
                match=None
            )

            if isinstance(dbTasks, DbTask):

                dbTasks = [dbTasks]

            if isinstance(dbTasks, list):
                
                apiTasks = [
                    dbTask.getApiFormat()
                    for dbTask in dbTasks
                ]

                
                taskData['task_data'] = apiTasks
                
            del dbTasks

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


        return taskData
    def setTaskData(self, taskData):
        """Sets task data from API."""

        statusMessage = {'error': 'Bad request'}
        statusCode = 400

        try:

            if isinstance(taskData, dict):

                taskData = [taskData]

            if isinstance(taskData, list):

                for task in taskData:

                    if isinstance(task, dict):

                        if 'name' in task.keys():

                            dbTask = self.db.get(
                                'task',
                                match={
                                    'name': task['name']
                                }
                            )

                            if isinstance(dbTask, DbTask):

                                for key in ['delay', 'last', 'status']:

                                    if key in task.keys():

                                        dbTask.working[key] = task[key]

                                dbTask.save()

                                del dbTask

                                statusMessage = {'status': 'ok'}
                                statusCode = 200

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


        return statusMessage, statusCode


    def getLogs(self, filters=None):
        """Gets log entries."""

        logData = {
            'log_data': {
                'keys': [
                    key
                    for key in self.db.paths.keys()
                    if self.db.paths[key]['type'] == 'log'
                ],
                'logs': []
            }
        }

        try:

            # Default filter
            logFilter = {
                'paging': {
                    'size': 50,
                    'page': 0
                },
                'sort': 'DESC',
                'keys': [
                    key
                    for key in self.db.paths.keys()
                    if self.db.paths[key]['type'] == 'log'
                ]
            }

            # API-defined filter
            if isinstance(filters, dict):

                if 'paging' in filters.keys():

                    if 'size' in filters['paging'].keys() and 'page' in filters['paging'].keys():

                        logFilter['paging']['size'] = filters['paging']['size']
                        logFilter['paging']['page'] = filters['paging']['page']

                if 'sort' in filters.keys():

                    logFilter['sort'] = filters['sort']

                if 'keys' in filters.keys():

                    logFilter['keys'] = filters['keys']


            if isinstance(logFilter['keys'], list):

                logOutputs = []

                for logKey in logFilter['keys']:

                    if os.path.exists(self.db.paths[logKey]['path']):

                        logTemp = []

                        with open(self.db.paths[logKey]['path'], 'r', encoding='utf-8') as f:

                            logTemp = f.readlines()

                        for log in logTemp:

                            logOutputs.append(log)


                if logFilter['sort'] == 'ASC':

                    logOutputs = list(reversed(sorted(logOutputs)))

                else:

                    logOutputs = list(sorted(logOutputs))


                logOutputs = logOutputs[
                    (
                        logFilter['paging']['size'] * logFilter['paging']['page']
                    ):(
                        logFilter['paging']['size'] * (logFilter['paging']['page'] + 1)
                    )
                ]


                logJson = []

                for logOutput in logOutputs:

                    if '|' in logOutput:

                        if len(logOutput.replace('\r', '').rstrip('\n').split('|', 1)[-1].split(':')) > 1:

                            logJson.append(
                                {
                                    'date': logOutput.replace('\r', '').rstrip('\n').split('|', 1)[0].strip(),
                                    'source': logOutput.replace('\r', '').rstrip('\n').split('|', 1)[-1].split(':', 1)[0].strip(),
                                    'entry': logOutput.replace('\r', '').rstrip('\n').split('|', 1)[-1].split(':', 1)[-1].strip()
                                }
                            )

                del logOutputs


                logData['log_data']['logs'] = logJson

            del logFilter

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


        return logData
    def rotateLogs(self):
        """Rotates log files."""

        maxEntries = 1000

        statusMessage = {'error': 'Bad request'}
        statusCode = 400

        try:

            logPaths = [
                self.db.paths[pathKey]['path']
                for pathKey in self.db.paths.keys()
                if self.db.paths[pathKey]['type'] == 'log'
            ]

            for logPath in logPaths:

                if os.path.exists(logPath):

                    if os.path.isfile(logPath):

                        try:

                            logged = []

                            with open(logPath, 'r', encoding='utf-8') as f:

                                logged = f.readlines()

                            logged = logged[-maxEntries:]

                            with open(logPath, 'w', encoding='utf-8') as f:

                                for l in logged:

                                    f.write(l + '\n')

                        except Exception as e:

                            self.db.log(
                                self.logFileKey,
                                '.'.join(
                                    [
                                        str(self.__class__.__name__),
                                        str(sys._getframe().f_code.co_name)
                                    ]
                                ),
                                ' '.join(
                                    [
                                        'Error rotating log file',
                                        logPath,
                                        str(e)
                                    ]
                                )
                            )

            statusMessage = {'status': 'ok'}
            statusCode = 200

        except Exception as e:

            self.db.log(
                self.logFileKey,
                '.'.join(
                    [
                        str(self.__class__.__name__),
                        str(sys._getframe().f_code.co_name)
                    ]
                ),
                str(e)
            )


        return statusMessage, statusCode
    def clearTempFiles(self):
        """Clears orphaned files from temp folder."""

        statusMessage = {'error': 'Server error'}
        statusCode = 500

        try:

            tempFilePaths = glob.glob(
                os.path.join(
                    self.db.paths['temp']['path'],
                    '*'
                )
            )

            current = (datetime.datetime.now() - datetime.datetime.fromtimestamp(0)).total_seconds()

            for tempFilePath in tempFilePaths:

                fileTouched = max(
                    [
                        os.path.getctime(tempFilePath),
                        os.path.getmtime(tempFilePath),
                        os.path.getatime(tempFilePath)
                    ]
                )

                if (fileTouched + 3600.0) < current:

                    try:

                        os.remove(tempFilePath)

                    except: pass

            statusMessage = {'status': 'ok'}
            statusCode = 200

        except Exception as e:

            self.db.log(
                self.logFileKey,
                '.'.join(
                    [
                        str(self.__class__.__name__),
                        str(sys._getframe().f_code.co_name)
                    ]
                ),
                str(e)
            )


        return statusMessage, statusCode
    def getServerInfo(self, filters=None):
        """Get server data from DB."""

        serverData = {
            'server_data': []
        }

        try:

            dbMatch = ' ORDER BY collected DESC LIMIT 50'

            if isinstance(filters, dict):

                dbMatch = ''

                if 'sort' in filters.keys():

                    if 'key' in filters['sort'].keys() and 'direction' in filters['sort'].keys():

                        dbMatch = dbMatch + ' ORDER BY %(key)s %(direction)' % {
                            'key': filters['sort']['key'],
                            'direction': filters['sort']['direction']
                        }

                if 'paging' in filters.keys():

                    if 'size' in filters['paging'].keys() and 'page' in filters['paging'].keys():

                        dbMatch = dbMatch + ' LIMIT %(size)i OFFSET %(start_row)i' % {
                            'size': filters['paging']['size'],
                            'start_row': int(filters['paging']['size'] * filters['paging']['page'])
                        }


            dbInfos = self.db.get(
                'info',
                match=dbMatch
            )

            if isinstance(dbInfos, DbInfo):

                dbInfos = [dbInfos]

            if isinstance(dbInfos, list):

                for dbInfo in dbInfos:

                    serverData['server_data'].append(
                        dbInfo.getApiFormat()
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


        return serverData
    def collectServerInfo(self):
        """Collect server info."""

        statusMessage = {'error': 'Server error'}
        statusCode = 500

        serverInfo = {
            'collected': (datetime.datetime.now() - datetime.datetime.fromtimestamp(0)).total_seconds(),
            'temperature_celcius': None,
            'temperature_fahrenheit': None,
            'cpu_load_one_minute': None,
            'cpu_load_five_minute': None,
            'cpu_load_fifteen_minute': None,
            'ram_used': None,
            'ram_total': None,
            'originals_count': None,
            'originals_size': None,
            'quantizations_count': None,
            'quantizations_size': None,
            'thumbnails_count': None,
            'thumbnails_size': None,
            'disk_used': None,
            'disk_total': None
        }

        try:

            # Temperature

            try:

                with open('/sys/class/thermal/thermal_zone0/temp', 'r', encoding='utf-8') as f:

                    tempRaw = f.read()

                    tempC = int(tempRaw.strip()) / 1000.0
                    tempF = (tempC * (9.0 / 5.0)) + 32.0


                    serverInfo['temperature_celcius'] = tempC
                    serverInfo['temperature_fahrenheit'] = tempF

            except Exception as e:

                statusMessage['error'] = statusMessage['error'] + ' - Error collecting temperature data'

                self.log(
                    self.logFileKey,
                    '.'.join(
                        [
                            str(self.__class__.__name__),
                            str(sys._getframe().f_code.co_name),
                            'temperature'
                        ]
                    ),
                    str(e)
                )


            # CPU Load

            try:

                cpuRaw = self.runLocalCommand('uptime|awk \'{print $(NF-2) $(NF-1) $(NF)}\'')
                cpuRaw = str(cpuRaw).strip().split(',')

                if len(cpuRaw) == 3:

                    load1 = float(cpuRaw[0]) * 100.0
                    load5 = float(cpuRaw[1]) * 100.0
                    load15 = float(cpuRaw[2]) * 100.0


                    serverInfo['cpu_load_one_minute'] = load1
                    serverInfo['cpu_load_five_minute'] = load5
                    serverInfo['cpu_load_fifteen_minute'] = load15

            except Exception as e:

                statusMessage['error'] = statusMessage['error'] + ' - Error collecting CPU data'

                self.log(
                    self.logFileKey,
                    '.'.join(
                        [
                            str(self.__class__.__name__),
                            str(sys._getframe().f_code.co_name),
                            'cpu_load'
                        ]
                    ),
                    str(e)
                )


            # RAM Load

            try:

                ramRaw = self.runLocalCommand('free|sed -n \'2p\'|awk \'{print $2,$3,$4}\'')
                ramRaw = str(ramRaw).strip().split(' ')

                if len(ramRaw) == 3:

                    total = int(ramRaw[0])
                    used = int(ramRaw[1])


                    serverInfo['ram_used'] = used
                    serverInfo['ram_total'] = total

            except Exception as e:

                statusMessage['error'] = statusMessage['error'] + ' - Error collecting RAM data'

                self.log(
                    self.logFileKey,
                    '.'.join(
                        [
                            str(self.__class__.__name__),
                            str(sys._getframe().f_code.co_name),
                            'ram_load'
                        ]
                    ),
                    str(e)
                )


            # Images

            try:

                for pathKey in ['original', 'quantization', 'thumbnail']:

                    pathFiles = [
                        pathFile
                        for pathFile in glob.glob(
                            os.path.join(
                                self.db.paths[pathKey]['path'],
                                '*'
                            )
                        )
                        if os.path.isfile(pathFile)
                    ]

                    serverInfo[pathKey + 's_count'] = len(pathFiles)
                    serverInfo[pathKey + 's_size'] = sum(
                        [
                            os.path.getsize(pathFile)
                            for pathFile in pathFiles
                        ]
                    )

            except Exception as e:

                statusMessage['error'] = statusMessage['error'] + ' - Error collecting images data'

                self.log(
                    self.logFileKey,
                    '.'.join(
                        [
                            str(self.__class__.__name__),
                            str(sys._getframe().f_code.co_name),
                            'images'
                        ]
                    ),
                    str(e)
                )


            # Disk

            try:

                diskRaw = self.runLocalCommand('df -Pk|sed -n \'1!p\'|awk \'{{u=u+$3} {t=t+($3+$4)} {printf "%.3f %.3f\\n", u, t}}\'|tail -1')
                diskRaw = str(diskRaw).strip().split(' ')

                if len(diskRaw) == 2:

                    used = int(diskRaw[0].split('.')[0])
                    total = int(diskRaw[1].split('.')[0])


                    serverInfo['disk_used'] = used
                    serverInfo['disk_total'] = total

            except Exception as e:

                statusMessage['error'] = statusMessage['error'] + ' - Error collecting disk data'

                self.log(
                    self.logFileKey,
                    '.'.join(
                        [
                            str(self.__class__.__name__),
                            str(sys._getframe().f_code.co_name),
                            'disk'
                        ]
                    ),
                    str(e)
                )


            # Add to DB

            if all([serverInfo[key] is not None for key in serverInfo.keys()]) == True:

                self.db.new(
                    'info',
                    serverInfo
                )

                statusMessage = {'status': 'ok'}
                statusCode = 200

            del serverInfo

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


        return statusMessage, statusCode
    def runLocalCommand(self, command):
        """Runs os command."""

        commandOutput = ''

        try:

            localProcess = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )

            while True:

                processOut = localProcess.stdout.readline().strip()

                if len(processOut.strip('\n').strip('\r').strip()) > 0:

                    commandOutput = commandOutput + processOut + '\n'

                if processOut == '' and localProcess.poll() is not None:

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


        return commandOutput


    def log(self, logFileKey, source, status):
        """Relay log."""

        self.db.log(logFileKey, source, status)


        return
