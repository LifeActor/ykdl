from logging import getLogger
from importlib import import_module
from urllib.request import HTTPCookieProcessor

from .common import alias, url_to_module
from .videoinfo import VideoInfo
from .util.http import add_default_handler, remove_default_handler, \
                       install_default_handlers, fake_headers, get_content, \
                       url_info
from .util.match import match1


__all__ = ['VideoExtractor', 'SimpleExtractor', 'EmbedExtractor']

class VideoExtractor:

    cookiejar = None

    def __init__(self):
        self.logger = getLogger(self.name)
        self.url = None
        self.vid = None

    def parser(self, url):
        self.url = None
        self.vid = None
        if isinstance(url, str) and url.startswith('http'):
            self.url = url
            if self.list_only():
                return self.parser_list(url)
        else:
            self.vid= url

        info = self.prepare()
        if info:
            info.sort()
        return info

    def parser_list(self, url):
        self.url = url
        self._is_list = True
        video_list = self.prepare_list()
        if not video_list:
            raise NotImplementedError(
                    'playlist not support for {self.name} with url: {self.url}'
                    .format(**vars()))
        for video in video_list:
            if isinstance(video, VideoInfo):
                info = video
            else:
                info = self.parser(video)
            if info:
                info.sort()
                yield info

    def prepare(self):
        '''
        this API is to do real job to get source URL, or site and VID
        sometimes title
        MUST override!!
        '''
        pass

    def prepare_list(self):
        '''
        this API is to do real job to get source URL, or site and VID
        sometimes title
        MUST override!!
        '''
        pass

    @property
    def is_list(self):
        try:
            return self._is_list
        except AttributeError:
            self._is_list = self.list_only()
            return self._is_list

    def list_only(self):
        '''
        this API is to check if only the list informations is included
        if true, go to parser list mode
        MUST override!!
        '''
        pass

    def install_cookie(self):
        '''Install HTTPCookieProcessor to default opener.'''
        if self.cookiejar is None:
            handler = HTTPCookieProcessor()
            add_default_handler(handler)
            install_default_handlers()
            self.cookiejar = handler.cookiejar

    def uninstall_cookie(self):
        '''Uninstall HTTPCookieProcessor from default opener.'''
        if self.cookiejar:
            remove_default_handler(HTTPCookieProcessor)
            install_default_handlers()
            self.cookiejar = None

    def get_cookie(self, domain, path, name):
        '''Return specified cookie in existence, or None.

        MUST call self.install_cookie() before use.
        '''
        try:
            return self.cookiejar._cookies[domain][path][name]
        except KeyError:
            pass

    def get_cookies(self, domain=None, path=None, name=None):
        '''Get cookies in existence.
        No param (None) get all, mismatch param get empty.

        MUST call self.install_cookie() before use.
        '''
        if name and path and domain:
            return [self.get_cookie(domain, path, name)]
        cookies = []
        c = self.cookiejar._cookies
        if domain is None:
            dl = c.values()
        else:
            d = c.get(domain)
            dl = d and [d] or []
        for d in dl:
            if path is None:
                pl = d.values()
            else:
                p = d.get(path)
                pl = p and [p] or []
            for p in pd:
                if name is None:
                    cookies.extend(p.values())
                else:
                    n = p.get(name)
                    if n:
                        cookies.append(n)
        return cookies


class SimpleExtractor(VideoExtractor):

    name = 'SimpleExtractor'

    def __init__(self):
        VideoExtractor.__init__(self)
        self.html = ''
        self.title_pattern = ''
        self.url_pattern = ''
        self.artist_pattern = ''
        self.live = False
        self.headers = fake_headers
        self.init()

    def init(self):
        pass

    def get_title(self):
        if self.title_pattern:
            self.info.title = match1(self.html, self.title_pattern)

    def get_artist(self):
        if self.artist_pattern:
            self.info.artist = match1(self.html, self.artist_pattern)

    def get_url(self):
        if self.url_pattern:
            self.v_url = [match1(self.html, self.url_pattern)]

    def get_info(self):
        size=0
        ext=''
        for u in self.v_url:
            _, ext, temp = url_info(u)
            size += temp
        return ext, size

    def l_assert(self):
        pass

    def reprocess(self):
        pass

    def prepare(self):
        self.info = VideoInfo(self.name, self.live)
        self.l_assert()
        self.html = get_content(self.url, headers=self.headers)
        self.get_title()
        self.get_artist()
        self.get_url()
        self.reprocess()
        ext, size = self.get_info()
        self.info.stream_types.append('current')
        self.info.streams['current'] = {
            'container': ext,
            'src': self.v_url,
            'size' : size
        }
        return self.info


class EmbedExtractor(VideoExtractor):
    '''
    this class is to help video embed site to handle
    video from other site.
    we just need to know the source URL, or source site name, and video ID
    that's enough.
    with site name and VID, develop can easily to find out the real URL.

        embedextractor.video_info['url'] = url

    or

        embedextractor.video_info['site'] = site
        embedextractor.video_info['vid'] = vid

    compatible: also receive the video info which will return directly.

        embedextractor.video_info['info'] = info

    because embed site don't have video info, so they don't need stream_info.
    '''

    def __init__(self):
        super().__init__()
        self.video_info = None
        self.video_info_list = None

    @staticmethod
    def new_video_info():
        return {'extra': {}}

    def _parser(self, video_info):
        if 'info' in video_info:
            return video_info['info']

        elif 'site' in video_info:
            site = video_info['site']
            vid = video_info['vid']
            if site in alias.keys():
                site = alias[site]
            s = import_module('.'.join(['ykdl','extractors',site])).site
            info = s.parser(vid)
 
        elif 'url' in video_info:
            url = video_info['url']
            s, u = url_to_module(url)
            info = s.parser(u)

        if 'title' in video_info:
            info.title = video_info['title']
        if 'artist' in video_info:
            info.artist = video_info['artist']
        if 'extra' in video_info and video_info['extra']:
            info.extra.update(video_info['extra'])

        return info

    def parser(self, url):
        self.url = url
        if self.is_list:
            return self.parser_list(url)

        self.video_info = self.new_video_info()
        self.prepare()

        if not self.video_info:
            raise NotImplementedError(self.url + ' is not supported')

        info = self._parser(self.video_info)
        if info:
            if self.name != info.site:
                info.site = '{self.name} / {info.site}'.format(**vars())
            info.sort()
        return info

    def parser_list(self, url):
        self.url = url
        self.video_info_list = []
        self.prepare_playlist()

        if not self.video_info_list:
            raise NotImplementedError(
                'Playlist is not supported for {self.name} with url: {self.url}'
                .format(**vars()))

        for video in self.video_info_list:
            if isinstance(video, VideoInfo):
                info = video
            else:
                info = self._parser(video)
            if info:
                info.sort()
                yield info

