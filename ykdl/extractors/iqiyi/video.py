# -*- coding: utf-8 -*-

from .._common import *
from .util import md5, md5x, cmd5x


# vms
# src=1702633101b340d8917a69cf8a4b8c7c
# salt=t6hrq6k0n6n6k6qdh6tje6wpb62v7654
# salt=u6fnp3eok0dpftcq9qbr4n9svk8tqh7u

# src=02020031010000000000
# salt=3sj8xof48xof4tk9f4tk9ypgk9ypg5ul

def gettmts(tvid, vid):
    tm = int(time.time() * 1000)
    key = 'd5fb4bd9d50c4be6948c97edd7254b0e'
    host = 'https://cache.m.iqiyi.com'
    params = {
        'src': '76f90cbd92f94a2e925d83e8ccd22cb7',
        'sc': md5(str(tm) + key + vid),
        't': tm
    }
    req_url = '{host}/tmts/{tvid}/{vid}/'.format(**vars())
    return get_response(req_url, params=params).json()

def getdash(tvid, vid, bid=500):
    cmd5x_null = cmd5x('')
    tm = int(time.time() * 1000)
    host = 'https://cache.video.iqiyi.com'
    params = urlencode({
        #'uid': '',
        'k_uid': get_random_id(32, 'k_uid'), # necessary
        #'dfp': dfp,
        #'pck': '',
        #'bop': '{{"version":"10.0","dfp":"{dfp}"}}'.format(dfp=dfp),
        # keys above are relative to cookies
        'tvid': tvid,
        'bid': bid,
        'vid': vid,
        'src': '01010031010000000000',
        'vt': 0,
        'rs': 1,
        'ori': 'pcw',
        'ps': 1,
        'pt': 0,
        'd': 0,
        's': '',
        'lid': '',
        'cf': '',
        'ct': '',
        'authKey': cmd5x('{cmd5x_null}{tm}{tvid}'.format(**vars())),
        'k_tag': 1,
        'ost': 0,
        'ppt': 0,
        'locale': 'zh_cn',
        'prio': '{"ff":"f4v","code":2}',
        'k_err_retries': 0,
        'up': '',
        'qd_v': 2,
        'tm': tm,
        'qdy': 'a',
        'qds': 0,
        'ut': 0, # 600 bid isn't available
        # relative to encode
        #'k_ft1': ,
        #'k_ft4': ,
        #'k_ft5': ,
    })
    src = '/dash?' + params
    vf = cmd5x(src)
    req_url = '{host}{src}&vf={vf}'.format(**vars())
    return get_response(req_url).json()

def getvps(tvid, vid):
    tm = int(time.time() * 1000)
    host = 'http://cache.video.qiyi.com'
    params = urlencode({
        'tvid': tvid,
        'vid': vid,
        'v': 0,
        'qypid': '{}_12'.format(tvid),
        'src': '01012001010000000000',
        't': tm,
        'k_tag': 1,
        'k_uid': get_random_id(32, 'k_uid'),
        'rs': 1,
    })
    src = '/vps?' + params
    vf = md5x(src)
    req_url = '{host}{src}&vf={vf}'.format(**vars())
    return get_response(req_url).json()

class Iqiyi(Extractor):
    name = '爱奇艺 (Iqiyi)'

    vd_2_id = dict(sum([[(vd, id) for vd in vds] for id, vds in {
        '4K': [10, 19],
        'BD': [5, 18, 600],
        'TD': [4, 17, 500],
        'HD': [2, 14, 21, 75, 300],
        'SD': [1, 200],
        'LD': [96, 100]
    }.items()], []))
    id_2_profile = {
        '4K': '4K',
        'BD': '1080p',
        'TD': '720p',
        'HD': '540p',
        'SD': '360p',
        'LD': '210p'
    }

    def prepare(self):
        info = MediaInfo(self.name)

        if self.url and not self.vid:
            vid = match(self.url, 'curid=([^_]+)_([\w]+)')
            if vid:
                self.vid = vid
                try:
                    info_json = get_response(
                            'http://pcw-api.iqiyi.com/video/video/playervideoinfo',
                            params={'tvid': self.vid[0]}).json()
                    info.title = info_json['data']['vn']
                except:
                    self.vid = None

        def get_vid():
            html = get_content(self.url)
            video_info = match1(html, ":video-info='(.+?)'")

            if video_info:
                video_info = json.loads(video_info)
                self.vid = str(video_info['tvId']), str(video_info['vid'])
                info.title = video_info['name']

            else:
                tvid = match1(html,
                              'tvId:\s*"([^"]+)',
                              'data-video-tvId="([^"]+)',
                              '''\['tvid'\]\s*=\s*"([^"]+)''',
                              '"tvId":\s*([^,]+)')
                videoid = match1(html,
                                'data-video-vid="([^"]+)',
                                'vid"?\'?\]?\s*(?:=|:)\s*"?\'?([^"\',]+)')
                if not (tvid and videoid):
                    url = match1(html, '(www\.iqiyi\.com/v_\w+\.html)')
                    if url:
                        self.url = 'https://' + url
                        return get_vid()
                self.vid = (tvid, videoid)
                info.title = match1(html, '<title>([^<]+)').split('-')[0]

        if self.url and not self.vid:
            get_vid()
        tvid, vid = self.vid
        assert tvid and vid, "can't play this video!!"

        def push_stream_vd(vs):
            vd = vs['vd']
            stream = self.vd_2_id[vd]
            stream_profile = self.id_2_profile[stream]
            fmt = vs.get('fileFormat')
            if fmt:
                stream += '-' + fmt
            m3u8 = vs['m3utx']
            info.streams[stream] = {
                'video_profile': stream_profile,
                'container': 'm3u8',
                'src': [m3u8],
                'size': 0
            }

        def push_stream_bid(url_prefix, bid, container, fs_array, size):
            stream = self.vd_2_id[bid]
            real_urls = []
            for seg_info in fs_array:
                url = url_prefix + seg_info['l']
                json_data = get_response(url).json()
                down_url = json_data['l']
                real_urls.append(down_url)
            stream_profile = self.id_2_profile[stream]
            info.streams[stream] = {
                'video_profile': stream_profile,
                'container': container,
                'src': real_urls,
                'size': size
            }

        def fetch_tmts():
            raise
            # try use tmts first
            # less http requests, get results quickly
            tmts_data = gettmts(tvid, vid)
            assert tmts_data['code'] == 'A00000'
            vs_array = tmts_data['data']['vidl']
            for vs in vs_array:
                push_stream_vd(vs)
            vip_conf = tmts_data['data'].get('ctl', {}).get('configs')
            if vip_conf:
                for vds in (('5', '18'), ('10', '19')):
                    for vd in vds:
                        if vd in vip_conf:
                            tmts_data = gettmts(tvid, vip_conf[vd]['vid'])
                            if tmts_data['code'] == 'A00000':
                                push_stream_vd(tmts_data['data'])
                                break
        def fetch_vps():
            # use vps as preferred fallback
            vps_data = getvps(tvid, vid)
            assert vps_data['code'] == 'A00000'
            url_prefix = vps_data['data']['vp'].get('du')
            assert url_prefix
            vs_array = vps_data['data']['vp']['tkl'][0]['vs']
            for vs in vs_array:
                bid = vs['bid']
                fs_array = vs['fs']
                size = vs['vsize']
                push_stream_bid(url_prefix, bid, 'flv', fs_array, size)

        def fetch_dash():
            # use dash as fallback
            for bid in (500, 300, 200, 100):
                dash_data = getdash(tvid, vid, bid)
                assert dash_data['code'] == 'A00000'
                url_prefix = dash_data['data'].get('dd')
                if url_prefix is None:
                    continue
                streams = dash_data['data']['program']['video']
                for stream in streams:
                    if 'fs' in stream:
                        _bid = stream['bid']
                        container = stream['ff']
                        fs_array = stream['fs']
                        size = stream['vsize']
                        push_stream_bid(url_prefix, _bid, container, fs_array, size)
                        break

        for fetch in (fetch_tmts, fetch_vps, fetch_dash):
            try:
                fetch()
                break
            except AssertionError:
                break
            except Exception as e:
                self.logger.debug(e, exc_info=True)
                continue

        assert info.streams, "can't play this video!!"
        return info

    def prepare_list(self):
        html = get_content(self.url)

        return matchall(html, 'data-tvid=\"([^\"]+)\" data-vid=\"([^\"]+)\"')

site = Iqiyi()
