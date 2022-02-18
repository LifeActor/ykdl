import sys
import json
import random
import logging
from collections import defaultdict
from datetime import datetime
from html import unescape
from urllib.parse import unquote

from .util import log
from .util.fs import legitimize
from .util.human import human_size, _format_time, human_time, stream_index
from .util.match import match, match1
from .util.wrap import get_random_str

logger = logging.getLogger(__name__)


class MediaInfo:
    def __init__(self, site, live=False):
        self.site = site
        self.live = live
        self.orig_url = None
        self._title = None
        self._album = None
        self._artist = None
        self._duration = None
        self._comments = []
        self.streams = MediaStreams()
        self.subtitles = []
        self.extra = {k: '' for k in ['ua',
                                      'referer',
                                      'header',
                                      'proxy',
                                      'rangefetch'
                                     ]}

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        if value:
            self._title = unquote(unescape(value))

    @property
    def album(self):
        return self._album

    @album.setter
    def album(self, value):
        if value:
            self._album = unquote(unescape(value))

    @property
    def artist(self):
        return self._artist

    @artist.setter
    def artist(self, value):
        if value:
            self._artist = unquote(unescape(value))

    @property
    def duration(self):
        return self._duration

    @duration.setter
    def duration(self, value):
        if isinstance(value, str):
            value = _format_time(value)
        if isinstance(value, (int, float)) and value > 0:
            self._duration = int(value)

    @property
    def comments(self):
        return ', '.join(self._comments)

    def add_comment(self, value):
        if value:
            value = unquote(unescape(value))
            self._comments.append(value)

    def print_stream_info(self, stream_id, show_all=False):
        stream = self.streams[stream_id]
        fmt, id = self.streams._split_id(stream_id)
        stream_fmt = id and self.streams[fmt] is stream and fmt
        size = stream.get('size', 0) not in (0, float('inf')) and stream['size']
        self.lprint(
        ['    - format:         {}', (stream_fmt and
                                      log.sprint(stream_fmt, log.NEGATIVE) + ' '
                                      or '')
                                   + log.sprint(stream_id, log.NEGATIVE)],
        ['      container:      {}', stream.get('container')],
        ['      video-profile:  {}', stream.get('video_profile')],
        ['      quality:        {}', stream.get('quality')],
        ['      size:           {} ({:d} Bytes)', size and human_size(size), size],
        ['    # download-with:  {}', stream_id != 'current' and
                log.sprint('ykdl --format=%s [URL]' % stream_id, log.UNDERLINE)])
        if show_all:
            print('Real urls:')
            for url in stream['src']:
                print(url)

    def print_subtitle_info(self, subtitle, show_all=False):
        size = subtitle.get('size', 0) not in (0, float('inf')) and subtitle['size']
        self.lprint(
        ['    - language:       {}', log.sprint(subtitle['lang'], log.NEGATIVE)],
        ['      name:           {}', subtitle['name']],
        ['      format:         {}', subtitle['format']],
        ['      size:           {} ({:d} Bytes)', size and human_size(size), size])
        if show_all:
            print('Real url:')
            print(subtitle['src'])

    def jsonlize(self):
        json_dict = {
            'site'          : self.site,
            'title'         : self.title,
            'album'         : self.album,
            'artist'        : self.artist,
            'duration'      : self.duration,
            'comments'      : self.comments,
            'streams'       : dict(self.streams.items()),
            'subtitles'     : self.subtitles,
            'extra'         : self.extra,
        }
        for s in json_dict['streams']:
            if json_dict['streams'][s].get('size') == float('inf'):
                json_dict['streams'][s].pop('size')
        return json_dict

    def print_info(self, stream_id=None, show_all=False):
        self.lprint(
        ['site:                 {}', self.site],
        ['title:                {}', self.title],
        ['album:                {}', self.album],
        ['artist:               {}', self.artist],
        ['duration:             {}', self.duration and human_time(self.duration)],
        ['comments:             {}', self.comments],
        ['streams:', 1])
        if not show_all:
            stream_id = stream_id or self.streams.get_id(0)
            self.print_stream_info(stream_id, show_all)
        else:
            for stream_id in self.streams:
                self.print_stream_info(stream_id, show_all)
        if self.subtitles:
            print('subtitles:')
            for subtitle in self.subtitles:
                self.print_subtitle_info(subtitle, show_all)

    def build_file_name(self, stream_id):
        unique_title = []
        if self.title:
            unique_title.append(self.title)
            if self.album and self.album not in self.title:
                unique_title.append(self.album)
            if self.artist and self.artist not in self.title:
                unique_title.append(self.artist)
        else:
            unique_title += [self.site, get_random_str(8)]
        if not stream_id == 'current':
            unique_title.append(stream_id)
        if self.live:
            unique_title.append(datetime.now().isoformat().split('.')[0])
        return legitimize('_'.join(unique_title))

    @staticmethod
    def lprint(*ll):
        for l, *v in ll:
            if v[0]:
                print(l.format(*v))


class MediaStreams:
    def __init__(self):
        self._streams = {}
        self._streamids = []
        self._formats = defaultdict(lambda: 0)
        self._sorted = False

    def __len__(self):
        return len(self._streamids)

    def __getitem__(self, name):
        if isinstance(name, int):
            return self._streams[self._streamids[name][1:]]
        value = self.get(name)
        if value is None:
            raise KeyError(name)
        return value

    def __setitem__(self, name, value):
        self.set(name, value)

    def __delitem__(self, name):
        hit, _, i = self._index(name)
        while hit:
            del self._streams[self._streamids[i][1:]]
            del self._streamids[i]
            hit, _, i = self._index(name)

    def __contains__(self, name):
        hit, *_ = self._index(name)
        return hit

    def __str__(self):
        return str(dict(self.items()))

    def __iter__(self):
        for k in self.keys():
            yield k

    def keys(self):
        return [self.get_id(i) for i in range(len(self))]

    def values(self):
        self.check_index()
        return [self._streams[id[1:]] for id in self._streamids]

    def items(self):
        return list(zip(self.keys(), self.values()))

    def get(self, name, failobj=None):
        hit, fallback, i = self._index(name)
        if hit or fallback:
            return self._streams[self._streamids[i][1:]]
        return failobj

    def set(self, name, value):
        fmt, id = self._split_id(name)
        if not id:
            id = str(self._formats[fmt])
        if (fmt, id) in self._streams:
            raise KeyError(name)
        self._streamids.append((stream_index(fmt), fmt, id))
        self._streams[(fmt, id)] = value
        self._formats[fmt] += 1
        self._sorted = False

    def check_index(self):
        if not self._sorted:
            self.sort()

    def sort(self):
        if len(self) > 1:
            self._streamids.sort(key=self._sort_key)
        self._sorted = True

    @staticmethod
    def _sort_key(ids):
        i, _, id = ids
        if 'H265' in id:  # raise, the size of h265 file is smaller than others
            id = '0' + id
        return i, id

    @staticmethod
    def _split_id(name):
        fmt, _, id = name.replace('_', '-').partition('-')
        return fmt, id.upper()

    def _index(self, name):
        self.check_index()
        fmt, id = self._split_id(name)
        fmt_id = fmt, id or '0'
        idx = 0
        idx_fmt = None
        hit = fallback = False
        i = stream_index(fmt)
        for _i, _fmt, _id in self._streamids:
            if not id and idx_fmt is None and _i == i:
                idx_fmt = idx
            if _i > i:
                fallback = idx_fmt is None
                break
            if (_fmt, _id) == fmt_id:
                hit = True
                break
            idx += 1
        if not (hit or fallback) and idx_fmt is not None:
            idx = idx_fmt
            hit = True
        return hit, fallback, idx

    def index(self, name):
        '''Index name, no Error, a lower or the highest(0) are fallback.'''
        hit, fallback, i = self._index(name)
        i = (hit or fallback) and i or 0
        if not hit:
            fb = self.get_id(i)
            if fb != 'current':
                logger.info('The fallback %r has applied to %r', fb, name)
        return i

    def get_id(self, i):
        '''Get the name of index.'''
        self.check_index()
        _, fmt, id = self._streamids[i]
        if id == '0':
            return fmt
        else:
            return '-'.join((fmt, id))

