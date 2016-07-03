#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ykdl.extractor import VideoExtractor
from ykdl.videoinfo import VideoInfo
from .youkujs import *
from ykdl.util.html import get_content

from ykdl.compact import urlencode

import json
from random import randint

class YoukuBase(VideoExtractor):

    def get_custom_sign(self):
        custom_api = 'https://api.youku.com/players/custom.json?client_id={}&video_id={}&vext=null&embsig=undefined&styleid=undefined'.format(self.client_id, self.vid)
        html = get_content(custom_api)
        data = json.loads(html)
        self.playsign = data['playsign']

    def get_custom_stream(self):
        custom_api = 'http://play.youku.com/partner/get.json?vid={}&ct={}&sign={}&ran={}'.format(self.vid, self.ct, self.playsign, randint(1,9999))
        html = get_content(custom_api)
        data = json.loads(html)['data']
        self.stream_data = data['stream']
        self.ep = data['security']['encrypt_string']
        self.ip = data['security']['ip']

    def prepare(self):
        info = VideoInfo(self.name)
        self.setup(info)
        self.streams_parameter = {}
        for stream in self.stream_data:
            stream_id = stream_code_to_id[stream['stream_type']]
            if not stream_id in info.stream_types:
                self.streams_parameter[stream_id] = {
                    'fileid': stream['stream_fileid'],
                    'segs': stream['segs']
                }
                info.streams[stream_id] = {
                    'container': id_to_container[stream_id],
                    'video_profile': stream_code_to_profiles[stream_id],
                    'size': stream['size']
                }
                info.stream_types.append(stream_id)
                self.extract_single(info, stream_id)

        info.stream_types = sorted(info.stream_types, key = ids.index)
        return info

    def extract_single(self, info, stream_id):
        sid, token = init(self.ep)
        segs = self.streams_parameter[stream_id]['segs']
        streamfileid = self.streams_parameter[stream_id]['fileid']
        urls = []
        no = 0
        for seg in segs:
            k = seg['key']
            assert k != -1
            fileId = getFileid(streamfileid, no)
            ep  = create_ep(sid, fileId, token)
            q = urlencode(dict(
                ctype = self.ct,
                ev    = 1,
                K     = k,
                ep    = ep,
                oip   = str(self.ip),
                token = token,
                yxon  = 1,
                myp   = 0,
                ymovie= 1,
                ts    = seg['total_milliseconds_audio'][:-3],
                hd    = stream_type_to_hd[stream_id],
                special = 'true',
                yyp   = 2
            ))
            nu = '%02x' % no
            u = 'http://k.youku.com/player/getFlvPath/sid/{sid}_{nu}' \
                '/st/{container}/fileid/{fileid}?{q}'.format(
                sid       = sid,
                nu        = nu,
                container = info.streams[stream_id]['container'],
                fileid    = fileId,
                q         = q
            )
            no += 1
            url = json.loads(get_content(u))[0]['server']
            urls.append(url)

        info.streams[stream_id]['src'] = urls
        if not info.streams[stream_id]['src'] and self.password_protected:
            log.e('[Failed] Wrong password.')

