from logging import getLogger
from importlib import import_module
from types import GeneratorType

from .common import alias, url_to_module
from .mediainfo import MediaInfo
from .util.http import get_content, url_info
from .util.match import match1


__all__ = ['Extractor', 'SimpleExtractor', 'EmbedExtractor']

class Extractor:

    def get_proxy(self, parser, url):
        assert parser in ['parser', 'parser_list']
        info = getattr(self, parser)(url)
        if info:
            return ProxyExtractor(self, info)

    def __init__(self):
        self.logger = getLogger(self.name)
        self.url = None
        self.vid = None
        self.from1 = None

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
            info.orig_url = url
        return info

    def parser_list(self, url):
        self.url = url
        self._is_list = True
        media_list = self.prepare_list()
        if not media_list:
            raise NotImplementedError(
                    'playlist not support for {self.name} with url: {self.url}'
                    .format(**vars()))
        for media in media_list:
            if isinstance(media, MediaInfo):
                info = media
            else:
                info = self.parser(media)
            if info:
                info.orig_url = url
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


class ProxyExtractor(Extractor):

    def __init__(self, real, info):
        self.name = real.name
        self.url = real.url
        self.vid = real.vid
        if type(info) in [GeneratorType, list]:
            self.info_list = info
        else:
            self.info_list = [info]

    def parser(self, url):
        for info in self.parser_list(url):
            return info

    def parser_list(self, url):
        if url in [self.url, self.vid]:
            for info in self.info_list:
                yield info


class SimpleExtractor(Extractor):

    name = 'SimpleExtractor'

    def __init__(self):
        Extractor.__init__(self)
        self.html = ''
        self.title_pattern = ''
        self.url_pattern = ''
        self.artist_pattern = ''
        self.live = False
        self.headers = {}
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
        self.info = MediaInfo(self.name, self.live)
        self.l_assert()
        self.html = get_content(self.url, headers=self.headers)
        self.get_title()
        self.get_artist()
        self.get_url()
        self.reprocess()
        ext, size = self.get_info()
        self.info.streams['current'] = {
            'container': ext,
            'src': self.v_url,
            'size' : size
        }
        return self.info


class EmbedExtractor(Extractor):
    '''
    this class is to help media embed site to handle
    media from other site.
    we just need to know the source URL, or source site name, and media ID
    that's enough.
    with site name and VID, develop can easily to find out the real URL.

        embedextractor.media_info['url'] = url

    or

        embedextractor.media_info['site'] = site
        embedextractor.media_info['vid'] = vid

    compatible: also receive the media info which will return directly.

        embedextractor.media_info['info'] = info

    because embed site don't have media info, so they don't need stream_info.
    '''

    def __init__(self):
        super().__init__()
        self.media_info = None
        self.media_info_list = None

    @staticmethod
    def new_media_info():
        return {'extra': {}}

    def _parser(self, media_info):
        if 'info' in media_info:
            return media_info['info']

        elif 'site' in media_info:
            site = media_info['site']
            vid = media_info['vid']
            if site in alias.keys():
                site = alias[site]
            s = import_module('.'.join(['ykdl','extractors',site])).site
            info = s.parser(vid)
 
        elif 'url' in media_info:
            url = media_info['url']
            s, u = url_to_module(url)
            info = s.parser(u)

        if 'title' in media_info:
            info.title = media_info['title']
        if 'artist' in media_info:
            info.artist = media_info['artist']
        if 'extra' in media_info and media_info['extra']:
            info.extra.update(media_info['extra'])

        return info

    def parser(self, url):
        self.url = url
        if self.is_list:
            return self.parser_list(url)

        self.media_info = self.new_media_info()
        self.prepare()

        if not self.media_info:
            raise NotImplementedError(self.url + ' is not supported')

        info = self._parser(self.media_info)
        if info:
            if self.name != info.site:
                info.site = '{self.name} / {info.site}'.format(**vars())
        return info

    def parser_list(self, url):
        self.url = url
        self.media_info_list = []
        self.prepare_playlist()

        if not self.media_info_list:
            raise NotImplementedError(
                'Playlist is not supported for {self.name} with url: {self.url}'
                .format(**vars()))

        for media in self.media_info_list:
            if isinstance(media, MediaInfo):
                info = media
            else:
                info = self._parser(media)
            if info:
                yield info

