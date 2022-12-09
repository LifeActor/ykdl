# -*- coding: utf-8 -*-

from ._common import *


class PPTV(Extractor):
    # https://tv.pptv.com/
    name = 'PPTV (PP聚力)'

    id_2_profile = {
        'BD': '蓝光',
        'TD': '超清',
        'HD': '高清',
        'SD': '高清',
        'LD': '流畅'
    }

    def prepare_mid(self):
        html = get_content(self.url)
        return match1(html, '"(?:c|ps)id":"?(\d+)')

    def prepare(self):
        info = MediaInfo(self.name)

        #key = gen_key(int(time.time()) - 60)
        data = get_response('https://web-play.pptv.com/webplay3-0-{self.mid}.xml'
                            .format(**vars()),
                            params={
                                'zone': 8,
                                'version': 4,
                                'username': '',
                                'ppi': '302c3333',
                                'type': 'ppbox.launcher',
                                'pageUrl': 'http://v.pptv.com',
                                'o': 0,
                                'referrer': '',
                                'kk': '',
                                'scver': 1,
                                'appplt': 'flp',
                                'appid': 'pptv.flashplayer.vod',
                                'appver': '3.4.3.3',
                                'nddp': 1
                            }).xml()['root']
        assert 'error' not in data, data['error'][0]['@message']

        info.title = data['channel'][0]['@nm']
        for item, dt, drag in zip(data['channel'][0]['file'][0]['item'],
                                  data['dt'],
                                  data.get('dragdata') or data['drag']):
            host = dt['sh']
            rid = dt['@rid']
            params = urlencode({
                #'key': key,  # it is now useless
                'k': unquote(dt['key'][0]['#text']),
                'fpp.ver': '1.3.0.23',
                'type': 'ppbox.launcher'
            })
            urls = []
            for seg in drag['sgm']:
                no = seg['@no']
                urls.append('http://{host}/{no}/{rid}?{params}'.format(**vars()))

            stream_id = format_vps(item['@width'], item['@height'])[0]
            stream_profile = self.id_2_profile[stream_id]
            info.streams[stream_id] = {
                'container': 'mp4',
                'profile': stream_profile,
                'src' : urls,
                'size': int(item['@filesize'])
            }

        return info

site = PPTV()
