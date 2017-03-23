#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
import json
import types
from multiprocessing import cpu_count

from ykdl.common import url_to_module
from ykdl.compact import ProxyHandler, build_opener, install_opener, compact_str
from ykdl.util import log
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
    parser.add_argument('-F', '--format',  help="Video format code.")
    parser.add_argument('-o', '--output-dir', default='.', help="Set the output directory for downloaded videos.")
    parser.add_argument('-O', '--output-name', default='', help="downloaded videos with the NAME you want, don't use with -l")
    parser.add_argument('-p', '--player', help="Directly play the video with PLAYER like mpv")
    parser.add_argument('--proxy', type=str, default='system', help="set proxy HOST:PORT for http(s) transfer. default: use system proxy settings")
    parser.add_argument('-t', '--timeout', type=int, default=60, help="set socket timeout seconds, default 60s")
    parser.add_argument('--no-merge', action='store_true', default=False, help="do not merge video slides")
    parser.add_argument('-s', '--start', type=int, default=0, help="start from INDEX to play/download playlist")
    parser.add_argument('-j', '--jobs', type=int, default=cpu_count(), help="number of jobs for multiprocess download")
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
    if not urls[0].startswith('http') or not ext == 'm3u8':
        m3u8_internal = True
    # for live video, always use ffmpeg to rebuild timeline.
    if live:
        m3u8_internal = False
    # change m3u8 ext to mp4
    # rebuild urls when use internal downloader
    if ext == 'm3u8':
        ext = 'mp4'
        if m3u8_internal:
            urls = load_m3u8(urls[0])

    # OK check m3u8_internal
    if not m3u8_internal:
        launch_ffmpeg_download(urls[0], name + '.' + ext, live)
    else:
        save_urls(urls, name, ext, jobs = args.jobs)
        lenth = len(urls)
        if lenth > 1 and not args.no_merge:
            ret = launch_ffmpeg(name, ext,lenth)
            if not ret:
                clean_slices(name, ext,lenth)

def handle_videoinfo(info, index=0):
    if not args.json:
        info.print_info(args.format, args.info)
    else:
        print(json.dumps(info.jsonlize(), indent=4, sort_keys=True, ensure_ascii=False))
    if args.info or args.json:
        return
    stream_id = args.format or info.stream_types[0]
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
    if args.player:
        launch_player(args.player, urls)
    else:
        download(urls, name, ext, live)

def main():
    arg_parser()
    if args.timeout:
        socket.setdefaulttimeout(args.timeout)
    if args.proxy == 'system':
        proxy_handler = ProxyHandler()
    else:
        proxy_handler = ProxyHandler({
            'http': args.proxy,
            'https': args.proxy
        })
    opener = build_opener(proxy_handler)
    install_opener(opener)

    #mkdir and cd to output dir
    if not args.output_dir == '.':
        try:
            if not os.path.exists(args.output_dir):
                os.makedirs(args.output_dir)
        except:
            log.w("No permission or Not found " + args.output_dir)
            log.w("use current folder")
            args.output_dir = '.'
    if os.path.exists(args.output_dir):
        os.chdir(args.output_dir)

    try:
        exit = 0
        for url in args.video_urls:
            try:
                m,u = url_to_module(url)
                if args.playlist:
                    parser = m.parser_list
                else:
                    parser = m.parser
                info = parser(u)
                if type(info) is types.GeneratorType or type(info) is list:
                    ind = 0
                    for i in info:
                        if ind < args.start:
                            ind+=1
                            continue
                        handle_videoinfo(i, index=ind)
                        ind+=1
                else:
                    handle_videoinfo(info)
            except AssertionError as e:
                log.wtf(compact_str(e))
                exit = 1
            except (RuntimeError, NotImplementedError, SyntaxError) as e:
                log.e(compact_str(e))
                exit = 1
        sys.exit(exit)
    except KeyboardInterrupt:
        print('\nInterrupted by Ctrl-C')

if __name__ == '__main__':
    main()
