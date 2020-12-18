#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import os
import sys
import threading
from logging import getLogger
from shutil import get_terminal_size
from ykdl.compact import Request, urlopen
from ykdl.util import log
from .html import fake_headers

logger = getLogger('downloader')

try:
    from concurrent.futures import ThreadPoolExecutor
    MultiThread = True
except:
    MultiThread = False
    logger.warning('failed to import ThreadPoolExecutor!')
    logger.warning('multithread download disabled!')
    logger.warning('please install concurrent.futures from https://github.com/agronholm/pythonfutures !')

processes = {}
print_lock = threading.Lock()
_max_columns = get_terminal_size().columns - 1
_clear_enter = '\r' + ' ' * _max_columns + '\r'

def print_processes():
    with print_lock:
        sys.stdout.write(_clear_enter)
        Processes = 'Processes: ' + ' '.join(['P%d-%s' % p for p in processes.items()])
        if len(Processes) > _max_columns:
            Processes = Processes[:_max_columns - 3] + '...'
        sys.stdout.write(Processes)
        sys.stdout.flush()

def simple_hook(arg1, arg2, arg3):
    if arg2 > 0:
        percent = min(int(arg1 * 100 / arg2), 100)
        processes[arg3] = '%d%%' % percent
    else:
        processes[arg3] = '%sMB' % round(arg1 / 1048576, 1)
    print_processes()
    if percent == 100:
        processes.pop(arg3, None)

def _save_url(url, name, ext, status, part=None, reporthook=simple_hook):

    def Print(*args, **kwargs):
        with print_lock:
            sys.stdout.write(_clear_enter)
            print(*args, **kwargs)
        print_processes()

    if part is None:
        print('Download: ' + name)
        name = name + '.' + ext
        part = 0
    else:
        Print('Download: %s part %d' % (name, part))
        name = '%s_%d.%s' % (name, part, ext)
    bs = 1024 * 8
    size = -1
    filesize = 0
    blocknum = 0
    open_mode = 'wb'
    response = None
    req = Request(url, headers=fake_headers)
    try:
        if os.path.exists(name):
            filesize = os.path.getsize(name)
            if filesize:
                req.add_header('Range', 'bytes=%d-' % (filesize-1))  # get +1, avoid 416
                response = urlopen(req, None)
                if response.status == 206:
                    size = int(response.headers['Content-Range'].split('/')[-1])
                    needless_size = 1
                elif response.status == 200:
                    size = int(response.headers.get('Content-Length', -1))
                    needless_size = filesize
                if filesize == size:
                    Print('Skipped: file part %d has already been downloaded' % part)
                    status[part] = 1
                    return True
                if filesize < size:
                    percent = int(filesize * 100 / size)
                    open_mode = 'ab'
                    Print('Restored: file part %d is incomplete at %d%%' % (part, percent))
                    reporthook(filesize, size, part)
                    response.read(needless_size)
        if response is None:
            response = urlopen(req, None)
        if size < 0:
            size = int(response.headers.get('Content-Length', -1))
        reporthook(filesize, size, part)
        with open(name, open_mode) as tfp:
            while True:
                block = response.read(bs)
                if not block:
                    break
                filesize += len(block)
                tfp.write(block)
                reporthook(filesize, size, part)
        if os.path.exists(name):
            filesize = os.path.getsize(name)
            if size < 0 or filesize == size:
                status[part] = 1
                return True
    finally:
        processes.pop(part, None)

def save_url(*args, **kwargs):
    '''There are two retries for every failed downloading'''
    for _ in range(3):
        if _save_url(*args, **kwargs):
            break

def save_urls(urls, name, ext, jobs=1, fail_confirm=True):

    def run(*args):
        fn, *args = args
        for no, url in enumerate(urls):
            if status[no] == 1:
                continue
            fn(*args, url, name, ext, status, part=no)

    count = len(urls)
    status = [0] * count
    while True:
        if count == 1:
            save_url(urls[0], name, ext, status)
        elif jobs > 1 and MultiThread:
            with ThreadPoolExecutor(max_workers=jobs) as worker:
                run(worker.submit, save_url)
        else:
            run(_save_url)
        print()
        succeed = 0 not in status
        if not succeed:
            if count == 1:
                logger.error('donwload failed')
            else:
                for no, s in enumerate(status):
                    if s == 0:
                        logger.error('downloader failed at part %d' % no)
        if not fail_confirm or succeed or \
                input('Do you want to continue downloading? [Y] ').upper() != 'Y':
            break
    return succeed
