#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import os
import sys
import time
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
_last_refresh = 0

def print_processes(force_refresh=True):
    if not force_refresh:
        global _last_refresh
        ct = time.monotonic()
        if ct - _last_refresh > 0.1:
            _last_refresh = ct
        else:
            return
    with print_lock:
        sys.stdout.write(_clear_enter)
        Processes = _Processes + ' '.join(['P%d-%s' % p for p in processes.items()])
        if len(Processes) > _max_columns:
            Processes = Processes[:_max_columns - 3] + '...'
        sys.stdout.write(Processes)
        sys.stdout.flush()

def simple_hook(size, total, part, action=['default']):
    action, *action_args = action
    force_refresh = True
    if action == 'default':
        if size is None:
            processes[part] ='n/a'
        elif total > 0:
            percent = min(int(size * 100 / total), 100)
            processes[part] = '%d%%' % percent
            force_refresh = percent == 100
        else:
            processes[part] = '%sMB' % round(size / 1048576, 1)
            force_refresh = False
    elif action == 'print':
        args, kwargs = action_args
        with print_lock:
            sys.stdout.write(_clear_enter)
            print(*args, **kwargs)
    elif action == 'over':
        global _Processes
        status, = action_args
        _Processes = 'Processes[%d/%d]: ' % (sum(status), len(status))
        processes.pop(part, None)
    print_processes(force_refresh)

def _save_url(url, name, ext, status, part=None, reporthook=simple_hook):

    def print(*args, **kwargs):
        reporthook(None, None, None, ['print', args, kwargs])

    if part is None:
        name = name + '.' + ext
        part = 0
    else:
        name = '%s_%d.%s' % (name, part, ext)
    bs = 1024 * 8
    size = -1
    filesize = 0
    open_mode = 'wb'
    response = None
    req = Request(url, headers=fake_headers)
    try:
        reporthook(None, None, part)
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
                    print('Skipped: file part %d has already been downloaded' % part)
                    status[part] = 1
                    return True
                if filesize < size:
                    percent = int(filesize * 100 / size)
                    open_mode = 'ab'
                    print('Restored: file part %d is incomplete at %d%%' % (part, percent))
                    reporthook(filesize, size, part)
                    while needless_size > bs:
                        block = response.read(bs)
                        if not block:
                            return
                        needless_size -= len(block)
                    response.read(needless_size)
        if response is None:
            response = urlopen(req, None)
        if size < 0:
            size = int(response.headers.get('Content-Length', -1))
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
            if filesize and (size < 0 or filesize == size):
                status[part] = 1
                return True
    finally:
        time.sleep(1)
        reporthook(None, None, part, ['over', status])

def save_url(*args, tries=3, **kwargs):
    '''There are two retries for every failed downloading'''
    while tries:
        tries -= 1
        try:
            if _save_url(*args, **kwargs):
                break
        except IOError as e:
            if not tries or getattr(e, 'code', 0) >= 400:
                raise e

def save_urls(urls, name, ext, jobs=1, fail_confirm=True):

    def run(*args, **kwargs):
        fn, *args = args
        for no, url in enumerate(urls):
            if status[no] == 1:
                continue
            fn(*args, url, name, ext, status, part=no, **kwargs)
            time.sleep(0.1)

    global _Processes
    count = len(urls)
    _Processes = 'Processes[0/%d]: ' % count
    status = [0] * count
    tries = 1
    if count > 1 and jobs == 1 or not MultiThread:
        tries = 3
    print('Start downloading: ' + name)
    while tries:
        tries -= 1
        if count == 1:
            save_url(urls[0], name, ext, status)
        elif jobs > 1 and MultiThread:
            if count >= jobs > 12:
                logger.warning('number of active download processes is too big to works well!!')
            with ThreadPoolExecutor(max_workers=jobs) as worker:
                run(worker.submit, save_url)
        else:
            run(save_url, tries=1)
        print()
        succeed = 0 not in status
        if not succeed:
            if count == 1:
                logger.error('donwload failed')
            else:
                logger.error('download failed at parts: ' + 
                        ', '.join([str(no) for no, s in enumerate(status) if s == 0]))
        if not tries or not fail_confirm or succeed or \
                input('Do you want to continue downloading? [Y] ').upper() != 'Y':
            break
        if not tries:
            tries += 1
        print('Restart downloading: ' + name)
    return succeed
