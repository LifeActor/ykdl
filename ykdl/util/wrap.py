#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import os
import subprocess
import shlex
from logging import getLogger

logger = getLogger("wrap")

from ykdl.compact import compact_tempfile

posix = os.name == 'posix'

# The maximum length of cmd string
if posix:
    # Used in Unix is ARG_MAX in conf
    ARG_MAX = int(os.popen('getconf ARG_MAX').read())
else:
    # Used in Windows CreateProcess is 32K
    ARG_MAX = 32 * 1024

def launch_player(player, urls, **args):
    if ' ' in player:
        cmd = shlex.split(player, posix=posix)
        if not posix:
            cmd = [arg[1:-1] if arg[0] == arg[-1] == "'" else arg for arg in cmd]
    else:
        cmd = [player]

    if 'mpv' in cmd[0]:
        cmd += ['--demuxer-lavf-o', 'protocol_whitelist=[file,tcp,http]']
        if args['ua']:
            cmd += ['--user-agent', args['ua']]
        if args['referer']:
            cmd += ['--referrer', args['referer']]
        if args['title']:
            cmd += ['--force-media-title', args['title']]
        if args['header']:
            cmd += ['--http-header-fields', args['header']]

    if args['rangefetch']:
        urls = ['http://127.0.0.1:8806/' + url for url in urls]
        cmds = split_cmd_urls(cmd, urls)
        env = os.environ.copy()
        env.pop('HTTP_PROXY', None)
        env.pop('HTTPS_PROXY', None)
        from ykdl.util.rangefetch_server import start_new_server
        new_server = start_new_server(**args['rangefetch'])
        for cmd in cmds:
            subprocess.call(cmd, env=env)
        new_server.server_close()
    else:
        urls = list(urls)
        cmds = split_cmd_urls(cmd, urls)
        if args['proxy']:
            env = os.environ.copy()
            env['HTTP_PROXY'] = args['proxy']
            env['HTTPS_PROXY'] = args['proxy']
        else:
            env = None
        for cmd in cmds:
            subprocess.call(cmd, env=env)

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
    #build input
    inputfile = compact_tempfile(mode='w+t', suffix='.txt', dir='.', encoding='utf-8')
    for i in range(lenth):
        inputfile.write('file \'%s_%d_.%s\'\n' % (basename, i, ext))
    inputfile.flush()

    outputfile = basename+ '.' + ext

    cmd = ['ffmpeg','-f', 'concat', '-safe', '-1', '-y', '-i', inputfile.name, '-c', 'copy', '-hide_banner']
    if ext == 'mp4':
        cmd += ['-absf', 'aac_adtstoasc']

    cmd.append(outputfile)
    print('Merging video %s using ffmpeg:' % basename)
    subprocess.call(cmd)

def launch_ffmpeg_download(url, name, live):
    print('Now downloading: %s' % name)
    if live:
        print('stop downloading by press \'q\'')

    cmd = ['ffmpeg', '-y']

    if not url.startswith('http'):
       cmd += ['-protocol_whitelist', 'file,tcp,http' ]

    cmd += ['-i', url, '-c', 'copy', '-absf', 'aac_adtstoasc',  '-hide_banner', name]

    subprocess.call(cmd)
