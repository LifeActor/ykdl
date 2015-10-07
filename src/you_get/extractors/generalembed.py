__all__ = ['embed_download']

from ..common import *
from ..embedextractor import EmbedExtractor

"""
refer to http://open.youku.com/tools
"""
youku_embed_patterns = [ 'youku\.com/v_show/id_([a-zA-Z0-9=]+)',
                         'player\.youku\.com/player\.php/sid/([a-zA-Z0-9=]+)/v\.swf',
                         'loader\.swf\?VideoIDS=([a-zA-Z0-9=]+)',
                         'player\.youku\.com/embed/([a-zA-Z0-9=]+)',
                         'YKU.Player\(\'[a-zA-Z0-9]+\',{ client_id: \'[a-zA-Z0-9]+\', vid: \'([a-zA-Z0-9]+)\''
                       ]

"""
http://www.tudou.com/programs/view/html5embed.action?type=0&amp;code=3LS_URGvl54&amp;lcode=&amp;resourceId=0_06_05_99
http://www.tudou.com/v/voahn6inu8k/&resourceId=402221676_04_02_99/v.swf
"""
tudou_embed_patterns = [ 'tudou\.com[a-zA-Z0-9\/\?=\&\.\;]+code=([^&]+)',
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
                      'v\.qq\.com[a-zA-Z0-9\/\?\.\;]+\/([a-zA-Z0-9]+)\.html',
                      'TPout\.swf\?\&vid=([a-zA-Z0-9]+)'
                    ]


"""
tv.sohu.com
"""
sohu_embed_patterns = [ 'tv\.sohu\.com[a-zA-Z0-9\/\?=]+\&vid=([a-zA-Z0-9]+)\&',
                        'share\.vrs\.sohu\.com\/my\/v.swf[&+=a-zA-z0-9]+&id=([^&]+)',
                        'my\.tv\.sohu\.com\/[a-zA-Z0-9\/]+/([^\.]+)'
                      ]

"""
Youtube
"""
youtube_embed_patterns = [ 'youtu\.be/([^\"]+)',
                           'youtube\.com/embed/([^\"]+)',
                           'youtube\.com/v/([^\"]+)'
                         ]

"""
Ku6
"""
ku6_embed_url = [ '(http://v.ku6vms.com/[^\"]+)'
                     ]


class GeneralEmbed(EmbedExtractor):

    def prepare(self, **kwargs):
        assert self.url
        found = False
        content = get_content(self.url)
        self.title = match1(content, '<title>([^<>]+)</title>')

        vids = matchall(content, youku_embed_patterns)
        for vid in vids:
            found =True
            self.video_info.append(('youku',vid))

        vids = matchall(content, tudou_embed_patterns)
        for vid in vids:
            found = True
            new_url = get_location("http://tudou.com/v/"+vid)
            iid = match1(new_url, 'iid=([^&]+)')
            self.video_info.append(('tudou',iid))

        vids = matchall(content, qq_embed_patterns)
        for vid in vids:
            found = True
            self.video_info.append(('qq',vid))

        vids = matchall(content, sohu_embed_patterns)
        for vid in vids:
            found = True
            self.video_info.append(('sohu',vid))

        vids = matchall(content, youtube_embed_patterns)
        for vid in vids:
            found = True
            self.video_info.append(('youtube',vid))

        urls = matchall(content, ku6_embed_url)
        for url in urls:
            found = True
            html = get_content(url)
            flashvars = matchall(html, ['vid=([^&]+)', 'style=([^&]+)', 'sn=([^&]+)'])
            data = json.loads(get_content('http://v.ku6vms.com/phpvms/player/forplayer/vid/{}/style/{}/sn/{}'.format(flashvars[0], flashvars[1],flashvars[2])))
            vid = data['ku6vid']
            self.video_info.append(('ku6',vid))

        tmp = []
        for v in self.video_info:
            if not v in tmp:
                tmp.append(v)
        self.video_info = tmp

site = GeneralEmbed()
download = site.download
download_playlist = playlist_not_supported('any.any')
