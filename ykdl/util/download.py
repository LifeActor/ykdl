#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from threading import Thread
from ykdl.compact import Request, urlopen

from .html import fake_headers


class downloadThread(Thread):
    def __init__(self, url, file_name):
        super(downloadThread, self).__init__()
        self.url = url
        self.file_name = file_name

    def run(self):
        try:
            save_url(self.url, self.file_name)
        except:
            import traceback
            traceback.print_exc()

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

def save_url(url, name, reporthook = simple_hook):
    bs = 1024*8
    size = -1
    read = 0
    blocknum = 0
    open_mode = 'wb'
    req = Request(url, headers = fake_headers)
    response = urlopen(req, None)
    if "content-length" in response.headers:
        size = int(response.headers["Content-Length"])
    if os.path.exists(name):
        filesize = os.path.getsize(name)
        if filesize == size:
            print('Skipped: file already downloaded')
            return
        elif -1 != size:
            req.add_header('Range', 'bytes=%d-' % filesize)
            blocknum = int(filesize / bs)
            response = urlopen(req, None)
            open_mode = 'ab'
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

def save_urls(urls, name, ext):
    no = 0
    downloads_pool = []
    for u in urls:
        if type(urls) is list and len(urls) == 1:
            print("Download: " + name)
            n = name + '.' + ext
        else:
            print("Download: " + name + " part %d" % no)
            n = name + '_%d_.' % no + ext
        t = downloadThread(u, n)
        downloads_pool.append(t)
        t.start()
        print("")
        no += 1
    for t in downloads_pool:
        t.join()
