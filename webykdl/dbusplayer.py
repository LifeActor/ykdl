#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gi.repository import GLib
from pydbus import SessionBus
import json

from playthread import Mpvplayer

loop = GLib.MainLoop()
player = Mpvplayer()
player.start()

class DBUSPlayerService(object):
    '''
        <node>
            <interface name='github.zhangn1985.dbplay'>
                <method name='play'>
                    <arg type='s' name='playinfo' direction='in'/>
                </method>
                <method name='stop'/>
                <method name='exit'/>
            </interface>
        </node>
    '''

    def play(self, playinfo):
        player.play(playinfo)
    def stop(self):
        player.stop()
    def exit(self):
        player.exit()
        loop.quit()

bus = SessionBus()
bus.publish('github.zhangn1985.dbplay', DBUSPlayerService())
loop.run()
