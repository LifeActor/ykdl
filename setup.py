#!/usr/bin/env python3

from setuptools import setup
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

def find_packages(*tops):
    packages = []
    for d in tops:
        for root, dirs, files in os.walk(d, followlinks=True):
            if '__init__.py' in files:
                packages.append(root)
    return packages

# memo: pycryptodome is not being used now
REQ = ['m3u8>=1.0.0', 'jsengine>=1.0.5']
EXT = {
  'proxy': ['ExtProxy'],
  'rangefetch': ['urllib3'],
  'br': ['BrotliCFFI'],
  'js': ["QuickJS; os_name != 'nt'",
         "PyChakra>=2.2.0; os_name == 'nt' and platform_release < '8'"],
  'color': ["colorama; os_name == 'nt'"]
}
EXT['all-js'] = sum((v for k,v in EXT.items() if k != 'js'), [])
EXT['all'] = EXT['all-js'] + EXT['js']
EXT['net'] = EXT['proxy'] + EXT['rangefetch'] + EXT['br']

here = os.path.abspath(os.path.dirname(__file__))
README = read_file('README.rst')
CHANGES = read_file('CHANGELOG.rst')


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
    long_description = README + '\n\n' +  CHANGES,
    keywords = 'video download youku acfun bilibili',
    packages = find_packages('ykdl', 'cykdl'),
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
