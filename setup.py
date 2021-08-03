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
try:
    from ykdl.util.jsengine import JSEngine
except ImportError:
    JSEngine = None

REQ = ['m3u8']  # remove pycryptodome, it is not being used now
EXT = {
  'proxy': ['ExtProxy'],
  'rangefetch': ['urllib3'],
  'js': JSEngine and [] or ['PyChakra>=2.2.0'],
  'color': os.name != 'nt' and [] or ['colorama']
}
EXT['all'] = sum((rs for rs in EXT.values()), [])
EXT['all-js'] = EXT['all'].copy()
try:
    EXT['all-js'].remove(EXT['js'][0])
except IndexError:
    pass
EXT['net'] = EXT['proxy'] + EXT['rangefetch']


setup(
    name = "ykdl",
    version = __version__,
    author = "Zhang Ning",
    author_email = "zhangn1985@gmail.com",
    maintainer = "SeaHOH",
    maintainer_email = "seahoh@gmail.com",
    url = "https://github.com/zhangn1985/ykdl",
    license = "MIT",
    description = "a video downloader written in Python",
    long_description = README + '\n\n' +  CHANGES,
    keywords = "video download youku acfun bilibili",
    packages = find_packages('ykdl', 'cykdl'),
    requires = REQ,
    install_requires = REQ,
    extras_require = EXT,
    platforms = 'any',
    zip_safe = True,
    package_data = {
        'ykdl': ['extractors/*.js', 'extractors/*/*.js'],
    },

    classifiers = [
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
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
