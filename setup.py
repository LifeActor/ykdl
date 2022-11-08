#!/usr/bin/env python3

from setuptools import setup, find_packages
import os
import re


def read_file(*paths):
    with open(os.path.join(here, *paths), 'r', encoding='utf-8') as fp:
        return fp.read()

def get_version():
    content = read_file('ykdl', 'version.py')
    version_match = re.search('^__version__ = [\'"]([^\'"]+)', content, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')

# memo: pycryptodome is not being used now
REQ = [
    'm3u8>=1.0.0',
    'jsengine>=1.0.5',
    "colorama;os_name=='nt'",
]
EXT = {
  'proxy': ['ExtProxy'],
  'br': ['BrotliCFFI'],
}
EXT['net'] = sum(EXT.values(), [])
EXT['js'] = ['quickjs']
EXT['all'] = list(set(sum((EXT.values()), [])))

here = os.path.abspath(os.path.dirname(__file__))
LONGS = '\n\n'.join((
    read_file('README.rst'),
    *read_file('CHANGELOG.rst').split('\n\n\n')[:4],
    '`See full change log '
    '<https://github.com/SeaHOH/ykdl/blob/master/CHANGELOG.rst>`_.\n'
))


setup(
    name = 'ykdl',
    version = get_version(),
    author = 'Zhang Ning',
    author_email = 'zhangn1985@gmail.com',
    maintainer = 'SeaHOH',
    maintainer_email = 'seahoh@gmail.com',
    url = 'https://github.com/SeaHOH/ykdl',
    license = 'MIT',
    description = 'a video downloader written in Python',
    long_description = LONGS,
    keywords = 'video download youku acfun bilibili',
    packages = find_packages(here),
    install_requires = REQ,
    extras_require = EXT,
    platforms = 'any',
    zip_safe = True,
    package_data = {
        'ykdl': ['extractors/*.js', 'extractors/*/*.js'],
    },
    python_requires = '>=3.5',

    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Internet',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Multimedia',
        'Topic :: Multimedia :: Sound/Audio',
        'Topic :: Multimedia :: Video',
        'Topic :: Utilities'
    ],
    entry_points = {
        'console_scripts': ['ykdl=cykdl.__main__:main']
    },
)
