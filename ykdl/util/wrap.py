#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import shlex

def launch_player(player, urls):
    subprocess.call(shlex.split(player) + list(urls))
