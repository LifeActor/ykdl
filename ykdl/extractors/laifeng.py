# -*- coding: utf-8 -*-

from ._common import *

import datetime


class Laifeng(Extractor):
    name = 'laifeng (来疯直播)'

    def prepare(self):
        info = MediaInfo(self.name, True)

        html = get_content(self.url)
        info.artist = match1(html, 'anchorName:\s*\'([^\']+)',
                                   '"anchorName":\s*"([^"]+)"')
        info.title = info.artist + '的直播房间'

        Alias = match1(html, 'initAlias:\'([^\']+)' ,'"ln":\s*"([^"]+)"')
        Token = match1(html, 'initToken: \'([^\']+)', '"tk":\s*"([^"]+)"')
        ts = datetime.datetime.utcnow().isoformat().split('.')[0] + 'Z'
        data = get_response('http://lapi.lcloud.laifeng.com/Play',
                            params={
                                'AppId': 101,
                                'StreamName': Alias,
                                'Action': 'Schedule',
                                'Token': Token,
                                'Version': 2.0,
                                'CallerVersion': 3.3,
                                'Caller': 'flash',
                                'Format': 'HttpFlv',
                                'Timestamp': ts,
                                'rd': random.randint(10000, 99999),
                            }).json()
        assert data['Code'] == 'Success', data['Message']

        stream_url = data['HttpFlv'][0]['Url']
        info.streams['current'] = {
            'container': 'flv',
            'profile': 'current',
            'src' : [stream_url],
            'size': Infinity
        }
        return info

site = Laifeng()
