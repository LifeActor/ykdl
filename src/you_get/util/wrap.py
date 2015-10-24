#!/usr/bin/env python

def launch_player(player, urls, size):
    import subprocess
    import shlex
    if size and size != float('inf'):
        size_kb = int(size/1024) + 1
        if 'mpv' in player:
            if size_kb > 2147483647:
                size_kb = 2147483647
            if size_kb < 1024:
                size_kb = 1024
            player += " --cache={}".format(size_kb)
        elif 'mplayer' in player:
            player += " --cache={} --cache-min=1".format(size_kb)
        else:
            log.d("your player: {} 's cache option is not supported!!".format(player))
            log.d("please report issue to https://github.com/zhangn1985/you-get/issues/5")
            log.d("thanks a lot!")
    subprocess.call(shlex.split(player) + list(urls))
