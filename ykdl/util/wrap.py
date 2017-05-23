#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import shlex
from logging import getLogger

logger = getLogger("wrap")

from ykdl.compact import compact_tempfile


def launch_player(player, urls):
    subprocess.call(shlex.split(player) + list(urls))

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

    cmd = ['ffmpeg', '-y', '-i', url, '-c', 'copy', '-absf', 'aac_adtstoasc',  '-hide_banner', name]

    subprocess.call(cmd)
