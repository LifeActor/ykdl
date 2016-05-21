from distutils.core import setup

import os

def find_packages(*tops):
    packages = []
    for d in tops:
        for root, dirs, files in os.walk(d, followlinks=True):
            if '__init__.py' in files:
                packages.append(root)
    return packages

setup(
    name = "you-get",
    version = "v1.0.6:0.3.34@soimort",
    author = "Mort Yao, Zhang Ning",
    author_email = "mort.yao@gmail.com, zhangn1985@gmail.com",
    url = "https://github.com/zhangn1985/you-get",
    license = "MIT",
    description = "a video downloader written in Python 3",
    keywords = "video download youtube youku",
    packages = find_packages('you_get'),
    platforms = 'any',
    classifiers = [
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.0",
        "Programming Language :: Python :: 3.1",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Topic :: Internet",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Multimedia",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Multimedia :: Video",
        "Topic :: Utilities"
    ],
    scripts = ['you-get']
)
