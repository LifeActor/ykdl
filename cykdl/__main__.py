#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import sys
import os
try:
    import ykdl
except(ImportError):
    _base_len = len('cykdl/__main__.py')
    _filepath = os.path.abspath(sys.argv[0])[:-_base_len]
    sys.path[0] = _filepath
    import ykdl

from argparse import ArgumentParser
import socket
import ssl
import json
import types
import ast
from urllib.request import ProxyHandler, HTTPSHandler, getproxies
from urllib.parse import urlparse

import logging
logger = logging.getLogger("YKDL")

from ykdl.common import url_to_module
from ykdl.util.html import add_default_handler, install_default_handlers
from ykdl.util.wrap import launch_player, launch_ffmpeg, launch_ffmpeg_download
from ykdl.util.m3u8_wrap import load_m3u8
from ykdl.util.download import save_urls
from ykdl.version import __version__

m3u8_internal = True
args = None

def arg_parser():
    parser = ArgumentParser(description="YouKuDownLoader(ykdl {}), a video downloader. Forked from you-get 0.3.34@soimort".format(__version__))
    parser.add_argument('-l', '--playlist', action='store_true', default=False, help="Download as a playlist")
    parser.add_argument('-i', '--info', action='store_true', default=False, help="Display the information of videos without downloading")
    parser.add_argument('-J', '--json', action='store_true', default=False, help="Display info in json format")
    parser.add_argument('-F', '--format',  help="Video format code, or resolution level 0, 1, ...")
    parser.add_argument('-o', '--output-dir', default='.', help="Set the output directory for downloaded videos")
    parser.add_argument('-O', '--output-name', default='', help="Downloaded videos with the NAME you want")
    parser.add_argument('-p', '--player', help="Directly play the video with PLAYER like mpv")
    parser.add_argument('-k', '--insecure', action='store_true', default=False, help="Allow insecure server connections when using SSL")
    parser.add_argument('-c', '--append-certs', type=str, nargs='+', metavar='CERTS', help="Append additional certs, used to verify SSL handshak, note that video urls can't follow this argument")
    parser.add_argument('--proxy', type=str, default='system', metavar='[SCHEME://]HOST:PORT | system | none', help="Set proxy for http(s) transfer. default: use system proxy settings")
    parser.add_argument('-t', '--timeout', type=int, default=60, metavar='SECONDS', help="Set socket timeout, default 60s")
    parser.add_argument('--fail-retry-eta', type=int, default=3600, metavar='SECONDS', help="If the number is bigger than ETA, a fail downloading will be auto retry, default 3600s, set 0 to void it")
    parser.add_argument('--no-fail-confirm', action='store_true', default=False, help="Do not wait confirm when downloading failed, for run as tasks (non-blocking)")
    parser.add_argument('--no-merge', action='store_true', default=False, help="Do not merge video slides")
    parser.add_argument('--no-sub', action='store_true', default=False, help='Do not download subtitles')
    parser.add_argument('-s', '--start', type=int, default=0, metavar='INDEX_NUM', help="Start from INDEX to play/download playlist")
    parser.add_argument('-j', '--jobs', type=int, default=8, metavar='NUM', help="Number of jobs for multiprocess download")
    parser.add_argument('--debug', default=False, action='store_true', help="Print debug messages from ykdl")
    parser.add_argument('video_urls', type=str, nargs='+', help="video urls")
    global args
    args = parser.parse_args()

def clean_slices(name, ext, lenth):
    for i in range(lenth):
        file_name = '%s_%d.%s' % (name, i, ext)
        os.remove(file_name)

def download(urls, name, ext, live=False):
    # ffmpeg can't handle local m3u8.
    # only use ffmpeg to hanle m3u8.
    global m3u8_internal
    # for live video, always use ffmpeg to rebuild timeline.
    if live:
        m3u8_internal = False
    # rebuild m3u8 urls when use internal downloader,
    # change the ext to segment's ext, default is "ts",
    # otherwise change the ext to "mp4".
    if ext == 'm3u8':
        if m3u8_internal:
            urls = load_m3u8(urls[0])
            ext = urlparse(urls[0])[2].split('.')[-1]
            if ext not in ['ts', 'm4s', 'mp4']:
                ext = 'ts'
        else:
            ext = 'mp4'

    # OK check m3u8_internal
    if not m3u8_internal:
        launch_ffmpeg_download(urls[0], name + '.' + ext)
    else:
        if save_urls(urls, name, ext, jobs=args.jobs,
                     fail_confirm=not args.no_fail_confirm,
                     fail_retry_eta=args.fail_retry_eta):
            lenth = len(urls)
            if lenth > 1 and not args.no_merge:
                launch_ffmpeg(name, ext, lenth)
                clean_slices(name, ext, lenth)
        else:
            logger.critical("{}> donwload failed".format(name))

def download_subtitles(subtitles, name):
    for sub in subtitles:
        _name = name + '_' + sub['lang']
        if not save_urls([sub['src']], _name, sub['format'],
                         fail_confirm=not args.no_fail_confirm,
                         fail_retry_eta=args.fail_retry_eta):
            logger.critical('{}> donwload failed'.format(_name))

def handle_videoinfo(info, index=0):
    i = args.format or '0'
    if i.isdigit():
        i = int(i)
        if i > len(info.stream_types):
             i =  len(info.stream_types) -1
        stream_id = info.stream_types[i]
    else:
        if not i in info.stream_types:
            stream_id = info.stream_types[0]
        else:
            stream_id = i
    if not args.json:
        info.print_info(stream_id, args.info)
    else:
        print(json.dumps(info.jsonlize(), indent=4, sort_keys=True, ensure_ascii=False))
    if args.info or args.json:
        return
    urls = info.streams[stream_id]['src']
    name = args.output_name
    if name:
        if '\\u' in name:
            name = ast.literal_eval('"{}"'.format(name))
        if args.playlist:
            name = name + '_' + str(index)
    else:
        name = info.build_file_name(stream_id)

    ext = info.streams[stream_id]['container']
    live = info.live
    if args.player:
        player_args = info.extra
        if player_args['rangefetch']:
            player_args['rangefetch']['down_rate'] = player_args['rangefetch']['video_rate'][stream_id]
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

def main():
    arg_parser()
    if not args.debug:
        logging.root.setLevel(logging.WARNING)
    else:
        logging.root.setLevel(logging.DEBUG)

    if args.timeout:
        socket.setdefaulttimeout(args.timeout)

    if args.insecure:
        ssl._create_default_https_context = ssl._create_unverified_context
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
                if os.path.exists(cert):
                    context.load_verify_locations(cert)
            https_handler = HTTPSHandler(context=context)
            add_default_handler(https_handler)

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

    add_default_handler(proxy_handler)
    install_default_handlers()

    #mkdir and cd to output dir
    if not args.output_dir == '.':
        try:
            if not os.path.exists(args.output_dir):
                os.makedirs(args.output_dir)
        except:
            logger.warning("No permission or Not found " + args.output_dir)
            logger.warning("use current folder")
            args.output_dir = '.'
    if os.path.exists(args.output_dir):
        os.chdir(args.output_dir)

    exit = 0
    try:
        for url in args.video_urls:
            try:
                m, u = url_to_module(url)
                if args.playlist:
                    parser = m.parser_list
                else:
                    parser = m.parser
                info = parser(u)
                if type(info) is types.GeneratorType or type(info) is list:
                    ind = 0
                    for i in info:
                        if ind < args.start:
                            ind += 1
                            continue
                        handle_videoinfo(i, index=ind)
                        ind += 1
                else:
                    handle_videoinfo(info)
            except AssertionError as e:
                logger.critical(str(e))
                exit = 1
            except (RuntimeError, NotImplementedError, SyntaxError) as e:
                logger.error(str(e))
                exit = 1
    except KeyboardInterrupt:
        logger.info('Interrupted by Ctrl-C')
    except Exception as e:
        errmsg = str(e)
        logger.debug(errmsg, exc_info=True)
        if 'local issuer' in errmsg:
            logger.warning('Please install or update Certifi, and try again:\n'
                           'pip3 install certifi --upgrade')
        exit = 1
    sys.exit(exit)

if __name__ == '__main__':
    main()
