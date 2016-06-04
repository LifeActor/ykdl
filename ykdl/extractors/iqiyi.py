#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..util.html import get_content
from ..util.match import matchall, match1
from ..extractor import VideoExtractor

from uuid import uuid4
from random import random,randint
import json
from math import floor
import hashlib

from ykdl.compact import compact_bytes

'''
Changelog:
-> http://www.iqiyi.com/common/flashplayer/20150916/MainPlayer_5_2_28_c3_3_7_4.swf
   use @fffonion 's method in #617.
   Add trace AVM(asasm) code in Iqiyi's encode function where the salt is put into the encode array and reassemble by RABCDasm(or WinRABCDasm),then use Fiddler to response modified file to replace the src file with its AutoResponder function ,set browser Fiddler proxy and play with !debug version! Flash Player ,finially get result in flashlog.txt(its location can be easily found in search engine).
   Code Like (without letters after #comment:),it just do the job : trace("{IQIYI_SALT}:"+salt_array.join(""))
   ```(Postion After getTimer)
     findpropstrict      QName(PackageNamespace(""), "trace")
     pushstring          "{IQIYI_SALT}:" #comment for you to locate the salt
     getscopeobject      1
     getslot             17 #comment: 17 is the salt slots number defined in code
     pushstring          ""
     callproperty        QName(Namespace("http://adobe.com/AS3/2006/builtin"), "join"), 1
     add
     callpropvoid        QName(PackageNamespace(""), "trace"), 1
   ```

-> http://www.iqiyi.com/common/flashplayer/20150820/MainPlayer_5_2_27_2_c3_3_7_3.swf
    some small changes in Zombie.bite function

'''

'''
com.qiyi.player.core.model.def.DefinitonEnum
bid meaning for quality
0 none
1 standard
2 high
3 super
4 suprt-high
5 fullhd
10 4k
96 topspeed

'''
def mix(tvid):
    salt = '4a1caba4b4465345366f28da7c117d20'
    tm = str(randint(2000,4000))
    sc = hashlib.new('md5', compact_bytes(salt + tm + tvid, 'utf-8')).hexdigest()
    return tm, sc, 'eknas'

def getVRSXORCode(arg1,arg2):
    loc3=arg2 %3
    if loc3 == 1:
        return arg1^121
    if loc3 == 2:
        return arg1^72
    return arg1^103


def getVrsEncodeCode(vlink):
    loc6=0
    loc2=''
    loc3=vlink.split("-")
    loc4=len(loc3)
    # loc5=loc4-1
    for i in range(loc4-1,-1,-1):
        loc6=getVRSXORCode(int(loc3[loc4-i-1],16),i)
        loc2+=chr(loc6)
    return loc2[::-1]

def getDispathKey(rid):
    tp=")(*&^flash@#$%a"  #magic from swf
    time=json.loads(get_content("http://data.video.qiyi.com/t?tn="+str(random())))["t"]
    t=str(int(floor(int(time)/(10*60.0))))
    return hashlib.new("md5",compact_bytes(t+tp+rid,"utf-8")).hexdigest()

class Iqiyi(VideoExtractor):
    name = u"爱奇艺 (Iqiyi)"

    supported_stream_types = [ '4k', 'fullhd', 'suprt-high', 'super', 'high', 'standard', 'topspeed' ]

    stream_to_bid = {  '4k': 10, 'fullhd' : 5, 'suprt-high' : 4, 'super' : 3, 'high' : 2, 'standard' :1, 'topspeed' :96}

    stream_urls = {  '4k': [] , 'fullhd' : [], 'suprt-high' : [], 'super' : [], 'high' : [], 'standard' :[], 'topspeed' :[]}

    baseurl = ''

    gen_uid = ''

    def __init__(self):
        VideoExtractor.__init__(self)
        self.iterable = True


    def getVMS(self):
        #tm ->the flash run time for md5 usage
        #um -> vip 1 normal 0
        #authkey -> for password protected video ,replace '' with your password
        #puid user.passportid may empty?
        #TODO: support password protected video
        tvid, vid = self.vid
        tm, sc, src = mix(tvid)
        uid = self.gen_uid
        vmsreq='http://cache.video.qiyi.com/vms?key=fvip&src=1702633101b340d8917a69cf8a4b8c7' +\
                "&tvId="+tvid+"&vid="+vid+"&vinfo=1&tm="+tm+\
                "&enc="+sc+\
                "&qyid="+uid+"&tn="+str(random()) +"&um=1" +\
                "&authkey="+hashlib.new('md5',compact_bytes(hashlib.new('md5', b'').hexdigest()+str(tm)+tvid,'utf-8')).hexdigest()
        return json.loads(get_content(vmsreq))



    def prepare(self):

        if self.url and not self.vid:
            vid = matchall(self.url, ['curid=([^_]+)_([\w]+)'])
            if vid:
                self.vid = vid[0]

        if self.url and not self.vid:
            html = get_content(self.url)
            tvid = match1(html, 'data-player-tvid="([^"]+)"') or match1(self.url, 'tvid=([^&]+)')
            videoid = match1(html, 'data-player-videoid="([^"]+)"') or match1(self.url, 'vid=([^&]+)')
            self.vid = (tvid, videoid)

        self.gen_uid=uuid4().hex
        info = self.getVMS()

        assert info["code"] == "A000000", "[error] outdated iQIYI key\nis your ykdl up-to-date?"


        self.title = info["data"]["vi"]["vn"]

        # data.vp = json.data.vp
        #  data.vi = json.data.vi
        #  data.f4v = json.data.f4v
        # if movieIsMember data.vp = json.data.np

        #for highest qualities
        #for http://www.iqiyi.com/v_19rrmmz5yw.html  not vp -> np
        assert info["data"]['vp']["tkl"], "[Error] Do not support for iQIYI VIP video."

        vs = info["data"]["vp"]["tkl"][0]["vs"]
        self.baseurl=info["data"]["vp"]["du"].split("/")

        for stream in self.supported_stream_types:
            for i in vs:
                if self.stream_to_bid[stream] == i['bid']:
                    video_links=i["fs"] #now in i["flvs"] not in i["fs"]
                    if not i["fs"][0]["l"].startswith("/"):
                        tmp = getVrsEncodeCode(i["fs"][0]["l"])
                        if tmp.endswith('mp4'):
                             video_links = i["flvs"]
                    self.stream_urls[stream] = video_links
                    size = 0
                    for l in video_links:
                        size += l['b']
                    self.streams[stream] = {'container': 'f4v', 'video_profile': stream, 'size' : size}
                    self.stream_types.append(stream)
                    break

    def extract_iter(self):
        stream_id = self.param.format or self.stream_types[0]

        urls=[]
        for i in self.stream_urls[stream_id]:
            vlink=i["l"]
            if not vlink.startswith("/"):
                #vlink is encode
                vlink=getVrsEncodeCode(vlink)
            key=getDispathKey(vlink.split("/")[-1].split(".")[0])
            baseurl = [x for x in self.baseurl]
            baseurl.insert(-1,key)
            url="/".join(baseurl)+vlink+'?su='+self.gen_uid+'&qyid='+uuid4().hex+'&client=&z=&bt=&ct=&tn='+str(randint(10000,20000))
            yield json.loads(get_content(url))["l"]

    def download_playlist(self, url, param):
        self.url = url

        html = get_content(self.url)

        vids = matchall(html, ['data-tvid=\"([^\"]+)\" data-vid=\"([^\"]+)\"'])
        for v in vids:
            self.download(v, param)


site = Iqiyi()
