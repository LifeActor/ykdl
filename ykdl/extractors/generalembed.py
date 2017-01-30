#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..util.html import get_content, get_location
from ..util.match import matchall, match1
from ..embedextractor import EmbedExtractor

import json

"""
refer to http://open.youku.com/tools
"""
youku_embed_patterns = [ 'youku\.com/v_show/id_([a-zA-Z0-9=]+)',
                         'player\.youku\.com/player\.php/sid/([a-zA-Z0-9=]+)/v\.swf',
                         'loader\.swf\?VideoIDS=([a-zA-Z0-9=]+)',
                         'player\.youku\.com/embed/([a-zA-Z0-9=]+)',
                         'YKU.Player\(\'[a-zA-Z0-9]+\',{ client_id: \'[a-zA-Z0-9]+\', vid: \'([a-zA-Z0-9]+)\'',
                         'vid: \'([a-zA-Z0-9=]+)\',',
                         'data-youku=\"[a-zA-Z0-9,:]+vid:([a-zA-Z0-9=]+)\"'
                       ]

"""
http://www.tudou.com/programs/view/html5embed.action?type=0&amp;code=3LS_URGvl54&amp;lcode=&amp;resourceId=0_06_05_99
http://www.tudou.com/v/voahn6inu8k/&resourceId=402221676_04_02_99/v.swf
"""
tudou_embed_patterns = [ 'tudou\.com[a-zA-Z0-9\/\?=\&\.\;\#]+code=([^&]+)',
                         'tudou\.com\/[a-zA-Z]\/([^\/]+)'
                       ]

"""
refer to http://open.tudou.com/wiki/video/info
"""
tudou_api_patterns = [ ]


"""
v.qq.com
"""
qq_embed_patterns = [ 'v\.qq\.com[a-zA-Z0-9\/\?\.\;]+vid=([a-zA-Z0-9]+)',
                      'TPout\.swf[a-zA-Z0-9=\?\&_]+vid=([a-zA-Z0-9]+)'
                    ]


"""
tv.sohu.com
"""
sohu_embed_patterns = [ 'tv\.sohu\.com[a-zA-Z0-9\/\?=]+\&vid=([a-zA-Z0-9]+)\&',
                        'share\.vrs\.sohu\.com\/my\/v.swf[&+=a-zA-z0-9]+&id=([^&]+)',
                        'my\.tv\.sohu\.com\/[a-zA-Z0-9\/]+/([^\.]+)'
                      ]

"""
Ku6
"""
ku6_embed_url = [ '(http://v.ku6vms.com/[^\"]+)'
                     ]

ku6_embed_patterns = [ 'http://player.ku6.com/refer/(.*)/v.swf'
                     ]
"""
163
"""
netease_embed_patterns = [ 'v\.163\.com\/[0-9a-zA-Z\/\?\.]+topicid=([^&]+)&amp\;vid=([^&]+)',
                           'topicid=([a-zA-Z0-9]+)&amp;vid=([a-zA-Z0-9]+)&amp'
                     ]

"""
iqiyi
"""
iqiyi_embed_patterns = [ 'definitionID=([^&]+)&tvId=([^&]+)'
                     ]

"""
Letv Cloud
"""
lecloud_embed_patterns = [ '{"uu":"([^\"]+)","vu":"([^\"]+)"',
                           'bcloud.swf\?uu=([^&]+)&amp;vu=([^&]+)'
                     ]

"""
ifeng
"""
ifeng_embed_patterns = [ 'v\.ifeng\.com\/[a-zA-Z\=\/\?\&\.]+guid=([^\"]+)'
                     ]

"""
weibo
"""
weibo_embed_patterns = [ 'http://video.weibo.com/player/1034:(\w{32})\w*'
                     ]

"""
Sina
"""
sina_embed_patterns = [ 'http://video.sina.com.cn/share/video/(\d+).swf'
                     ]




class GeneralEmbed(EmbedExtractor):
    name = u"GeneralEmbed (通用嵌入视频)"

    def prepare_playlist(self):
        content = get_content(self.url)

        vids = matchall(content, youku_embed_patterns)
        for vid in vids:
            self.video_info_list.append(('youku',vid))

        vids = matchall(content, tudou_embed_patterns)
        for vid in vids:
            new_url = get_location("http://tudou.com/v/"+vid)
            iid = match1(new_url, 'iid=([^&]+)')
            self.video_info_list.append(('tdorig',iid))

        vids = matchall(content, qq_embed_patterns)
        for vid in vids:
            self.video_info_list.append(('qq.video',vid))

        vids = matchall(content, sohu_embed_patterns)
        for vid in vids:
            self.video_info_list.append(('sohu.my',vid))

        urls = matchall(content, ku6_embed_url)
        for url in urls:
            html = get_content(url)
            flashvars = matchall(html, ['vid=([^&]+)', 'style=([^&]+)', 'sn=([^&]+)'])
            data = json.loads(get_content('http://v.ku6vms.com/phpvms/player/forplayer/vid/{}/style/{}/sn/{}'.format(flashvars[0], flashvars[1],flashvars[2])))
            vid = data['ku6vid']
            self.video_info_list.append(('ku6',vid))
        vids = matchall(content, ku6_embed_patterns)
        for v in vids:
            self.video_info_list.append(('ku6', v))
        vids = matchall(content, netease_embed_patterns)
        for v in vids:
            self.video_info_list.append(('netease.video', v))

        vids = matchall(content, iqiyi_embed_patterns)
        for v in vids:
            videoid, tvid = v
            self.video_info_list.append(('iqiyi', (tvid, videoid)))

        vids = matchall(content, lecloud_embed_patterns)
        for v in vids:
            uu, vu = v
            self.video_info_list.append(('le.letvcloud', (vu, uu)))

        vids = matchall(content, ifeng_embed_patterns)
        for v in vids:
            v  = v.split('&')[0]
            self.video_info_list.append(('ifeng', v))

        vids = matchall(content, weibo_embed_patterns)
        for v in vids:
            self.video_info_list.append(('weibo','http://weibo.com/p/' + v))

        vids = matchall(content, sina_embed_patterns)
        for v in vids:
            v  = v.split('&')[0]
            self.video_info_list.append(('sina', v))

        tmp = []
        for v in self.video_info_list:
            if not v in tmp:
                tmp.append(v)
        self.video_info_list = tmp

    parser = EmbedExtractor.parser_list

site = GeneralEmbed()
