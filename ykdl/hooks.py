#!/usr/bin/env python
# -*- coding: utf-8 -*-

def default_input_hook(title):
    print("please input password for {}".format(title))
    return input(">: ")

hook_input = default_input_hook

def install_input_hook(hook):
    global hook_input = hook
