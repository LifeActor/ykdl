#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..util.html import *
from ..util.match import *
from ..extractor import VideoExtractor

class Veoh(VideoExtractor):

    name = 'Veoh'

    def prepare(self):

        if not self.vid:
            self.vid = match1(self.url, 'http://www.veoh.com/watch/(\w+)', 'http://www.veoh.com/m/watch.php\?v=(\w+)')

        assert self.vid, 'Cannot find item ID'

        webpage_url = 'http://www.veoh.com/m/watch.php?v={}&quality=1'.format(self.vid)

        #grab download URL
        a = get_content(webpage_url)
        url = match1(a, r'<source src="(.*?)\"\W')
    
        #grab title
        self.title = match1(a, r'<meta property="og:title" content="([^"]*)"')

        type_, ext, size = url_info(url)

        self.stream_types.append('current')
        self.streams['current'] = {'container': ext, 'src': [url], 'size' : size}


site = Veoh()
