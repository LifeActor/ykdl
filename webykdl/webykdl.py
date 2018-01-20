#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask
from flask import request
app = Flask(__name__)

from pydbus import SessionBus
bus = SessionBus()
try:
    player = bus.get("github.zhangn1985.dbplay")
except:
    from playthread import Mpvplayer
    player = Mpvplayer()
    player.start()

import json


from ykdl.common import url_to_module

@app.route('/play', methods=['POST', 'GET'])
def play():
    if request.method == 'POST':
        url = request.form['url']
        m,u = url_to_module(url)
        try:
            info = m.parser(u)
        except AssertionError as e: 
            return str(e)
        player_args = info.extra
        player_args['title'] = info.title
        urls = info.streams[info.stream_types[0]]['src']
        video = json.dumps({"urls": urls, "args": player_args})
        player.play(video)
        return "OK"
    else:
        return "curl --data-urlencode \"url=<URL>\" http://IP:5000/play"

@app.route('/stop')
def stop():
    player.stop()
    return "OK"

if __name__ == '__main__':
    app.run(host='0.0.0.0')
