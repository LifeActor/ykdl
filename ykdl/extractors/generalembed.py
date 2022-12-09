# -*- coding: utf-8 -*-

from ._common import *


'''
refer to http://open.youku.com/tools
'''
youku_embed_patterns = [
    'youku\.com/v_show/id_([a-zA-Z0-9=]+)',
    'player\.youku\.com/player\.php/sid/([a-zA-Z0-9=]+)/v\.swf',
    'loader\.swf\?VideoIDS=([a-zA-Z0-9=]+)',
    'player\.youku\.com/embed/([a-zA-Z0-9=]+)',
    'YKU.Player\(\'[a-zA-Z0-9]+\',{ client_id: \'[a-zA-Z0-9]+\', vid: \'([a-zA-Z0-9]+)\'',
    'data-youku=\"[a-zA-Z0-9,:]+vid:([a-zA-Z0-9=]+)\"'
]

'''
v.qq.com
'''
qq_embed_patterns = [
    'v\.qq\.com[a-zA-Z0-9\/\?\.\;]+vid=([a-zA-Z0-9]+)',
    'TPout\.swf[a-zA-Z0-9=\?\&_]+vid=([a-zA-Z0-9]+)'
]


'''
tv.sohu.com
'''
sohu_embed_patterns = [
    'tv\.sohu\.com[a-zA-Z0-9\/\?=]+\&vid=([a-zA-Z0-9]+)\&',
    'share\.vrs\.sohu\.com\/my\/v.swf[&+=a-zA-z0-9]+&id=(\d+)',
    'my\.tv\.sohu\.com\/[a-zA-Z0-9\/]+/(\d+)'
]

'''
Ku6
'''
ku6_embed_url = [
    '(http://v.ku6vms.com/[^\"]+)'
]

ku6_embed_patterns = [
    'http://player.ku6.com/refer/(.*)/v.swf'
]
'''
163
'''
netease_embed_patterns = [
    'v\.163\.com\/[0-9a-zA-Z\/\?\.]+topicid=([^&]+)&amp\;vid=([^&]+)',
    'topicid=([a-zA-Z0-9]+)&amp;vid=([a-zA-Z0-9]+)&amp'
]

'''
iqiyi
'''
iqiyi_embed_patterns = [
    'definitionID=([^&]+)&tvId=([^&]+)'
]

'''
Letv Cloud
'''
lecloud_embed_patterns = [
    '{"uu":"([^\"]+)","vu":"([^\"]+)"',
    'bcloud.swf\?uu=([^&]+)&amp;vu=([^&]+)',
    'uu=([^&]+)&amp;vu=([^&]+)'
]

'''
ifeng
'''
ifeng_embed_patterns = [
    'v\.ifeng\.com\/[a-zA-Z\=\/\?\&\.]+guid=([^\"&]+)'
]

'''
weibo
'''
weibo_embed_patterns = [
    'http://video.weibo.com/player/1034:(\w{32})\w*'
]

'''
Sina
'''
sina_embed_patterns = [
    'http://video.sina.com.cn/share/video/(\d+).swf'
]

'''
Bilibili
'''
bilibili_embed_patterns = [
    'flashvars="aid=(\d+)'
]

class GeneralEmbed(EmbedExtractor):
    name = 'GeneralEmbed (通用嵌入视频)'

    def prepare_playlist(self):

        def append_media_info(site, mid):
            media_info = self.new_media_info({
                'site': site,
                'mid': mid
            })
            if media_info not in self.media_info_list:
                self.media_info_list.append(media_info)

        html = get_content(self.url)

        for mid in matchall(html, *youku_embed_patterns):
            append_media_info('youku', mid)

        for mid in matchall(html, *qq_embed_patterns):
            append_media_info('qq.video', mid)

        for mid in matchall(html, *sohu_embed_patterns):
            append_media_info('sohu.my', mid)

        for url in matchall(html, *ku6_embed_url):
            flashvars = matchall(get_content(url),'vid=([^&]+)',
                                                  'style=([^&]+)',
                                                  'sn=([^&]+)')
            data = get_response(
                    'http://v.ku6vms.com/phpvms/player/forplayer/vid/'
                    '{}/style/{}/sn/{}'
                    .format(*flashvars)).json()
            mid = data['ku6vid']
            append_media_info('ku6', mid)

        for mid in matchall(html, *ku6_embed_patterns):
            append_media_info('ku6', mid)

        for mid in matchall(html, *netease_embed_patterns):
            append_media_info('netease.video', mid)

        for mid in matchall(html, *iqiyi_embed_patterns):
            append_media_info('iqiyi', mid)

        for mid in matchall(html, *lecloud_embed_patterns):
            append_media_info('le.letvcloud', mid)

        for mid in matchall(html, *ifeng_embed_patterns):
            append_media_info('ifeng.news', mid)

        for mid in matchall(html, *weibo_embed_patterns):
            append_media_info('weibo', 'http://weibo.com/p/' + mid)

        for mid in matchall(html, *sina_embed_patterns):
            append_media_info('sina.video', mid)

        for mid in matchall(html, *bilibili_embed_patterns):
            append_media_info('bilibili.video', mid)

    parser = EmbedExtractor.parser_list

site = GeneralEmbed()
