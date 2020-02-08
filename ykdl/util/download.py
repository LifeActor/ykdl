#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import os
import sys
from logging import getLogger
from ykdl.compact import Request, urlopen
from ykdl.util import log
from ykdl.util.wrap import encode_for_wrap
from .html import fake_headers

logger = getLogger("downloader")

try:
    from concurrent.futures import ThreadPoolExecutor
    MultiThread = True
except:
    MultiThread = False
    logger.warning("failed to import ThreadPoolExecutor!")
    logger.warning("multithread download disabled!")
    logger.warning("please install concurrent.futures from https://github.com/agronholm/pythonfutures !")

def simple_hook(arg1, arg2, arg3):
    if arg3 > 0:
        percent = int(arg1 * arg2 * 100 / arg3)
        if percent > 100:
            percent = 100
        sys.stdout.write('\r %3d' % percent + '%')
        sys.stdout.flush()
    else:
        sys.stdout.write('\r' + str(round(arg1 * arg2 / 1048576, 1)) + 'MB')
        sys.stdout.flush()

def save_url(url, name, ext, status, part=None, reporthook=simple_hook):
    if part is None:
        print("Download: " + name)
        name = name + '.' + ext
        part = 0
    else:
        print("Download: " + name + " part %d" % part)
        name = name + '_%d_.' % part + ext
    bs = 1024 * 8
    size = -1
    read = 0
    blocknum = 0
    open_mode = 'wb'
    req = Request(url, headers=fake_headers)
    if os.path.exists(name):
        filesize = os.path.getsize(name)
        req.add_header('Range', 'bytes=%d-' % filesize)
        response = urlopen(req, None)
        if response.status == 206:
            size = int(response.headers['Content-Range'].split('/')[-1])
            if filesize == size:
                print('Skipped: file already downloaded')
                status[part] = 1
                return
            if filesize < size:
                if filesize:
                    blocknum = int(filesize / bs)
                open_mode = 'ab'
    else:
        response = urlopen(req, None)
    if size < 0:
        size = int(response.headers.get('Content-Length', -1))
    reporthook(blocknum, bs, size)
    with open(name, open_mode) as tfp:
        while True:
            block = response.read(bs)
            if not block:
                break
            read += len(block)
            tfp.write(block)
            blocknum += 1
            reporthook(blocknum, bs, size)
    if os.path.exists(name):
        filesize = os.path.getsize(name)
        if filesize == size:
            status[part] = 1

def save_urls(urls, name, ext, jobs=1):
    ext = encode_for_wrap(ext)
    status = [0] * len(urls)
    if len(urls) == 1:
        save_url(urls[0], name, ext, status)
        if 0 in status:
            logger.error("donwload failed")
        return not 0 in status
    if not MultiThread:
        for no, u in enumerate(urls):
            save_url(u, name, ext, status, part=no)
    else:
        with ThreadPoolExecutor(max_workers=jobs) as worker:
            for no, u in enumerate(urls):
                worker.submit(save_url, u, name, ext, status, part=no)
            worker.shutdown()
    for no, a in enumerate(status):
        if a == 0:
            logger.error("downloader failed at part {}".format(no))
    return not 0 in status
