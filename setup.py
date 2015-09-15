try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    "description": "CameraLink communication with Wasatch devices ",
    "author": "Nathan Harrington",
    "url": "https://github.com/nharringtonwasatch/WasatchCameraLink",
    "download_url": \
        "https://github.com/nharringtonwasatch/WasatchCameraLink",
    "author_email": "nharrington@wasatchphotonics.com.",
    "version": "1.0.0",
    "install_requires": ["numpy"],
    "packages": ["wasatchcameralink"],
    "scripts": [],
    "name": "WasatchCameraLink"
}

setup(**config)
