#!/usr/bin/env python
# -*- coding: utf-8 -*-

from argparse import ArgumentParser
import socket
import os
import sys
import json

from ykdl.common import url_to_module
from ykdl.compact import ProxyHandler, build_opener, install_opener, compact_str
from ykdl.util import log
from ykdl.util.wrap import launch_player, launch_ffmpeg, launch_ffmpeg_download
from ykdl.util.m3u8_wrap import load_m3u8
from ykdl.util.download import save_urls
from ykdl.version import __version__

args = None

def arg_parser():
    parser = ArgumentParser(description="YouKuDownLoader(ykdl {}), a video downloader. Forked form you-get 0.3.34@soimort".format(__version__))
    parser.add_argument('-l', '--playlist', action='store_true', default=False, help="Download as a playlist.")
    parser.add_argument('-i', '--info', action='store_true', default=False, help="Display the information of videos without downloading.")
    parser.add_argument('-j', '--json', action='store_true', default=False, help="Display info in json format.")
    parser.add_argument('-m', '--merge', action='store_true', default=False, help="merge download video (experimental)")
    parser.add_argument('-F', '--format',  help="Video format code.")
    parser.add_argument('-o', '--output-dir', default='.', help="Set the output directory for downloaded videos.")
    parser.add_argument('-p', '--player', help="Directly play the video with PLAYER like mpv")
    parser.add_argument('-s', '--start', type=int, default=0, help="start from INDEX to play/download playlist")
    parser.add_argument('--proxy', type=str, default='', help="set proxy HOST:PORT for http(s) transfer")
    parser.add_argument('-t', '--timeout', type=int, default=60, help="set socket timeout seconds, default 60s")
    parser.add_argument('video_urls', type=str, nargs='+', help="video urls")
    global args
    args = parser.parse_args()

def download(urls, name, ext, live = False):
    if ext == 'm3u8' and not live:
        ext = 'mp4'
        urls = load_m3u8(urls[0])
    if live:
        launch_ffmpeg_download(urls[0], name + '.' + ext, live)
    else:
        save_urls(urls, name, ext)
        lenth = len(urls)
        if args.merge and lenth > 1:
            launch_ffmpeg(name, ext,lenth)

def handle_videoinfo(info):
    if not args.json:
        info.print_info(args.format, args.info)
    else:
        print(json.dumps(info.jsonlize(), indent=4, sort_keys=True, ensure_ascii=False))
    if args.info or args.json:
        return
    stream_id = args.format or info.stream_types[0]
    urls = info.streams[stream_id]['src']
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
    if args.proxy:
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
                    info_list = m.parser_list(u)
                    if args.start >= len(info_list):
                        log.w('invalid argument -s/--start')
                        log.w('start from beginning')
                        args.start = 0
                    for info in info_list[args.start:]:
                        handle_videoinfo(info)
                else:
                    info = m.parser(u)
                    if type(info) is list:
                        for i in info:
                            handle_videoinfo(i)
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
