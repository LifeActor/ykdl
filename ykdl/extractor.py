import traceback
from logging import getLogger
from importlib import import_module
from types import GeneratorType

from .common import alias, url_to_module
from .mediainfo import MediaInfo
from .util.http import get_content, url_info
from .util.match import match1
from .util.wrap import deprecated


__all__ = ['Extractor', 'SimpleExtractor', 'EmbedExtractor']

class Extractor:

    def get_proxy(self, parser, url):
        assert parser in ['parser', 'parser_list']
        try:
            info = getattr(self, parser)(url)
        except AssertionError:
            return None
        else:
            return ProxyExtractor(url, self, info)

    def __init__(self):
        self.logger = getLogger(self.name)
        self.url = None
        self._mid = None
        self.start = -1
        self.end = 'N/A'

    @property
    def vid(self):
        deprecated('Extractor().vid is deprecated, '
                   'please use Extractor().mid instead.')
        return self.mid

    @vid.setter
    def vid(self, value):
        deprecated('Extractor().vid is deprecated, '
                   'please use Extractor().mid instead.')
        self._mid = value

    @property
    def mid(self):
        if self._mid is None:
            self.mid = self.prepare_mid()
        assert self._mid, 'no media ID found!'
        return self._mid

    @mid.setter
    def mid(self, value):
        if not value:
            self._mid = None
            return
        if isinstance(value, list):
            value = tuple(value)
        try:
            self._mid = self.format_mid(value)
        except AssertionError:
            raise ValueError('invalid media ID: {value!r}'.format(**vars()))
        self.logger.debug(f'media ID: {self._mid}')

    @property
    def sum(self):
        if isinstance(self.end, int):
            return self.end + 1
        return self.end

    def parser(self, url):
        self.url = None
        self.mid = None
        if isinstance(url, str) and url.startswith('http'):
            self.url = url
            if not hasattr(self, '_is_list') and self.list_only():
                return self.parser_list(url)
        else:
            self.mid = url

        info = self.prepare()
        assert info and info.streams, 'no media found!'
        info.orig_url = url
        return info

    def set_index(self, mid, mids):
        '''Input `int` is the order base 1, or index `mid` from `mids` list.'''
        if mids and isinstance(mids, list):
            if mid and self.start < 0:
                try:
                    self.start = mids.index(mid)
                except ValueError:
                    self.logger.debug(
                            'MID %r can not be found, may a pay media', mid)
            self.end = len(mids) - 1
        elif isinstance(mid, int) or isinstance(mids, int):
            if mid and mid > 0 and self.start < 0:
                self.start = mid - 1
            if mids and mids > 0:
                self.end = mids - 1

    def parser_list(self, url):
        self.url = url
        self._is_list = True
        i = None
        try:
            media_list = self.prepare_list()
            if not media_list:
                return

            self.logger.debug('> start at index %d', self.start)
            for i, media in enumerate(media_list):
                if i < self.start:
                    self.logger.debug('> skip index %d: %r', i, media)
                    continue
                if isinstance(media, MediaInfo):
                    info = media
                else:
                    info = self.parser(media)
                if self.sum != 1:
                    info.index = i + 1, self.sum
                info.orig_url = url
                yield info
        except:
            if i is None:
                self.logger.debug(traceback.format_exc())
        finally:
            self.start = -1
            self.end = 'N/A'
            del self._is_list
            if i is None:
                raise NotImplementedError(
                        'playlist not support for {self.name} with url: {url}'
                        .format(**vars()))

    @staticmethod
    def format_mid(mid):
        '''
        This method make MID as a standard structure.
        Override if needed.
        About input mid (see `mid.setter` source above):
            `bool(mid)` is always `True`.
            `type(mid)` never be `list`, `list` will be auto convert to `tuple`.
            recommend raise invalid mid via keyword `assert`.
        '''
        return mid

    def prepare_mid(self):
        '''
        This method is to do real job to get MID.
        Override if needed.
        '''
        raise NotImplementedError('method `prepare_mid()` of Extractor "{self.name}" '
                                  'is not implemented'.format(**vars()))

    def prepare(self):
        '''
        This method is to do real job to get source URL, or site and MID.
        sometimes title
        MUST override!!
        '''
        raise NotImplementedError('method `prepare()` of Extractor "{self.name}" '
                                  'is not implemented'.format(**vars()))

    def prepare_list(self):
        '''
        This method is to do real job to get source URL, or site and MID.
        Override if needed.
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
        This method is to check if only the list informations is included,
        if true, go to parser list mode.
        Override if needed.
        '''
        pass


class ProxyExtractor(Extractor):

    def __init__(self, url, real, info):
        self._orig_url = url
        self.name = real.name
        self.url = real.url
        self._mid = real._mid
        if isinstance(info, (GeneratorType, list)):
            self.info_list = info
        else:
            self.info_list = [info]

    def parser(self, url):
        for info in self.parser_list(url):
            return info

    def parser_list(self, url):
        if url and url in [self._orig_url, self.url, self._mid]:
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
        size = 0
        ext = ''
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
            'size': size
        }
        return self.info


class MediaInfoDict(dict):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setdefault('extra', {})

    def __hash__(self):
        return hash((self['site'], self['mid']))


class EmbedExtractor(Extractor):
    '''
    This class is to help media embed site to handle media from other site.
    We just need to know the source URL, or source site name, and media ID
    that's enough.
    With site name and MID, develop can easily to find out the real URL.

        embedextractor.media_info['url'] = url

    or

        embedextractor.media_info['site'] = site
        embedextractor.media_info['mid'] = mid

    Compatible: also receive the media info which will return directly.

        embedextractor.media_info['info'] = info

    Because embed site don't have media info, so they don't need stream_info.
    '''

    def __init__(self):
        super().__init__()
        self.media_info = None
        self.media_info_list = None

    @staticmethod
    def new_media_info(*args, **kwargs):
        return MediaInfoDict(*args, **kwargs)

    def _parser(self, media_info):
        if 'info' in media_info:
            return media_info['info']

        elif 'site' in media_info:
            site = media_info['site']
            mid = media_info['mid']
            if site in alias.keys():
                site = alias[site]
            s = import_module('.'.join(['ykdl','extractors',site])).site
            info = s.parser(mid)
 
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
        self._is_list = True
        self.media_info_list = []
        try:
            self.prepare_playlist()
            if not self.media_info_list:
                return

            self.logger.debug('> start at index %d', self.start)
            for i, media in enumerate(self.media_info_list):
                if i < self.start:
                    self.logger.debug('> skip index %d: %r', i, media)
                    continue
                if isinstance(media, MediaInfo):
                    info = media
                else:
                    info = self._parser(media)
                if self.sum != 1:
                    info.index = i + 1, self.sum
                info.orig_url = url
                yield info
        except:
            if not self.media_info_list:
                self.logger.debug(traceback.format_exc())
        finally:
            self.start = -1
            self.end = 'N/A'
            del self._is_list
            if not self.media_info_list:
                raise NotImplementedError(
                    'Playlist is not supported for {self.name} with url: {url}'
                    .format(**vars()))
