#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import os
import sys
import subprocess
import shlex
from logging import getLogger

logger = getLogger("wrap")

from ykdl.compact import compact_tempfile
from .html import fake_headers

posix = os.name == 'posix'
nt = os.name == 'nt'

# The maximum length of cmd string
if posix:
    # Used in Unix is ARG_MAX in conf
    ARG_MAX = int(os.popen('getconf ARG_MAX').read())
else:
    # Used in Windows CreateProcess is 32K
    ARG_MAX = 32 * 1024

class PlayerHandle(object):
    def __init__(self, cmds, env, cleanup=[]):
        self.handle = None
        self.cmds = cmds
        self.env = env
        if cleanup:
            if callable(cleanup):
                cleanup = [cleanup]
            else:
                try:
                    cleanup = [c for c in cleanup if callable(c)]
                except:
                    cleanup = []
        self.cleanup = cleanup

    def __getattr__(self, name):
        return getattr(self.handle, name)

    def wait(self, *args, **kwargs):
        if not self.handle:
            self.play()

    def play(self):
        if self.handle:
            return
        try:
            for cmd in self.cmds:
                self.handle = handle = subprocess.Popen(cmd, env=self.env)
                handle.wait()
        finally:
            self.terminate()

    def terminate(self):
        if self.handle:
            self.handle.terminate()
        while self.cleanup:
            self.cleanup.pop()()

    kill = terminate

def launch_player(player, urls, ext, play=True, **args):
    if ' ' in player:
        lex = shlex.shlex(player, posix=nt or posix)
        lex.whitespace_split = True
        if nt:
            lex.quotes = '"'
            lex.escape = ''
        cmd = list(lex)
    else:
        cmd = [player]

    if 'mpv' in cmd[0]:
        if ext == 'm3u8' and any(os.path.isfile(url) for url in urls):
            cmd += ['--demuxer-lavf-o=protocol_whitelist=[file,http,https,tls,rtp,tcp,udp,crypto,httpproxy]']
        if args['ua']:
            cmd += ['--user-agent=' + args['ua']]
        if args['referer']:
            cmd += ['--referrer=' + args['referer']]
        if args['title']:
            cmd += ['--force-media-title=' + args['title']]
        if args['header']:
            header = args['header']
            if not isinstance(header, str):
                header = ','.join("'{}: {}'".format(k, v) for k, v in header.items())
            cmd += ['--http-header-fields=' + header]
        if args['subs']:
            for sub in args['subs']:
                cmd += ['--sub-file=' + sub]

    start_new_server = None
    if args['rangefetch']:
        try:
            from ykdl.util.rangefetch_server import start_new_server
        except ImportError:
            logger.warning('start rangefetch failed, please install urllib3 to use it')
        else:
            urls = ['http://127.0.0.1:8806/' + url for url in urls]
            cmds = split_cmd_urls(cmd, urls)
            env = os.environ.copy()
            env.pop('HTTP_PROXY', None)
            env.pop('HTTPS_PROXY', None)
            cleanup = start_new_server(**args['rangefetch']).server_close
            phandle = PlayerHandle(cmds, env, cleanup=cleanup)
    if start_new_server is None:
        urls = list(urls)
        cmds = split_cmd_urls(cmd, urls)
        if args['proxy'].lower().startswith('http:'):
            env = os.environ.copy()
            env['HTTP_PROXY'] = args['proxy']
            env['HTTPS_PROXY'] = args['proxy']
        else:
            env = None
        phandle = PlayerHandle(cmds, env)
    if play:
        phandle.play()
    return phandle

def split_cmd_urls(cmd, urls):
    _cmd = cmd + urls
    cmd_len = len(subprocess.list2cmdline(_cmd))
    if cmd_len > ARG_MAX:
        n = cmd_len // ARG_MAX + 1
        m = len(urls) // n + 1
        cmds = []
        for i in range(n):
            s = i * m
            e = s + m
            cmds.append(cmd + urls[s:e])
    else:
        cmds = [_cmd]
    return cmds

def launch_ffmpeg(basename, ext, lenth):
    print('Merging video %s using FFmpeg:' % basename)
    if ext == 'ts':
        outputfile = basename + '.mp4'
    else:
        outputfile = basename + '.' + ext

    if ext in ['ts', 'mpg', 'mpeg']:
        cmd = [ 'ffmpeg',
                '-y', '-hide_banner',
                '-i', '-',
                '-c', 'copy',
                outputfile ]
        pipe_input = subprocess.Popen(cmd, stdin=subprocess.PIPE).stdin

        # use pipe pass data does not need to wait subprocess
        bufsize = 1024 * 64
        for i in range(lenth):
            inputfile = '%s_%d.%s' % (basename, i, ext)
            with open(inputfile, 'rb') as fp:
                data = fp.read(bufsize)
                while data:
                    pipe_input.write(data)
                    data = fp.read(bufsize)
    else:
        # build input file
        inputfile = compact_tempfile(mode='w+t', suffix='.txt', dir='.', encoding='utf-8')
        for i in range(lenth):
            inputfile.write("file '%s_%d.%s'\n" % (basename, i, ext))
        inputfile.flush()

        cmd = [ 'ffmpeg',
                '-y', '-hide_banner',
                '-safe', '-1',
                '-f', 'concat',
                '-i', inputfile.name,
                '-c', 'copy',
                outputfile ]
        if ext == 'mp4':
            cmd[-1:-1] = ['-bsf:a', 'aac_adtstoasc']
        subprocess.call(cmd)

        if os.name == 'nt':
            try:
                inputfile.close()
                os.remove(inputfile.name)
            except:
                pass

def launch_ffmpeg_download(url, name):
    print('Now downloading: %s' % name)
    logger.warning('''
=================================
  stop downloading by press 'q'
=================================
''')

    cmd = [ 'ffmpeg',
            '-y', '-hide_banner',
            '-headers', ''.join('%s: %s\r\n' % x for x in fake_headers.items()),
            '-i', url,
            '-c', 'copy',
            '-bsf:a', 'aac_adtstoasc',
            name ]
    if os.path.isfile(url):
       cmd[2:2] = ['-protocol_whitelist', 'file,http,https,tls,rtp,tcp,udp,crypto,httpproxy']

    subprocess.call(cmd)
