#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup

try:
    import wheel
except:
    pass

import os, codecs, platform

here = os.path.abspath(os.path.dirname(__file__))
README = codecs.open(os.path.join(here, 'README.rst'), encoding='utf8').read()
CHANGES = codecs.open(os.path.join(here, 'CHANGELOG.rst'), encoding='utf8').read()

def find_packages(*tops):
    packages = []
    for d in tops:
        for root, dirs, files in os.walk(d, followlinks=True):
            if '__init__.py' in files:
                packages.append(root)
    return packages

from ykdl.version import __version__

REQ = ['m3u8', 'pycryptodome', 'urllib3']

setup(
    name = "ykdl",
    version = __version__,
    author = "Zhang Ning",
    author_email = "zhangn1985@gmail.com",
    url = "https://github.com/zhangn1985/ykdl",
    license = "MIT",
    description = "a video downloader written in Python",
    long_description = README + '\n\n' +  CHANGES,
    keywords = "video download youku acfun bilibili",
    packages = find_packages('ykdl', 'cykdl'),
    requires = REQ,
    install_requires = REQ,
    platforms = 'any',
    zip_safe = True,
    classifiers = [
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Internet",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Multimedia",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Multimedia :: Video",
        "Topic :: Utilities"
    ],
      entry_points={
          "console_scripts": ["ykdl=cykdl.__main__:main"]
      },
)
