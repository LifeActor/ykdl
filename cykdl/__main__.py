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
from multiprocessing import cpu_count

import logging
logger = logging.getLogger("YKDL")

from ykdl.common import url_to_module
from ykdl.compact import ProxyHandler, compact_str, urlparse, getproxies
from ykdl.util.html import add_default_handler, install_default_handlers
from ykdl.util.wrap import launch_player, launch_ffmpeg, launch_ffmpeg_download
from ykdl.util.m3u8_wrap import load_m3u8
from ykdl.util.download import save_urls
from ykdl.version import __version__

m3u8_internal = True
args = None

def arg_parser():
    parser = ArgumentParser(description="YouKuDownLoader(ykdl {}), a video downloader. Forked form you-get 0.3.34@soimort".format(__version__))
    parser.add_argument('-l', '--playlist', action='store_true', default=False, help="Download as a playlist.")
    parser.add_argument('-i', '--info', action='store_true', default=False, help="Display the information of videos without downloading.")
    parser.add_argument('-J', '--json', action='store_true', default=False, help="Display info in json format.")
    parser.add_argument('-F', '--format',  help="Video format code, or resolution level 0, 1, ...")
    parser.add_argument('-o', '--output-dir', default='.', help="Set the output directory for downloaded videos.")
    parser.add_argument('-O', '--output-name', default='', help="downloaded videos with the NAME you want")
    parser.add_argument('-p', '--player', help="Directly play the video with PLAYER like mpv")
    parser.add_argument('-k', '--insecure', action='store_true', default=False, help="Allow insecure server connections when using SSL.")
    parser.add_argument('--proxy', type=str, default='system', help="set proxy HOST:PORT for http(s) transfer. default: use system proxy settings")
    parser.add_argument('-t', '--timeout', type=int, default=60, help="set socket timeout seconds, default 60s")
    parser.add_argument('--no-merge', action='store_true', default=False, help="do not merge video slides")
    parser.add_argument('-s', '--start', type=int, default=0, help="start from INDEX to play/download playlist")
    parser.add_argument('-j', '--jobs', type=int, default=cpu_count(), help="number of jobs for multiprocess download")
    parser.add_argument('--debug', default=False, action='store_true', help="print debug messages from ykdl")
    parser.add_argument('video_urls', type=str, nargs='+', help="video urls")
    global args
    args = parser.parse_args()

def clean_slices(name, ext, lenth):
    for i in range(lenth):
        file_name = name + '_%d_.' % i + ext
        os.remove(file_name)

def download(urls, name, ext, live = False):
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
        launch_ffmpeg_download(urls[0], name + '.' + ext, live)
    else:
        if save_urls(urls, name, ext, jobs = args.jobs):
            lenth = len(urls)
            if lenth > 1 and not args.no_merge:
                launch_ffmpeg(name, ext,lenth)
                clean_slices(name, ext,lenth)
        else:
            logger.critical("{}> donwload failed".format(name))

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
    if args.output_name:
        if args.playlist:
            name = args.output_name + '_' + str(index)
        else:
            name = args.output_name
    else:
        name = info.build_file_name(stream_id)

    ext = info.streams[stream_id]['container']
    live = info.live
    if info.extra['rangefetch']:
        info.extra['rangefetch']['down_rate'] = info.extra['rangefetch']['video_rate'][stream_id]
    if args.proxy != 'none':
        info.extra['proxy'] = args.proxy
        if info.extra['rangefetch']:
            info.extra['rangefetch']['proxy'] = args.proxy
    player_args = info.extra
    player_args['title'] = info.title
    if args.player:
        launch_player(args.player, urls, ext, **player_args)
    else:
        download(urls, name, ext, live)

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

    try:
        exit = 0
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
                logger.critical(compact_str(e))
                exit = 1
            except (RuntimeError, NotImplementedError, SyntaxError) as e:
                logger.error(compact_str(e))
                exit = 1
        sys.exit(exit)
    except KeyboardInterrupt:
        logger.info('Interrupted by Ctrl-C')

if __name__ == '__main__':
    main()
