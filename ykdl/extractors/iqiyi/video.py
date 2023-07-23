# -*- coding: utf-8 -*-

from .._common import *
from .util import md5, md5x, cmd5x


# vms
# src=1702633101b340d8917a69cf8a4b8c7c
# salt=t6hrq6k0n6n6k6qdh6tje6wpb62v7654
# salt=u6fnp3eok0dpftcq9qbr4n9svk8tqh7u

# src=02020031010000000000
# salt=3sj8xof48xof4tk9f4tk9ypgk9ypg5ul

def get_epsodelist(tvid):
    secret_key = 'howcuteitis'
    params = {
        'entity_id': tvid,
        'timestamp': int(time.time() * 1000),
        'src': 'pcw_tvg',
        'vip_status': '0',
        'vip_type': '',
        'auth_cookie': '',
        'device_id': get_random_id(32, 'device_id'),
        'user_id': '',
        'app_version': '3.0.0'
    }
    src = urlencode(sorted(params.items()) + [('secret_key', secret_key)])
    params['sign'] = hash.md5(src).upper()
    data = get_response('https://mesh.if.iqiyi.com/tvg/pcw/base_info',
                        params=params).json()
    return sorted(sum(data['data']['template']['pure_data']['selector_bk'][0]
                          ['videos']['feature_paged']
                          .values(), []),
                  key=lambda ep: ep['album_order'])

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

    vd_2_id = reverse_list_dict({
        '4K': [10, 19],
        'BD': [5, 18, 600],
        'TD': [4, 17, 500],
        'HD': [2, 14, 21, 75, 300],
        'SD': [1, 200],
        'LD': [96, 100]
    })
    id_2_profile = {
        '4K': '4K',
        'BD': '1080p',
        'TD': '720p',
        'HD': '540p',
        'SD': '360p',
        'LD': '210p'
    }

    def format_mid(self, mid):
        if isinstance(mid, (str, bytes)):
            mid = fullmatch(mid, '[av]_[0-9a-z]+')
            assert mid
            self.url = 'https://www.iqiyi.com/{mid}.html'.format(**vars())
            return None
        assert isinstance(mid, tuple)
        mid = mid[:2]
        assert len(mid) == 2 and all(mid)
        return mid

    def parse_html(self):
        html = get_content(self.url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:60.1) Gecko/20100101 Firefox/60.1',
        })
        data = match1(html, "playPageInfo=({.+?});")
        if data:
            return json.loads(data)

        url = match1(html, '(www\.iqiyi\.com/v_[0-9a-z]+\.html)')
        if url:
            self.url = 'https://' + url
            return self.parse_html()

    def prepare_mid(self):
        mid = matchm(self.url, 'curid=([^_]+)_([\w]+)')
        if all(mid):
            return mid
        data = self.parse_html()
        return data and (str(data['tvId']), data['vid'])

    def prepare(self):
        info = MediaInfo(self.name)

        try:
            info_data = self.parse_html()
            assert info_data
        except:
            tvid, vid = self.mid
            info_data = get_response(
                    'http://pcw-api.iqiyi.com/video/video/playervideoinfo',
                    params={'tvid': tvid}).json()['data']
            info.title = info_data['vn']
            info.duration = info_data['plg']
        else:
            tvid = str(info_data['tvId'])
            vid = info_data['vid']
            info.title = info_data['name']
            info.duration = info_data['duration']

        if info_data['payMark']:
            self.logger.warning('<%s> is a VIP video!', info.title)

        def push_stream_vd(vs):
            vd = vs['vd']
            stream_id = self.vd_2_id[vd]
            stream_profile = self.id_2_profile[stream_id]
            fmt = vs.get('fileFormat')
            if fmt:
                stream_id += '-' + fmt
            m3u8 = vs['m3utx']
            info.streams[stream_id] = {
                'container': 'm3u8',
                'profile': stream_profile,
                'src': [m3u8]
            }

        def push_stream_bid(url_prefix, bid, container, fs_array, size):
            stream_id = self.vd_2_id[bid]
            real_urls = []
            for seg_info in fs_array:
                url = url_prefix + seg_info['l']
                json_data = get_response(url).json()
                down_url = json_data['l']
                real_urls.append(down_url)
            stream_profile = self.id_2_profile[stream_id]
            info.streams[stream_id] = {
                'container': container,
                'profile': stream_profile,
                'src' : real_urls,
                'size': size
            }

        def fetch_tmts():
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

        for fetch in (fetch_tmts, fetch_vps, fetch_dash):
            try:
                fetch()
                break
            except AssertionError:
                break
            except Exception as e:
                self.logger.debug(e, exc_info=True)
                continue

        return info

    def list_only(self):
        return self.url and match(self.url, 'a_[0-9a-z]+\.html')

    def prepare_list(self):
        html = get_content(self.url)

        if self.list_only():
            data = matchall(html, "value='({.+})'/>")
            data = json.loads(data)
            epsodelist = data['epsodelist'] + data['updateprevuelist']
            self.set_index(None, epsodelist)
            for ep in epsodelist:
                yield ep['tvId'], ep['vid']
        else:
            mids = [matchall(ep['play_url'], 'tvid=(\d+).+vid=(\w+)')[0]
                    for ep in get_epsodelist(self.mid[0])]
            self.set_index(self.mid, mids)
            for mid in mids:
                yield mid

site = Iqiyi()
