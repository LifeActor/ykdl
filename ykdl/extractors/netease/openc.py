# -*- coding: utf-8 -*-

from .._common import *


assert JSEngine, "No JS Interpreter found, can't extract netease openCourse!"

class OpenC(Extractor):
    name = '网易公开课 (163 openCourse)'

    sopported_stream_types = [
        ['TD', 'Shd', '超清'], 
        ['HD',  'Hd', '高清'], 
        ['SD',  'Sd', '标清']
    ]
    name2lang = {
        '中文': 'zh',
        '英文': 'en'
    }

    def list_only(self):
        return self.mid[1] is None

    @staticmethod
    def format_mid(mid):
        if not isinstance(mid, tuple):
            mid = mid, None
        mid = mid[:2]
        assert len(mid) == 2 and mid[0]
        return mid

    def prepare_mid(self):
        return match1(self.url, r'\bpid=(\w+)'), match1(self.url, r'\bmid=(\w+)')

    @functools.cache
    def parse_html(self, url):
        html = get_content(url)
        js = match1(html, 'window\.__NUXT__=(.+);</script>')
        data = JSEngine().eval(js)
        self.logger.debug('data: \n%s', data)
        return data

    def prepare_data(self):
        url = 'https://open.163.com/newview/movie/free?pid={}'.format(self.mid[0])
        data = self.parse_html(url)
        try:
            self.url = data['data'][0]['playUrl']
        except KeyError:
            return data
        else:
            self.mid = None
            return self.prepare_data()

    def prepare(self):
        info = MediaInfo(self.name)

        data = self.prepare_data()
        moiveList = data['state']['movie']['moiveList']
        if not moiveList:
            return

        mid = self.mid[1]
        for movie in moiveList:
            if movie['mid'] == mid:
                break
        assert movie['mid'] == mid, "can't found mid %r" % mid

        title = data['data'][0]['title']
        mtitle = movie['title'].rpartition(title)[-1]
        if mtitle:
            for sp in ['：', '】']:
                t1, _, t2 = mtitle.partition(sp)
                if title.startswith(t1):
                    mtitle = t2
                    break
        if mtitle:
            p = movie['pNumber']
            pc = len(moiveList)
            if pc > 1 and not mtitle[0].isdecimal() and str(p) not in mtitle:
                pl = 0
                while pc:
                    pl += 1
                    pc //= 10
                mtitle = ('{:0>%dd} {}' % pl).format(p, mtitle)
            title = '{title} - {mtitle}'.format(**vars())
        school_info = data['data'][0]
        school = school_info['school']
        director = school_info['director']
        if director and director != 'null':
            if director != school :
                director = '[{school}] {director}'.format(**vars())
        else:
            director = school
        if school not in title:
            title = '[{school}] {title}'.format(**vars())
        info.title = title
        info.artist = director

        for stream_id, tp, stream_profile in self.sopported_stream_types:
            for ext in ['mp4', 'm3u8']:
                for orig in ['', 'Orign']:
                    if stream_id in info.streams:
                        continue
                    url = movie['{ext}{tp}Url{orig}'.format(**vars())]
                    if not url:
                        continue
                    size = movie['{ext}{tp}Size{orig}'.format(**vars())]
                    info.streams[stream_id] = {
                        'container': ext,
                        'profile': stream_profile,
                        'src' : [url],
                        'size': size
                    }

        nlang = 0
        for sub in movie['subList']:
            name = sub['subName']
            if not name:
                if nlang:
                    name = movie['subtitle']
                else:
                    name = '中文'
                nlang += 1
            lang = self.name2lang[name]
            info.subtitles.append({
                'lang': lang,
                'name': name,
                'format': 'srt',
                'src' : sub['subUrl'],
                'size': sub['subSize']
            })

        return info

    def prepare_list(self):
        data = self.prepare_data()
        pid, mid = self.mid
        mids = [movie['mid'] for movie in data['state']['movie']['moiveList']]
        self.set_index(mid, mids)
        for mid in mids:
            yield pid, mid

site = OpenC()
