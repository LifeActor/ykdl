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
        cmd += ['http://127.0.0.1:8806/' + url for url in urls]
        env = os.environ.copy()
        env.pop('HTTP_PROXY', None)
        env.pop('HTTPS_PROXY', None)
        from ykdl.util.rangefetch_server import start_new_server
        new_server = start_new_server(**args['rangefetch'])
        subprocess.call(cmd, env=env)
        new_server.server_close()
    else:
        cmd += list(urls)
        if args['proxy']:
            env = os.environ.copy()
            env['HTTP_PROXY'] = args['proxy']
            env['HTTPS_PROXY'] = args['proxy']
            subprocess.call(cmd, env=env)
        else:
            subprocess.call(cmd)

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
