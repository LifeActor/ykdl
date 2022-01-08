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
        self.vid = match1(self.url, 'mid=(\w+)')
        return self.vid is None

    def prepare_data(self):
        html = get_content(self.url)
        js = match1(html, 'window\.__NUXT__=(.+);</script>')
        js_ctx = JSEngine()
        data = js_ctx.eval(js)
        self.logger.debug('video_data: \n%s', data)
        try:
            self.url = data['data'][0]['playUrl']
        except KeyError:
            self.data = data
        else:
            self.prepare_data()

    def prepare(self):
        info = MediaInfo(self.name)

        if self.data is None:
            self.prepare_data()
        data = self.data
        moiveList = data['state']['movie']['moiveList']
        if self.vid is None:
            movie = moiveList[0]
        else:
            for movie in moiveList:
                mid = movie['mid']
                if mid == self.vid:
                    break
            assert mid == self.vid, "can't found mid %r" % mid

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

        for stream, tp, profile in self.sopported_stream_types:
            for ext in ['mp4', 'm3u8']:
                for orig in ['', 'Orign']:
                    if stream in info.streams:
                        continue
                    url = movie['{ext}{tp}Url{orig}'.format(**vars())]
                    if not url:
                        continue
                    size = movie['{ext}{tp}Size{orig}'.format(**vars())]
                    info.streams[stream] = {
                        'container': ext,
                        'video_profile': profile,
                        'src': [url],
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
                'src': sub['subUrl'],
                'size': sub['subSize']
            })

        return info

    def prepare_list(self):
        self.prepare_data()
        return [movie['mid'] for movie in self.data['state']['movie']['moiveList']]

site = OpenC()
