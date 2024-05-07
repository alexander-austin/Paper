# Paper

![Image of working e-Paper display and connected Raspberry Pi](/Paper/static/android-chrome-192x192.png?raw=true)

Paper is a Raspberry Pi powered 7-color e-Paper picture frame display with a web interface and API.

One side goal was getting practice with vanilla JS/CSS.

Scissor.py is a background worker that uses the API to run periodic maintenance tasks.

Pencil.py is a background worker that polls GPIO, including optional MPU 6050 for automatic orientation control.

![Image of working e-Paper display and connected Raspberry Pi](/docs/display.jpg?raw=true)

![Screenshot of homepage and image gallery.](/docs/gallery.jpg?raw=true)
![Screenshot of image upload.](/docs/upload.jpg?raw=true)
![Screenshot of image tag & description editor.](/docs/edit.jpg?raw=true)
![Screenshot of image tag filter & sort selection.](/docs/filter.jpg?raw=true)
![Screenshot of sizing and orientation selection.](/docs/sizing.jpg?raw=true)
![Screenshot of main menu.](/docs/menu.jpg?raw=true)
![Screenshot of settings page.](/docs/settings.jpg?raw=true)
![Screenshot of user page.](/docs/user.jpg?raw=true)

# Install

This is a quick start guide assuming an install path of `/usr/local/paper` and will use default user account in Paper/DB.py if left unchanged.

## Hardware

### Hardware Requirements

Raspberry Pi (tested on models 4, 5, and Zero 2W).

Adequate USB-C Power Supply.

Micro SD card (sufficient for OS, software, and image storage).

[Waveshare 7 color, 7.3" e-Paper display and hat](https://www.waveshare.com/wiki/7.3inch_e-Paper_HAT_(F)_Manual).

### Hardware & OS Install

![Screenshot of user page.](/docs/wiring.png?raw=true)

Wire the display to the Raspberry Pi GPIO per [manufacturer’s specifications](https://www.waveshare.com/wiki/7.3inch_e-Paper_HAT_(F)_Manual#Working_With_Raspberry_Pi).

Install [Raspberry Pi OS](https://www.raspberrypi.com/software/) (Raspbian) and configure networking. It’s likely other compatible distros/operating systems will work as well, but that’s at your own risk and discretion.

Transfer project files to the Raspberry Pi. There are a number of ways to do this, but if you’re unsure, look at SFTP or git options.

### Open TCP Ports & Enable SPI

These enable http connectivity and SPI communication via GPIO. The last line is for the optional MPU 6050 gyro/accelerometer. Enable a firewall or your Raspberry Pi will be reachable via the internet. There are far more secure ways of enabling connectivity, please use with caution.

```
sudo apt-get install authbind
sudo touch /etc/authbind/byport/80
sudo chmod 777 /etc/authbind/byport/80
sudo touch /etc/authbind/byport/5000
sudo chmod 777 /etc/authbind/byport/5000

sudo sed -i 's/#dtparam=spi=on/dtparam=spi=on/g' /boot/config.txt
sudo raspi-config nonint do_i2c 0
```

## Software

### Install Python

This was written for python 3.12.

The [cryptography package](https://github.com/pyca/cryptography/blob/main/docs/index.rst) is primarily used to encrypt/decrypt passwords stored in the database, which are also salted. That said, security was not intended to be secure enough for being accessed via the open internet.

[Flask](https://flask.palletsprojects.com/en/3.0.x/) handles the routing, requests, and responses for the API, HTML/CSS/JS user interface, file uploads, and file downloads.

[Pillow](https://python-pillow.org/) (PIL) performs several tasks on uploaded images. It first gets basic image dimensions, generates multiple sizes of thumbnails for the UI, it also generates a palette of colors used by the e-Paper display and quantizes the image into several user-selectable formats, and finally converts the quantized image into a byte array to be sent to the display.

[pillow-avif-plugin](https://github.com/fdintino/pillow-avif-plugin) and [pillow-heif](https://github.com/bigcat88/pillow_heif) allow Pillow to open additional image file formats that have become more common in mobile devices.

[Requests](https://github.com/psf/requests) is an http client used by [Scissor.py](/Scissor.py) which runs in the background and uses the API to run period tasks such as displaying the next image in queue and rotating log files, etc. Redis and celery would have been an obvious replacement that enabled some other cool features, but this seemed like a more minimal install and memory efficient route.

[RPi.GPIO](https://pypi.org/project/RPi.GPIO/) and [spidev](https://github.com/doceme/py-spidev) enable GPIO SPI communication with the e-Paper display.

[smbus2](https://github.com/kplindegaard/smbus2) enables serial communication with (optional) MPU 6050 gyro/accelerometer.

```
sudo apt update && sudo apt upgrade -y
sudo apt install -y libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev libffi-dev zlib1g-dev wget build-essential libreadline-dev
sudo wget https://www.python.org/ftp/python/3.12.0/Python-3.12.0.tar.xz
sudo tar -xvf Python-3.12.0.tar.xz
cd Python-3.12.0
sudo ./configure --enable-optimizations
sudo make altinstall
sudo update-alternatives --install /usr/bin/python3 python3 /usr/local/bin/python3.12 1
sudo ln /usr/local/bin/python3.12 /usr/bin/python3.12
sudo rm Python-3.12.0.tar.xz
sudo rm -rf Python-3.12.0
/usr/bin/python3.12 -m pip install --upgrade pip
/usr/bin/python3.12 -m pip install --upgrade --force-reinstall -r /usr/local/paper/requirements.txt
```

### Install Other Software

[SQLite](https://www.sqlite.org/) is used for the database. [DB.py](/Paper/DB.py) acts as a wrapper and data validation/access, but could certainly use cleanup.

[Nginx](https://www.nginx.com/) is used as a minimal reverse http proxy server. You may notice the defaults set in [run.py](/run.py) and [prep.py](/prep.py) set the hostname/IP and listening port as 5000. Nginx forwards this to the standard http listening port 80. You can easily use [gunicorn](https://docs.gunicorn.org/en/stable/) instead and/or add https functionality. You are strongly encouraged to add more robust hardening and security, particularly if you are looking to have this accessible over the internet. This was only intended for hobby use over LAN.

```
sudo apt-get install sqlite3
sudo apt install curl gnupg2 ca-certificates lsb-release
sudo apt-get install nginx

sudo rm /etc/nginx/sites-enabled/*
sudo su
cat>/etc/nginx/sites-enabled/paper
server {
    client_max_body_size 2G;
    listen 80;
    listen [::]:80;
    server_name paper;

    error_page 502 /error.html;
    location = /error.html {
        root /usr/local/paper/Paper/templates;
        internal;
    }

    location / {
        proxy_pass http://127.0.0.1:5000/;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Prefix /;
    }
}
```

### Generate Keys, Service Files, and Run

[!CAUTION]
Only run this script ONCE. Database encryption key and salt are generated and old data may be lost if run a second time. In addition to creating keys/salt, it ingests any images stored in the [Paper/local](/Paper/local) path, then it creates the systemd service file for the server and background worker [Scissor.py](/Scissor.py). There's no need to run this if you're configuring you're own systemd service files or using a container or non-standard install. 

`/usr/bin/python3.12 /usr/local/paper/prep.py`

### First Login

From a browser, enter the IP of your Raspberry Pi.

Default login:

User: `admin`

Password: `Ch@ng3_!+`

The "User" tab will allow you to change this password or you can modify it in the [Paper/DB.py](/Paper/DB.py) file prior to running.

### Understanding Image Profiles

Example Originals:

![Original native protrait and landscape images.](/docs/originals.jpg?raw=true)

Quantized images with landscape orientation and cover sizing:

![Quantized images with landscape orientation and cover sizing.](/docs/landscape_cover.jpg?raw=true)

Quantized images with landscape orientation and fit sizing & blank background:

![Quantized images with landscape orientation and fit sizing & blank background.](/docs/landscape_fit_blank.jpg?raw=true)

Quantized images with landscape orientation and fit sizing & blurred background:

![Quantized images with landscape orientation and fit sizing & blurred background.](/docs/landscape_fit_blur.jpg?raw=true)

Quantized images with portrait orientation and cover sizing:

![Quantized images with portrait orientation and cover sizing.](/docs/portrait_cover.jpg?raw=true)

Quantized images with portrait orientation and fit sizing & blank background:

![Quantized images with portrait orientation and fit sizing & blank background.](/docs/portrait_fit_blank.jpg?raw=true)

Quantized images with portrait orientation and fit sizing & blurred background:

![Quantized images with portrait orientation and fit sizing & blurred background.](/docs/portrait_fit_blur.jpg?raw=true)

# API Documentation

## /api/alive

This lets you know the server is up an running. It is not a health check beyond that.

**GET**

Permissions Required
| Logged In | Media | Settings | Admin | API |
| :-: | :-: | :-: | :-: | :-: |
| :negative_squared_cross_mark: | :negative_squared_cross_mark: | :negative_squared_cross_mark: | :negative_squared_cross_mark: | :negative_squared_cross_mark: |

Data
`None`

cUrl Example
`curl -X GET -H "Accept: application/json" http://localhost:5000/api/alive`

Example Response
`{"status":"ok"}`

## /api/auth/login

This is the API login. You'll get a 'token' in both JSON and cookie format. Again, if you're going to use this on the open internet, I highly recommend hardening.

**POST**

Permissions Required
| Logged In | Media | Settings | Admin | API |
| :-: | :-: | :-: | :-: | :-: |
| :negative_squared_cross_mark: | :negative_squared_cross_mark: | :negative_squared_cross_mark: | :negative_squared_cross_mark: | :negative_squared_cross_mark: |

Data
```
{
    "username": "USERNAME",
    "password": "PASSWORD"
}
```

cUrl Example
`curl -c cookie.txt -d "{\"username\":\"admin\",\"password\":\"Ch@ng3_!+\"}" -X POST -H "Accept: application/json" -H "Content-Type: application/json" http://localhost:5000/api/auth/login`

Example Response
`{"expires":1710170153.528143,"expires_date_formatted":"2024/03/11 09:15:53.528","token":"F>,P#vNBhT$GT-qR^?ipyIZ%fF8Q]9=mGg3KCIBMBV-A[|c5?C.yewXWj6)9z$,S","user_id":1}`

## /api/images/< PATH >

### /api/images/all

This will return data for all images that have been ingested. Replacing "all" with an image id will return data for just that image eg `/api/images/42`.

**GET**

Permissions Required
| Logged In | Media | Settings | Admin | API |
| :-: | :-: | :-: | :-: | :-: |
| :white_check_mark: | :negative_squared_cross_mark: | :negative_squared_cross_mark: | :negative_squared_cross_mark: | :negative_squared_cross_mark: |

Data
```
{
    "token": "TOKEN"
}
```

cUrl Example
`curl -d "{\"token\":\"TOKEN\"}" -X GET -H "Accept: application/json" -H "Content-Type: application/json" http://localhost:5000/api/images/all`

Example Response
```
{
	"image_data":[
		{
			"id":12,
			"file":"test_image.jpg",
			"url":"/images/original/test_image.jpg",
			"width":4000,
			"height":1848,
			"bytes":4832269,
			"created":1710137622.565959,
			"created_date_formatted":"2024/03/11 00:13:42.565",
			"ingested":1710141223.997251,
			"ingested_date_formatted":"2024/03/11 01:13:43.997",
			"description":"This is a description for a test image.",
			"tags":[
				{
					"image_id":12,
					"category":{
						"id":1,
						"name":"Nature"
					},
					"subcategory":{
						"id":7,
						"name":"Forest"
					}
				}
			],
			"quantizations":[
				{
					"image_id":12,
					"width":800,
					"height":480,
					"bytes":111230,
					"orientation":"landscape",
					"url":"/images/quantization/test_image_landscape_fit_blur.png"
				},{
					"image_id":12,
					"width":800,
					"height":480,
					"bytes":89773,
					"orientation":"landscape",
					"url":"/images/quantization/test_image_landscape_fit_blank.png"
				},{
					"image_id":12,
					"width":800,
					"height":480,
					"bytes":97125,
					"orientation":"landscape",
					"url":"/images/quantization/test_image_landscape_cover.png"
				},{
					"image_id":12,
					"width":480,
					"height":800,
					"bytes":102811,
					"orientation":"portrait",
					"url":"/images/quantization/test_image_portrait_fit_blur.png"
				},{
					"image_id":12,
					"width":480,
					"height":800,
					"bytes":34939,
					"orientation":"portrait",
					"url":"/images/quantization/test_image_portrait_fit_blank.png"
				},{
					"image_id":12,
					"width":480,
					"height":800,
					"bytes":96367,
					"orientation":"portrait",
					"url":"/images/quantization/test_image_portrait_cover.png"
				}
			],
			"thumbnails":[
				{
					"image_id":12,
					"width":256,
					"height":256,
					"bytes":97788,
					"url":"/images/thumbnail/test_image_256.png"
				},{
					"image_id":12,
					"width":128,
					"height":128,
					"bytes":24999,
					"url":"/images/thumbnail/test_image_128.png"
				},{
					"image_id":12,
					"width":64,
					"height":64,
					"bytes":6583,
					"url":"/images/thumbnail/test_image_64.png"
				}
			]
		},
		... [ cont ] ...
	]
}
```

### /api/images/upload

This is for uploading and ingesting new images. Image files are assumed to be chunked, but don't have to be. Tag and description data are optional. The file index doesn't matter as much as long as it's used consistently to identify the same file, but the chunk index matters.

**POST**

Permissions Required
| Logged In | Media | Settings | Admin | API |
| :-: | :-: | :-: | :-: | :-: |
| :white_check_mark: | :white_check_mark: | :negative_squared_cross_mark: | :negative_squared_cross_mark: | :white_check_mark: |

Data
(Form data)
file=binary file or chunk
info=
```
{
    "info": [
        {
            "index": 0,
            "name": "test_image.jpg",
            "size": 4832269,
            "chunks": 1,
            "description": "Test description.",
            "tags": [
                {
                    "image_id": 0,
                    "category_id": 0,
                    "subcategory_id": 0
                }
            ]
        }
    ],
    "current": {
        "index": 0,
        "chunk": 0
    }
}
```

cUrl Example
`curl -b cookie.txt -X POST -H "Content-Type: multipart/form-data" -F "file=@Paper/local/test_image.jpg" -F "info={\"info\":[{\"index\":0,\"name\":\"test_image.jpg\",\"size\":4832269,\"chunks\":1,\"description\":\"Test description.\",\"tags\":[{\"image_id\":0,\"category_id\":0,\"subcategory_id\":0}]}],\"current\":{\"index\":0,\"chunk\":0}};type=application/json" http://localhost:5000/api/images/upload`

Example Response

When chunk received, but file not fully processed:

```
{
	"current_file": "test_image.jpg",
	"progress": [
		{
			"chunks": 4,
			"index": 0,
			"name": "test_image.jpg",
			"progress": 25.0,
			"size": 4832269
		}
	]
}
```

When all chunks and files have been uploaded and processed, the response will be the same as from `/api/images/all`.

### /api/images/delete

This is for deleting images.

**DELETE**

Permissions Required
| Logged In | Media | Settings | Admin | API |
| :-: | :-: | :-: | :-: | :-: |
| :negative_squared_cross_mark: | :white_check_mark: | :white_check_mark: | :white_check_mark: | :white_check_mark: |

Data
```
{
	"token": "TOKEN",
    "id": 0
}
```

cUrl Example
`curl -d "{\"token\":\"TOKEN\", \"id\": 0}" -X DELETE -H "Accept: application/json" -H "Content-Type: application/json" http://localhost:5000/api/images/delete`

Example Response
(Similar to /api/images/all)

## /api/settings/< PATH >

### /api/settings/image

This retrieves and edits image settings.

**GET**

Permissions Required
| Logged In | Media | Settings | Admin | API |
| :-: | :-: | :-: | :-: | :-: |
| :white_check_mark: | :white_check_mark: | :white_check_mark: | :white_check_mark: | :white_check_mark: |

Data
```
{
    "token": "TOKEN"
}
```

cUrl Example
`curl -d "{\"token\":\"TOKEN\"}" -X GET -H "Accept: application/json" -H "Content-Type: application/json" http://localhost:5000/api/settings/image`

Example Response
```
{
	"image_settings": {
		"current": -1,
		"queue": [],
		"filters": [],
		"orientation": "landscape",
        "orientation_control": "auto",
        "orientation_auto_control_available": true,
		"size": [800, 480],
		"sizing": {
			"type": "fit",
			"fill": "blur"
		},
		"blur_brightness": 0.5,
		"thumbnail_sizes": [256, 128, 64],
		"extension": "png",
		"palette": {
			"black": [0, 0, 0],
			"white": [255, 255, 255],
			"green": [0, 255, 0],
			"blue": [0, 0, 255],
			"red": [255, 0, 0],
			"yellow": [255, 255, 0],
			"orange": [255, 128, 0]
		}
	}
}
```

**POST**

Permissions Required
| Logged In | Media | Settings | Admin | API |
| :-: | :-: | :-: | :-: | :-: |
| :negative_squared_cross_mark: | :white_check_mark: | :white_check_mark: | :white_check_mark: | :white_check_mark: |

Data
```
{
	"token": "TOKEN",
    "orientation": "landscape"
}
```

cUrl Example
`curl -d "{\"token\":\"TOKEN\", \"orientation\": \"landscape\"}" -X POST -H "Accept: application/json" -H "Content-Type: application/json" http://localhost:5000/api/settings/image`

Example Response
(Similar to GET /api/settings/image)

### /api/settings/password

This retrieves and edits password requirement settings.

**GET**

Permissions Required
| Logged In | Media | Settings | Admin | API |
| :-: | :-: | :-: | :-: | :-: |
| :white_check_mark: | :white_check_mark: | :white_check_mark: | :white_check_mark: | :white_check_mark: |

Data
```
{
    "token": "TOKEN"
}
```

cUrl Example
`curl -d "{\"token\":\"TOKEN\"}" -X GET -H "Accept: application/json" -H "Content-Type: application/json" http://localhost:5000/api/settings/password`

Example Response
```
{
	"password_settings": {
		"upper": true,
		"lower": true,
		"number": true,
		"special": true,
		"length": 8
	}
}
```

**POST**

Permissions Required
| Logged In | Media | Settings | Admin | API |
| :-: | :-: | :-: | :-: | :-: |
| :negative_squared_cross_mark: | :negative_squared_cross_mark: | :white_check_mark: | :white_check_mark: | :white_check_mark: |

Data
```
{
	"token": "TOKEN",
    "special": false
}
```

cUrl Example
`curl -d "{\"token\":\"TOKEN\", \"special\": false}" -X POST -H "Accept: application/json" -H "Content-Type: application/json" http://localhost:5000/api/settings/password`

Example Response
(Similar to GET /api/settings/password)

### /api/settings/category

This retrieves and edits current category/subcategory data.

**GET**

Permissions Required
| Logged In | Media | Settings | Admin | API |
| :-: | :-: | :-: | :-: | :-: |
| :white_check_mark: | :white_check_mark: | :white_check_mark: | :white_check_mark: | :white_check_mark: |

Data
```
{
    "token": "TOKEN"
}
```

cUrl Example
`curl -d "{\"token\":\"TOKEN\"}" -X GET -H "Accept: application/json" -H "Content-Type: application/json" http://localhost:5000/api/settings/category`

Example Response
```
{
    "category_data": [
		{
            "id": 0,
            "name": "People",
            "subcategories": [
                {
                    "category_id": 0,
                    "id": 0,
                    "name": "Family"
                },
                {
                    "category_id": 0,
                    "id": 1,
                    "name": "Friend"
                },
                {
                    "category_id": 0,
                    "id": 2,
                    "name": "Coworker"
                }
            ]
        },
        {
            "id": 1,
            "name": "Nature",
            "subcategories": [
                {
                    "category_id": 1,
                    "id": 3,
                    "name": "Mountains"
                },
                {
                    "category_id": 1,
                    "id": 4,
                    "name": "Ocean"
                },
                {
                    "category_id": 1,
                    "id": 5,
                    "name": "Lake"
                },
                {
                    "category_id": 1,
                    "id": 6,
                    "name": "Beach"
                },
                {
                    "category_id": 1,
                    "id": 7,
                    "name": "Forest"
                },
                {
                    "category_id": 1,
                    "id": 8,
                    "name": "Desert"
                }
            ]
        },
        {
            "id": 2,
            "name": "Places",
            "subcategories": [
                {
                    "category_id": 2,
                    "id": 9,
                    "name": "Home"
                },
                {
                    "category_id": 2,
                    "id": 10,
                    "name": "Work"
                }
            ]
        },
		{
            "id": 3,
            "name": "Art",
            "subcategories": [
                {
                    "category_id": 3,
                    "id": 11,
                    "name": "Personal"
                },
                {
                    "category_id": 3,
                    "id": 12,
                    "name": "Renaissance"
                },
                {
                    "category_id": 3,
                    "id": 13,
                    "name": "Modern"
                }
            ]
        }
    ]
}
```

**POST**

Permissions Required
| Logged In | Media | Settings | Admin | API |
| :-: | :-: | :-: | :-: | :-: |
| :negative_squared_cross_mark: | :negative_squared_cross_mark: | :white_check_mark: | :white_check_mark: | :white_check_mark: |

Data
```
{
	"token": "TOKEN",
    "action": "add_category",
	"category_name": "My New Category"
}
```

cUrl Example
`curl -d "{\"token\":\"TOKEN\", \"action\": \"add_category\", \"category_name\": \"My New Category\"}" -X POST -H "Accept: application/json" -H "Content-Type: application/json" http://localhost:5000/api/settings/category`

Example Response
(Similar to GET /api/settings/category)

### /api/settings/user

This allows you to create users, modify permissions, set passwords, and remove users, etc. All logged in users can get & set their own data, but admin & api privilege users can retrieve and modify data for all users. You can't see other users passwords without direct DB access, but you can reset them.

**GET**

Permissions Required (Own user data)
| Logged In | Media | Settings | Admin | API |
| :-: | :-: | :-: | :-: | :-: |
| :white_check_mark: | :white_check_mark: | :white_check_mark: | :white_check_mark: | :white_check_mark: |

Permissions Required (ALL user data)
| Logged In | Media | Settings | Admin | API |
| :-: | :-: | :-: | :-: | :-: |
| :negative_squared_cross_mark: | :negative_squared_cross_mark: | :negative_squared_cross_mark: | :white_check_mark: | :white_check_mark: |

Data
```
{
    "token": "TOKEN"
}
```

cUrl Example
`curl -d "{\"token\":\"TOKEN\"}" -X GET -H "Accept: application/json" -H "Content-Type: application/json" http://localhost:5000/api/settings/user`

Example Response
```
{
    "user_data": [
        {
            "family_name": "API",
            "given_name": "Scissor",
            "id": 0,
            "tokens": [],
            "user_permissions": [
                {
                    "permission_id": 0,
                    "permissions": {
                        "description": "Full API control.",
                        "id": 0,
                        "name": "API"
                    },
                    "user_id": 0
                }
            ],
            "username": "scissor_api"
        },
        {
            "family_name": "",
            "given_name": "",
            "id": 1,
            "tokens": [
                {
                    "expires": 1713420132.288834,
                    "expires_date_formatted": "2024/04/18 00:02:12.288",
                    "token": "TOKEN",
                    "user_id": 1
                }
            ],
            "user_permissions": [
                {
                    "permission_id": 1,
                    "permissions": {
                        "description": "All \"Settings\" and \"Media\" permissions as well as allows user to add, edit, and delete users including resetting passwords.",
                        "id": 1,
                        "name": "Admin"
                    },
                    "user_id": 1
                },
                {
                    "permission_id": 2,
                    "permissions": {
                        "description": "All \"Media\" permissions as well as allows user to change settings.",
                        "id": 2,
                        "name": "Settings"
                    },
                    "user_id": 1
                },
                {
                    "permission_id": 3,
                    "permissions": {
                        "description": "Allows user to select, upload, delete, and modify media/tags.",
                        "id": 3,
                        "name": "Media"
                    },
                    "user_id": 1
                }
            ],
            "username": "admin"
        }
    ]
}
```

**POST**

Permissions Required (Own user data)
| Logged In | Media | Settings | Admin | API |
| :-: | :-: | :-: | :-: | :-: |
| :white_check_mark: | :white_check_mark: | :white_check_mark: | :white_check_mark: | :white_check_mark: |

Permissions Required (ALL user data)
| Logged In | Media | Settings | Admin | API |
| :-: | :-: | :-: | :-: | :-: |
| :negative_squared_cross_mark: | :negative_squared_cross_mark: | :negative_squared_cross_mark: | :white_check_mark: | :white_check_mark: |

Data
```
{
	"token": "TOKEN",
    "id": 0,
    "given_name": "New Name"
}
```

cUrl Example
`curl -d "{\"token\":\"TOKEN\", \"id\": 0, \"given_name\": \"New Name\"}" -X POST -H "Accept: application/json" -H "Content-Type: application/json" http://localhost:5000/api/settings/user`

Example Response
(Similar to GET /api/settings/user)

**DELETE**

Permissions Required
| Logged In | Media | Settings | Admin | API |
| :-: | :-: | :-: | :-: | :-: |
| :negative_squared_cross_mark: | :negative_squared_cross_mark: | :negative_squared_cross_mark: | :white_check_mark: | :white_check_mark: |

Data
```
{
	"token": "TOKEN",
    "id": 0
}
```

cUrl Example
`curl -d "{\"token\":\"TOKEN\", \"id\": 0}" -X DELETE -H "Accept: application/json" -H "Content-Type: application/json" http://localhost:5000/api/settings/user`

Example Response
(Similar to GET /api/settings/user)

## /api/maintenance/< PATH >

### /api/maintenance/export

This exports credentials for the worker API *locally* to disk.

**POST**

Permissions Required
| Logged In | Media | Settings | Admin | API |
| :-: | :-: | :-: | :-: | :-: |
| :white_check_mark: | :white_check_mark: | :white_check_mark: | :white_check_mark: | :white_check_mark: |

Data
`None`

cUrl Example
`curl -X POST -H "Accept: application/json" http://localhost:5000/api/maintenance/export`

Example Response
```
{
    "status": "ok"
}
```

### /api/maintenance/info

This retrieves basic server info such as CPU, disk, and RAM usage, etc. The POST verb runs the collection routine.

**GET**

Permissions Required
| Logged In | Media | Settings | Admin | API |
| :-: | :-: | :-: | :-: | :-: |
| :negative_squared_cross_mark: | :negative_squared_cross_mark: | :negative_squared_cross_mark: | :white_check_mark: | :white_check_mark: |

Data
```
{
	"token": "TOKEN"
}
```

cUrl Example
`curl -d "{\"token\":\"TOKEN\"}" -X GET -H "Accept: application/json" -H "Content-Type: application/json" http://localhost:5000/api/maintenance/info`

Example Response
```
{
    "server_data": [
        {
            "collected": 1712827334.514194,
            "collected_date_formatted": "2024/04/11 03:22:14.514",
            "cpu_load_fifteen_minute": 1.0,
            "cpu_load_five_minute": 4.0,
            "cpu_load_one_minute": 8.0,
            "disk_total": 245986056,
            "disk_used": 6323728,
            "originals_count": 58,
            "originals_size": 155537918,
            "quantizations_count": 348,
            "quantizations_size": 29601092,
            "ram_total": 7999812,
            "ram_used": 688992,
            "temperature_celcius": 45.277,
            "temperature_fahrenheit": 113.49860000000001,
            "thumbnails_count": 174,
            "thumbnails_size": 6876338
        },
        {
            "collected": 1712823731.237083,
            "collected_date_formatted": "2024/04/11 02:22:11.237",
            "cpu_load_fifteen_minute": 1.0,
            "cpu_load_five_minute": 5.0,
            "cpu_load_one_minute": 9.0,
            "disk_total": 245986056,
            "disk_used": 6240996,
            "originals_count": 38,
            "originals_size": 102389708,
            "quantizations_count": 228,
            "quantizations_size": 19824120,
            "ram_total": 7999812,
            "ram_used": 308244,
            "temperature_celcius": 45.277,
            "temperature_fahrenheit": 113.49860000000001,
            "thumbnails_count": 114,
            "thumbnails_size": 4913390
        },
        {
            "collected": 1712820126.630725,
            "collected_date_formatted": "2024/04/11 01:22:06.630",
            "cpu_load_fifteen_minute": 28.999999999999996,
            "cpu_load_five_minute": 64.0,
            "cpu_load_one_minute": 93.0,
            "disk_total": 245986056,
            "disk_used": 6240732,
            "originals_count": 38,
            "originals_size": 102389708,
            "quantizations_count": 228,
            "quantizations_size": 19824120,
            "ram_total": 7999812,
            "ram_used": 299408,
            "temperature_celcius": 55.017,
            "temperature_fahrenheit": 131.0306,
            "thumbnails_count": 114,
            "thumbnails_size": 4913390
        }
    ]
}
```

**POST**

Permissions Required
| Logged In | Media | Settings | Admin | API |
| :-: | :-: | :-: | :-: | :-: |
| :negative_squared_cross_mark: | :negative_squared_cross_mark: | :negative_squared_cross_mark: | :white_check_mark: | :white_check_mark: |

Data
```
{
	"token": "TOKEN"
}
```

cUrl Example
`curl -d "{\"token\":\"TOKEN\"}" -X POST -H "Accept: application/json" -H "Content-Type: application/json" http://localhost:5000/api/maintenance/info`

Example Response
```
{
    "status": "ok"
}
```

### /api/maintenance/ingest

This initiates ingesting images that were manually added to the local folder.

**POST**

Permissions Required
| Logged In | Media | Settings | Admin | API |
| :-: | :-: | :-: | :-: | :-: |
| :negative_squared_cross_mark: | :negative_squared_cross_mark: | :negative_squared_cross_mark: | :white_check_mark: | :white_check_mark: |

Data
```
{
	"token": "TOKEN"
}
```

cUrl Example
`curl -d "{\"token\":\"TOKEN\"}" -X POST -H "Accept: application/json" -H "Content-Type: application/json" http://localhost:5000/api/maintenance/ingest`

Example Response
```
{
    "status": "ok"
}
```

### /api/maintenance/logs

This retrieves and rotates server logs.

**GET**

Permissions Required
| Logged In | Media | Settings | Admin | API |
| :-: | :-: | :-: | :-: | :-: |
| :negative_squared_cross_mark: | :negative_squared_cross_mark: | :negative_squared_cross_mark: | :white_check_mark: | :white_check_mark: |

Data
```
{
	"token": "TOKEN",
    "keys": [
        "backend_log",
        "server_log",
        "db_log"
    ],
    "paging": {
        "size": 25,
        "page": 0
    },
    "sort": "ASC"
}
```

cUrl Example
`curl -d "{\"token\":\"TOKEN\"}" -X GET -H "Accept: application/json" -H "Content-Type: application/json" http://localhost:5000/api/maintenance/logs`

Example Response
```
{
    "log_data": {
        "files": [
            "/usr/local/paper/Paper/data/Paper_Backend.log",
            "/usr/local/paper/Paper/data/Paper_Server.log",
            "/usr/local/paper/Paper/data/Paper_DB.log",
            "/usr/local/paper/Paper/data/Paper_Display.log",
            "/usr/local/paper/Paper/data/Paper_Scissor.log"
        ],
        "keys": [
            "backend_log",
            "server_log",
            "db_log",
            "display_log",
            "scissor_log"
        ],
        "logs": [
            {
                "date": "2024/04/11 00:21:57.527",
                "entry": "started.",
                "source": "DB.__init__"
            },
            {
                "date": "2024/04/11 00:21:57.532",
                "entry": "started.",
                "source": "DB.__init__"
            },
            {
                "date": "2024/04/11 00:21:57.631",
                "entry": "started.",
                "source": "DB.__init__"
            },
            {
                "date": "2024/04/11 00:21:57.636",
                "entry": "started.",
                "source": "DB.__init__"
            }
        ]
    }
}
```

**DELETE**

Permissions Required
| Logged In | Media | Settings | Admin | API |
| :-: | :-: | :-: | :-: | :-: |
| :negative_squared_cross_mark: | :negative_squared_cross_mark: | :negative_squared_cross_mark: | :white_check_mark: | :white_check_mark: |

Data
```
{
	"token": "TOKEN"
}
```

cUrl Example
`curl -d "{\"token\":\"TOKEN\"}" -X DELETE -H "Accept: application/json" -H "Content-Type: application/json" http://localhost:5000/api/maintenance/logs`

Example Response
```
{
    "status": "ok"
}
```

### /api/maintenance/task

This gets and updates periodic task data used by Scissor.py.

**GET**

Permissions Required
| Logged In | Media | Settings | Admin | API |
| :-: | :-: | :-: | :-: | :-: |
| :negative_squared_cross_mark: | :negative_squared_cross_mark: | :negative_squared_cross_mark: | :white_check_mark: | :white_check_mark: |

Data
```
{
	"token": "TOKEN"
}
```

cUrl Example
`curl -d "{\"token\":\"TOKEN\"}" -X GET -H "Accept: application/json" -H "Content-Type: application/json" http://localhost:5000/api/maintenance/task`

Example Response
```
{
    "task_data": [
        {
            "delay": 1800,
            "description": "Displays next image in queue.",
            "endpoint": "/api/images/display",
            "last": 1712827441.812651,
            "last_date_formatted": "2024/04/11 03:24:01.812",
            "method": "POST",
            "name": "Rotate Images",
            "status": "ok"
        },
        {
            "delay": 2700,
            "description": "Ingests manually added files in \"local\" folder to DB.",
            "endpoint": "/api/maintenance/ingest",
            "last": 1712825536.647386,
            "last_date_formatted": "2024/04/11 02:52:16.647",
            "method": "POST",
            "name": "Ingest Local",
            "status": "ok"
        },
        {
            "delay": 3600,
            "description": "Gets server statistics.",
            "endpoint": "/api/maintenance/info",
            "last": 1712827334.69227,
            "last_date_formatted": "2024/04/11 03:22:14.692",
            "method": "POST",
            "name": "Server Info",
            "status": "ok"
        },
        {
            "delay": 14400,
            "description": "Removes expired tokens from DB.",
            "endpoint": "/api/maintenance/tokens",
            "last": 1712820126.755673,
            "last_date_formatted": "2024/04/11 01:22:06.755",
            "method": "DELETE",
            "name": "Reap Tokens",
            "status": "ok"
        },
        {
            "delay": 86400,
            "description": "Removes old entries from log files.",
            "endpoint": "/api/maintenance/logs",
            "last": 1712820126.80903,
            "last_date_formatted": "2024/04/11 01:22:06.809",
            "method": "DELETE",
            "name": "Rotate Logs",
            "status": "ok"
        },
        {
            "delay": 86400,
            "description": "Removes old files from temp folder.",
            "endpoint": "/api/maintenance/temp",
            "last": 1712820126.866955,
            "last_date_formatted": "2024/04/11 01:22:06.866",
            "method": "DELETE",
            "name": "Clear Temp Files",
            "status": "ok"
        }
    ]
}
```

**POST**

Permissions Required
| Logged In | Media | Settings | Admin | API |
| :-: | :-: | :-: | :-: | :-: |
| :negative_squared_cross_mark: | :negative_squared_cross_mark: | :negative_squared_cross_mark: | :white_check_mark: | :white_check_mark: |

Data
```
{
	"token": "TOKEN",
    "data": {
        "delay": 1800,
        "description": "Displays next image in queue.",
        "endpoint": "/api/images/display",
        "last": 1712827441.812651,
        "method": "POST",
        "name": "Rotate Images",
        "status": "ok"
    }
}
```

cUrl Example
`curl -d "{\"token\": \"TOKEN\", \"data\": {\"delay\": 1800, \"description\": \"Displays next image in queue.\", \"endpoint\": \"/api/images/display\", \"last\": 1712827441.812651, \"method\": \"POST\", \"name\": \"Rotate Images\", \"status\": \"ok\"}}" -X GET -H "Accept: application/json" -H "Content-Type: application/json" http://localhost:5000/api/maintenance/task`

Example Response
(Similar to GET /api/maintenance/task)

### /api/maintenance/temp

This clears out the temp folder.

**DELETE**

Permissions Required
| Logged In | Media | Settings | Admin | API |
| :-: | :-: | :-: | :-: | :-: |
| :negative_squared_cross_mark: | :negative_squared_cross_mark: | :negative_squared_cross_mark: | :white_check_mark: | :white_check_mark: |

Data
```
{
	"token": "TOKEN"
}
```

cUrl Example
`curl -d "{\"token\":\"TOKEN\"}" -X DELETE -H "Accept: application/json" -H "Content-Type: application/json" http://localhost:5000/api/maintenance/temp`

Example Response
```
{
    "status": "ok"
}
```

### /api/maintenance/tokens

This clears out expired tokens from the DB.

**DELETE**

Permissions Required
| Logged In | Media | Settings | Admin | API |
| :-: | :-: | :-: | :-: | :-: |
| :negative_squared_cross_mark: | :negative_squared_cross_mark: | :negative_squared_cross_mark: | :white_check_mark: | :white_check_mark: |

Data
```
{
	"token": "TOKEN"
}
```

cUrl Example
`curl -d "{\"token\":\"TOKEN\"}" -X DELETE -H "Accept: application/json" -H "Content-Type: application/json" http://localhost:5000/api/maintenance/tokens`

Example Response
```
{
    "status": "ok"
}
```
