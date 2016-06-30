#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import shlex
from ykdl.compact import compact_tempfile
from ykdl.util import log

def launch_player(player, urls):
    subprocess.call(shlex.split(player) + list(urls))

def launch_ffmpeg(basename, ext, lenth):
    #build input
    inputfile = compact_tempfile(mode='w+t', suffix='.txt', dir='.', encoding='utf-8')
    for i in range(lenth):
        inputfile.write('file \'%s_%d_.%s\'\n' % (basename, i, ext))
    inputfile.flush()

    outputfile = basename+ '.' + ext

    cmd = ['ffmpeg','-f', 'concat', '-safe', '-1', '-y', '-i', inputfile.name, '-c', 'copy']
    if ext == 'mp4':
        cmd += ['-absf', 'aac_adtstoasc']

    cmd.append(outputfile)

    subprocess.call(cmd)

def launch_ffmpeg_m3u8(url, name, live):
    if live:
        log.i('stop downloading by press \'q\'')

    cmd = ['ffmpeg', '-y', '-i', url, '-c', 'copy', '-absf', 'aac_adtstoasc', name]

    subprocess.call(cmd)
