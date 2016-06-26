#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.common import url_to_module
from ykdl.compact import ProxyHandler, build_opener, install_opener, compact_str
from .util import log
from .param import arg_parser

import socket
import os
import sys

def main():
    args = arg_parser()
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
                if not u == url:
                    args.video_urls[args.video_urls.index(url)]  = u
                if args.playlist:
                    m.download_playlist(u, args)
                else:
                    m.download(u, args)
            except AssertionError as e:
                log.wtf(compact_str(e))
                exit = 1
            except (RuntimeError, NotImplementedError, SyntaxError) as e:
                log.e(compact_str(e))
                exit = 1
        sys.exit(exit)
    except KeyboardInterrupt:
        print('\nInterrupted by Ctrl-C')
