'''Processes/progress report hook arguments and report order:

  reporthook(action, size=None, total=None, part=None)

    0. download init         (['init'])

      1. download start      (['start', single, status])

        2. part start        (['part'], part=part)

          3. part restore    (['part', last_incomplete])

          4. part progress   (['part'], filesize, totalsize, part)

        5. part end          (['part end', status, downloaded], filesize, totalsize, part)

      6. download end        (['end']) => (downloaded, filessize, totalsize, costtime)
'''

import os
import sys
import time
import socket
import string
import threading
from logging import getLogger
from shutil import get_terminal_size
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import quote
from urllib.request import Request, urlopen
from http.client import IncompleteRead

from .http import hit_conn_cache, clear_conn_cache, fake_headers
from .human import *
from .log import IS_ANSI_TERMINAL
from .wrap import hash


logger = getLogger(__name__)

print_lock = threading.Lock()
_max_columns = get_terminal_size().columns - 1
_clear_enter = '\r' + ' ' * _max_columns + '\r'
_progress_bar_len = _max_columns - 50
if IS_ANSI_TERMINAL:
    _progress_bar_fg = ' '
    _progress_bar_bg = ' '
    _progress_bar_fmt = ' \33[47m%s\33[100m%s\33[0m'
else:
    _progress_bar_fg = '#'
    _progress_bar_bg = '|'
    _progress_bar_fmt = ' %s%s'
ESCAPE_CODE_LEN = len(_progress_bar_fmt) - len(' %s%s')

def print(*args, print=print, **kwargs):
    kwargs['file'] = sys.stderr
    print(*args, **kwargs)

def set_rcvbuf(response):
    try:
        response.fp.raw._sock.setsockopt(
                socket.SOL_SOCKET, socket.SO_RCVBUF, 65536)  # 64KB
    except Exception as e:
        logger.debug('error occurred during set_rcvbuf: %s', e)

def get_progress_bar(percent):
    if _progress_bar_len <= 0:
        return ''
    bar_fg = _progress_bar_fg * int(_progress_bar_len * percent / 100)
    bar_bg = _progress_bar_bg * (_progress_bar_len - len(bar_fg))
    return _progress_bar_fmt % (bar_fg, bar_bg)

def multi_hook(action, size=None, total=None, part=None):
    global _processing, _processes, _processes_single, _progress, _restored_size
    global _processes_start, _processes_last_refresh, _processes_downloaded

    def print_processes(force_refresh=True):
        global _processes_last_refresh
        if not _processing:
            return
        with print_lock:
            if not force_refresh and ct - _processes_last_refresh < 0.1:
                return
            _processes_last_refresh = ct
            sys.stderr.write(_clear_enter)
            escape_code_len = 0
            if _processes_single:
                _, total, percent = _progress
                if total > 0:
                    Processes = get_progress_bar(percent) + get_processes_suffix()
                    escape_code_len = ESCAPE_CODE_LEN
                else:
                    Processes = get_processes_suffix()
            else:
                Processes = get_processes_prefix()
                Processes += ' '.join(['P%d-%s' % p for p in _processes.items()])
            if len(Processes) - escape_code_len > _max_columns:
                Processes = Processes[:_max_columns - 3] + '...'
            sys.stderr.write(Processes)
            sys.stderr.write('\r')
            sys.stderr.flush()

    def processes_deamon():
        nonlocal ct
        while _processing:
            print_processes(False)
            time.sleep(0.8)
            ct = time.monotonic()

    def update_processes_suffix():
        global _processes_suffix
        status = action_args[0]
        _processes_suffix = f'  %s [{sum(status)}/{len(status)}] [%s/%s]'

    def get_processes_suffix():
        size, total, *_ = _progress
        cost = ct - _processes_start
        eta = 'NA'
        if total > 0:
            percent = min(size / total, 1)
            progress = f'{percent:.1%} of {human_size(total)}'
            if _restored_size:
                size -= _restored_size
                percent = size / (total - _restored_size)
            if percent > 0.01 or size > 0x100000:
                eta = human_time(cost / percent - cost)
        elif size:
            progress = human_size(size)
        else:
            progress = 'N/A'
        return _processes_suffix % (progress, human_time(cost), eta)

    def update_processes_prefix():
        global _processes_prefix
        status = action_args[0]
        _processes_prefix = f'Processes[{sum(status)}/{len(status)}][%s]: '

    def get_processes_prefix():
        return _processes_prefix % human_time(ct - _processes_start)

    ct = time.monotonic()
    action, *action_args = action
    force_refresh = True

    if action == 'part':
        if _processes_single:
            if action_args:
                _restored_size = action_args[0]
            percent = last_percent = _progress[-1]
            if size is None:
                total = -1
            elif total > 0:
                percent = min(int(size * 100 / total), 100)
            _progress = size, total, percent
            force_refresh = percent != last_percent
        else:
            if size is None:
                _processes[part] = 'N/A'
            elif total > 0:
                percent = min(size / total, 1)
                _processes[part] = f'{percent:.1%}'
                force_refresh = percent == 100
            else:
                _processes[part] = human_size(size)
                force_refresh = False

    elif action == 'part end':
        if _processes_single:
            update_processes_suffix()
        else:
            update_processes_prefix()
            _processes.pop(part, None)
        downloaded = action_args[1]
        try:
            d, s, t = _processes_downloaded[part]
            downloaded += d
            if total < 0:
                total = t
        except KeyError:
            pass
        _processes_downloaded[part] = downloaded, size, total

    elif action == 'print':
        args, kwargs = action_args
        with print_lock:
            sys.stderr.write(_clear_enter)
            print(*args, **kwargs)

    elif action == 'init':
        _processes_downloaded = {}
        return

    elif action == 'start':
        _processes_single, *action_args = action_args
        if _processes_single:
            _restored_size = 0
            _progress = (0,) * 3
            update_processes_suffix()
        else:
            _processes = {}
            update_processes_prefix()
        _processes_start = ct
        _processes_last_refresh = 0
        _processing = True
        threading._start_new_thread(processes_deamon, ())

    elif action == 'end':
        _processing = False
        downloaded, size, total = map(sum, zip(*_processes_downloaded.values()))
        _processes_downloaded.update({k: (0, v[1], v[2])
                                     for k, v in _processes_downloaded.items()})
        cost = ct - _processes_start
        return downloaded, size, total, cost

    print_processes(force_refresh)

def _save_url(url, name, ext, status, part=None, reporthook=multi_hook):

    def print(*args, **kwargs):
        reporthook(['print', args, kwargs])

    def get_response(req):
        response = urlopen(req, timeout=timeout_q)
        try:
            response.fp.raw._sock.settimeout(timeout_r)
        except Exception as e:
            logger.debug('error occurred during settimeout: %s', e)
        return response

    single = part is None
    if single:
        name = name + '.' + ext
        part = 0
    else:
        name = '%s_%d.%s' % (name, part, ext)
    bs = 8192
    size = -1
    filesize = 0
    downloaded = 0
    open_mode = 'wb'
    response = None
    timeout_q = min(socket.getdefaulttimeout() or 30, 30)
    timeout_r = max(socket.getdefaulttimeout() or 0, 60)
    url = quote(url, safe=string.punctuation)
    req = Request(url, headers=fake_headers)
    req.remove_header('Accept-encoding')
    try:
        reporthook(['part'], part=part)
        if os.path.exists(name):
            filesize = os.path.getsize(name)
            if filesize:
                needless_size = min(filesize - 1, 32)
                # get + n, avoid 416
                req.add_header('Range', 'bytes=%d-' % (filesize-needless_size))
                try:
                    response = get_response(req)
                except OSError as e:
                    if single and getattr(e, 'code', 0) == 416:
                        raise FileExistsError()
                    raise
                set_rcvbuf(response)
                if response.status == 206:
                    size = int(response.headers['Content-Range'].split('/')[-1])
                elif response.status == 200:
                    size = int(response.headers.get('Content-Length', -1))
                    needless_size = filesize
                if filesize == size:
                    print('Skipped: file part %d has already been downloaded'
                          % part)
                    status[part] = 1
                    return True
                if filesize < size:
                    while _processing and needless_size > 0:
                        if needless_size > bs:
                            block = response.read(bs)
                        else:
                            block = response.read(needless_size)
                        if not block:
                            return
                        needless_size -= len(block)
                    else:
                        if single:
                            with open(name, 'rb') as tfp:
                                tfp.seek(-len(block), 2)
                                if tfp.read() != block:
                                    raise FileExistsError()
                    open_mode = 'ab'
                    percent = filesize / size
                    reporthook(['part', response.status == 206 and filesize or 0],
                               filesize, size, part)
                    print(f'Restored: file part {part:d} is incomplete '
                          f'at {percent:.1%}')
        if response is None:
            response = get_response(req)
            set_rcvbuf(response)
        if size < 0:
            size = int(response.headers.get('Content-Length', -1))
        reporthook(['part'], filesize, size, part)
        with open(name, open_mode) as tfp:
            while _processing and (size < 0 or filesize < size):
                block = response.read(bs)
                if not block:
                    break
                n = tfp.write(block)
                downloaded += n
                filesize += n
                reporthook(['part'], filesize, size, part)
        if os.path.exists(name):
            filesize = os.path.getsize(name)
            if filesize and (size < 0 or filesize == size):
                status[part] = 1
                return True
    finally:
        time.sleep(1)
        reporthook(['part end', status, downloaded], filesize, size, part)

def save_url(url, name, *args, tries=3, **kwargs):
    '''There are two retries for every failed downloading'''
    while _processing and tries:
        tries -= 1
        try:
            if _save_url(url, name, *args, **kwargs):
                break
        except FileExistsError:
            tries += 1
            hash_suffix = hash.crc32(url.split("?", 1)[0])
            name += hash_suffix
            reporthook(['print',
                        'Renamed: the file name has existed, '
                       f'append suffix [{hash_suffix}]'])
            continue
        except OSError as e:
            if not tries or getattr(e, 'code', 0) >= 400:
                raise e
        except IncompleteRead:
            pass

def save_urls(urls, name, ext, jobs=1, fail_confirm=True,
              fail_retry_eta=3600, reporthook=multi_hook):

    if not hit_conn_cache(urls[0]):
        clear_conn_cache()  # clear useless caches

    def run(*args, **kwargs):
        fn, *args = args
        futures = []
        for no, url in enumerate(urls):
            if status[no] == 1:
                continue
            futures.append(
                fn(*args, url, name, ext, status,
                   part=no, reporthook=reporthook, **kwargs))
            time.sleep(0.1)
        futures.reverse()
        return futures

    count = len(urls)
    status = [0] * count
    cost = 0
    tries = 1
    multi = False
    exc = None
    if count > 1:
        if jobs > 1:
            multi = True
        else:
            tries = 3
    print(f'Start downloading: {name}')
    reporthook(['init'])
    while tries:
        if count > 1 and os.path.exists(f'{name}.{ext=="ts" and "mp4" or ext}'):
            print('Skipped: files has already been downloaded')
            return
        tries -= 1
        reporthook(['start', not multi, status])
        try:
            if count == 1:
                save_url(urls[0], name, ext, status, reporthook=reporthook)
            elif jobs > 1:
                if min(count - sum(status), jobs) > 12:
                    logger.warning('number of active download processes'
                                   'is too big to works well!!')
                worker = ThreadPoolExecutor(max_workers=jobs)
                futures = run(worker.submit, save_url)
                downloading = True
                while downloading:
                    time.sleep(0.1)
                    for future in futures:
                        downloading = not future.done()
                        if downloading:
                            break
            else:
                run(save_url, tries=1)
        except BaseException as e:
            global _processing
            _processing = False
            time.sleep(0.5)
            exc = e
        downloaded, size, total, _cost = reporthook(['end'])
        cost += _cost
        print()
        if cost != _cost:
            print('Current downloaded %s, cost %s'
                  % (human_size(downloaded), human_time(_cost)))
        print('Total downloaded %s of %s, cost %s'
              % (human_size(size), human_size(total), human_time(cost)))
        succeed = 0 not in status
        if not succeed:
            if count == 1:
                logger.error('donwload failed')
            else:
                logger.error('download failed with %d parts', count-sum(status))
            if not tries:
                # increase retry automatically, speed 16KBps and ETA 3600s
                speed = downloaded / _cost or 1
                eta = (total - size) / speed
                if speed > 16384 and 0 < eta < fail_retry_eta:
                    tries += 1
        if exc:
            raise exc
        if succeed or not tries and (
                not fail_confirm or
                input(f'The estimated ETA is {human_time(eta)}, '
                       'do you want to continue downloading? [Y] '
                     ).upper() != 'Y'):
            break
        if not tries:
            tries += 1
        print(f'Restart downloading: {name}')
    return succeed
