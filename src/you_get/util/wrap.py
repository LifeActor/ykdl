#!/usr/bin/env python
import subprocess
import shlex

def launch_player(player, urls):
    subprocess.call(shlex.split(player) + list(urls))
