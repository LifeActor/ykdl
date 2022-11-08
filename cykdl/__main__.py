#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
try:
    import ykdl
except ImportError:
    sys.path.insert(0, os.path.abspath(__file__ + '/../..'))
    import ykdl

from argparse import ArgumentParser
import socket
import ssl
import json
import ast
from urllib.request import ProxyHandler, HTTPSHandler, getproxies
from urllib.parse import urlsplit
from tempfile import NamedTemporaryFile
from types import GeneratorType

import logging
logger = logging.getLogger('YKDL')

from ykdl.common import url_to_module
from ykdl.util import http, log
from ykdl.util.external import launch_player, launch_ffmpeg_merge, launch_ffmpeg_download
from ykdl.util.m3u8 import live_m3u8, crypto_m3u8, load_m3u8, _load as _load_m3u8
from ykdl.util.download import save_urls
from ykdl.util.wrap import literalize
from ykdl.version import __version__

m3u8_internal = True
args = None
description = 'YouKuDownLoader(YKDL {}), a video downloader forked from you-get 0.3.34@soimort'.format(__version__)

def parse_args(argv=None):
    parser = ArgumentParser(description=description)
    parser.add_argument('-l', '--playlist', action='store_true', default=False, help='Download as a playlist')
    parser.add_argument('-i', '--info', action='store_true', default=False, help='Display the information of videos without downloading')
    parser.add_argument('-J', '--json', action='store_true', default=False, help='Display info in json format')
    parser.add_argument('-a', '--show-all', action='store_true', default=False, help='Display all available video format before downloading')
    parser.add_argument('-F', '--format',  help='Video format code, or resolution level 0, 1, ...')
    parser.add_argument('-o', '--output-dir', default='.', help='Set the output directory for downloaded videos')
    parser.add_argument('-O', '--output-name', default='', help='Downloaded videos with the NAME you want')
    parser.add_argument('-p', '--player', help='Directly play the video with PLAYER like mpv')
    parser.add_argument('-k', '--insecure', action='store_true', default=False, help='Allow insecure server connections when using SSL')
    parser.add_argument('-c', '--append-certs', type=str, nargs='+', metavar='CERTS', help="Append additional certs, used to verify SSL handshak, note that video urls can't follow this argument")
    parser.add_argument('--proxy', type=str, default='system', metavar='[SCHEME://]HOST:PORT | system | none', help='Set proxy for http(s) transfer. default: use system proxy settings')
    parser.add_argument('-t', '--timeout', type=int, default=60, metavar='SECONDS', help='Set socket timeout, default 60s')
    parser.add_argument('--fail-retry-eta', type=int, default=3600, metavar='SECONDS', help='If the number is bigger than ETA, a fail downloading will be auto retry, default 3600s, set 0 to void it')
    parser.add_argument('--no-fail-confirm', action='store_true', default=False, help='Do not wait confirm when downloading failed, for run as tasks (non-blocking)')
    parser.add_argument('--no-merge', action='store_true', default=False, help='Do not merge video slides')
    parser.add_argument('--no-sub', action='store_true', default=False, help='Do not download subtitles')
    parser.add_argument('--no-http-cache', action='store_true', default=False, help='Do not allow HTTP cache')
    parser.add_argument('-s', '--start', type=int, default=-1, metavar='INDEX_NUM', help='Start from INDEX to play/download playlist, default -1, index at media of current URL')
    parser.add_argument('-j', '--jobs', type=int, default=8, metavar='NUM', help='Number of jobs for multiprocess download')
    parser.add_argument('--debug', action='store_true', default=False, help='Print debug messages from ykdl')
    parser.add_argument('video_urls', type=str, nargs='*', help='video urls, leave empty then enter interactive mode')
    global args
    args = parser.parse_args(argv)
    if args.start > 0:
        args.start -= 1

def clean_slices(name, ext, lenth):
    for i in range(lenth):
        file_name = '%s_%d.%s' % (name, i, ext)
        os.remove(file_name)

def fix_sa_name(name, ext, lenth):
    if lenth > 1:
        return
    fn1 = '%s.%s' % (name, ext)
    fn2 = '%s_0.%s' % (name, ext)
    os.rename(fn1, fn2)

def download(urls, name, ext, live=False):
    url = urls[0]
    m3u8 = ext == 'm3u8'
    m3u8_crypto = False
    audio = subtitle = None
    # for live video, always use ffmpeg to rebuild timeline.
    if not live and m3u8:
        live = live_m3u8(url)
    internal = not live and m3u8_internal
    if m3u8:
        m3u8_crypto = crypto_m3u8(url)
        # rebuild m3u8 urls when use internal downloader,
        # change the ext to segment's ext, default is "ts",
        # otherwise change the ext to "flv" or "mp4".
        if internal:
            urls, audio, subtitle = load_m3u8(url)
            ext = urlsplit(urls[0]).path.split('.')[-1]
            if ext not in ['ts', 'm4s', 'mp4', 'm4a']:
                ext = 'ts'
        elif live:
            ext = 'flv'
        else:
            ext = 'mp4'
    elif ext == 'mpd':
        # very slow
        # and now, it has many problems
        # TODO: implement internal download/merge process
        internal = False
        ext = 'mp4'

    # OK check internal
    if not internal:
        launch_ffmpeg_download(url, name + '.' + ext, allow_all_ext=m3u8_crypto)
    else:
        if save_urls(urls, name, ext, jobs=args.jobs,
                     fail_confirm=not args.no_fail_confirm,
                     fail_retry_eta=args.fail_retry_eta):
            lenth = len(urls)
            if (m3u8 or lenth > 1) and not args.no_merge:
                fix_sa_name(name, ext, lenth)
                if m3u8_crypto:
                    # use ffmpeg to merge internal downloaded m3u8
                    # build the local m3u8, and then the headers cannot be set
                    lm3u8 = NamedTemporaryFile(mode='w+t', suffix='.m3u8',
                                               dir='.', encoding='utf-8')
                    lkeys = []  # temp keys' references
                    m = _load_m3u8(url)
                    for k in m.keys + m.session_keys:
                        if k and k.uri:
                            key = NamedTemporaryFile(mode='w+b', suffix='.key',
                                                     dir='.')
                            key.write(http.get_response(k.absolute_uri).content)
                            key.flush()
                            k.uri = os.path.basename(key.name)
                            lkeys.append(key)
                    for i, seg in enumerate(m.segments):
                        seg.uri = '%s_%d.%s' % (name, i, ext)
                    lm3u8.write(m.dumps())
                    lm3u8.flush()
                    launch_ffmpeg_download(lm3u8.name, name + '.mp4', False, True)
                else:
                    launch_ffmpeg_merge(name, ext, lenth)
                clean_slices(name, ext, lenth)
        else:
            logger.critical('{}> donwload failed'.format(name))
        if audio:
            ext = 'm4a'
            lenth = len(audio)
            if save_urls(audio, name, ext, jobs=args.jobs,
                         fail_confirm=not args.no_fail_confirm,
                         fail_retry_eta=args.fail_retry_eta):
                if (m3u8 or lenth > 1) and not args.no_merge:
                    fix_sa_name(name, ext, lenth)
                    launch_ffmpeg_merge(name, ext, lenth)
                    clean_slices(name, ext, lenth)
            else:
                logger.critical('{}> HLS audio donwload failed'.format(name))
        if subtitle:
            ext = 'srt'
            if not save_urls(subtitle[:1], name, ext, jobs=args.jobs,
                         fail_confirm=not args.no_fail_confirm,
                         fail_retry_eta=args.fail_retry_eta):
                logger.critical('{}> HLS subtitle donwload failed'.format(name))

def download_subtitles(subtitles, name):
    for sub in subtitles:
        _name = name + '_' + sub['lang']
        if not save_urls([sub['src']], _name, sub['format'],
                         fail_confirm=not args.no_fail_confirm,
                         fail_retry_eta=args.fail_retry_eta):
            logger.critical('{}> donwload failed'.format(_name))

def handle_videoinfo(info):
    i = args.format or '0'
    if i.isdecimal():
        i = int(i)
        if i > len(info.streams) -1:
             i = -1
    else:
        i = info.streams.index(i)
    stream_id = info.streams.get_id(i)
    if args.json:
        print(json.dumps(info.jsonlize(), indent=4, sort_keys=True, ensure_ascii=False))
    else:
        info.print_info(stream_id, args.show_all, args.info)
        if args.show_all:
            action = args.player and 'playing' or 'downloading'
            print('Now %s format ' % action
                  + log.sprint(stream_id, log.NEGATIVE))
    if args.info or args.json:
        return
    urls = info.streams[stream_id]['src']
    name = args.output_name
    if name:
        if '\\u' in name:
            name = literalize(name)
        if info.index is not None:
            name = name + '_' + str(info.index[0])
    else:
        name = info.build_file_name(stream_id)

    ext = info.streams[stream_id]['container']
    live = info.live
    if args.player:
        player_args = info.extra
        if player_args['rangefetch']:
            player_args['rangefetch']['down_rate'] = player_args['rangefetch']['video_rate'].get(stream_id)
            player_args['rangefetch']['ca_certs'] = args.certs
        if args.proxy != 'none':
            player_args['proxy'] = args.proxy
            if player_args['rangefetch']:
                player_args['rangefetch']['proxy'] = args.proxy
        player_args['title'] = info.title
        player_args['subs'] = args.no_sub or [sub['src'] for sub in info.subtitles]
        launch_player(args.player, urls, ext, **player_args)
    else:
        download(urls, name, ext, live)
        if not args.no_sub:
            download_subtitles(info.subtitles, name)

def handle_video(video):
    http.reset_headers()
    http.uninstall_cookie()
    try:
        m, u = url_to_module(video)
        if args.playlist:
            parser = m.parser_list
            m.start = args.start
        else:
            parser = m.parser
        info = parser(u)
        if isinstance(info, (GeneratorType, list)):
            for i in info:
                handle_videoinfo(i)
        else:
            handle_videoinfo(info)
    except AssertionError as e:
        logger.critical(str(e))
        return 1
    except (RuntimeError, NotImplementedError, SyntaxError) as e:
        logger.error(repr(e))
        return 1
    return 0

def main(argv=None):
    parse_args(argv)
    if not args.debug:
        logging.root.setLevel(logging.INFO)
    else:
        logging.root.setLevel(logging.DEBUG)

    if args.timeout:
        socket.setdefaulttimeout(args.timeout)

    if args.insecure:
        ssl._create_default_https_context = ssl._create_unverified_context
        args.certs = ssl.CERT_NONE
    else:
        certs = args.append_certs or []
        try:
            import certifi
        except ImportError:
            pass
        else:
            certs.append(certifi.where())
        if certs:
            context = ssl._create_default_https_context()
            for cert in certs:
                if os.path.isfile(cert):
                    context.load_verify_locations(cert)
                elif os.path.isdir(cert):
                    context.load_verify_locations(capath=cert)
            https_handler = HTTPSHandler(context=context)
            http.add_default_handler(https_handler)
            args.certs = certs
        else:
            args.certs = None

    proxies = None
    if args.proxy == 'system':
        proxies = getproxies()
        args.proxy = proxies.get('http') or proxies.get('https', 'none')
    args.proxy = args.proxy.lower()
    if not args.proxy.startswith(('http', 'socks', 'none')):
        args.proxy = 'http://' + args.proxy

    if args.proxy == 'none':
        proxies = {}
    elif args.proxy.startswith(('http', 'socks')):
        if args.proxy.startswith(('https', 'socks')):
            try:
                import extproxy
            except ImportError:
                logger.error('Please install ExtProxy to use proxy: ' + args.proxy)
                raise
        proxies = {
            'http': args.proxy,
            'https': args.proxy
        }
    proxy_handler = ProxyHandler(proxies)

    http.add_default_handler(proxy_handler)

    if args.no_http_cache:
        http.CACHED.set(0)

    #mkdir and cd to output dir
    if not args.output_dir == '.':
        try:
            if not os.path.exists(args.output_dir):
                os.makedirs(args.output_dir)
        except:
            logger.warning('No permission or Not found ' + args.output_dir)
            logger.warning('use current folder')
            args.output_dir = '.'
    if os.path.exists(args.output_dir):
        os.chdir(args.output_dir)

    if args.video_urls:
        exit = 0
        try:
            for rc in map(handle_video, args.video_urls):
                exit = exit or rc
        except KeyboardInterrupt:
            logger.info('Interrupted by Ctrl-C')
            exit = 0
        except Exception as e:
            errmsg = str(e)
            logger.debug(errmsg, exc_info=True)
            if 'local issuer' in errmsg:
                logger.warning('Please install or update Certifi, and try again:\n'
                               'pip3 install certifi --upgrade')
            exit = 255
        finally:
            sys.exit(exit)

    print('Welcome to use', description)
    print('Start interactive mode, now support an URL as input.')
    print('Input "exit" or press Ctrl-C to exit.')
    while True:
        try:
            video = input('YKDL> ').strip()
        except KeyboardInterrupt:
             sys.exit()
        if not video:
            continue
        cmd = video.strip().lower()
        if cmd == 'cache clear':
            http.cache_clear()
            continue
        if cmd == 'exit':
            sys.exit()
        try:
            handle_video(video)
        except KeyboardInterrupt:
            logger.warning('\nInterrupted by Ctrl-C, press Ctrl-C again to exit YKDL.')
        except Exception as e:
            errmsg = str(e)
            logger.debug(errmsg, exc_info=True)
            if 'local issuer' in errmsg:
                logger.warning('Please install or update Certifi, and try again:\n'
                               'pip3 install certifi --upgrade')

if __name__ == '__main__':
    main()
