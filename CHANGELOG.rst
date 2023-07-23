Change Log for ykdl
===================

1.8.2
-----------

- enable pep517
- change API name from "vid" to "mid", step 1
- add index item to MediaInfo for playlist
- add util.lazy
- fix compatibility with m3u8 3.5.0 (#621) @Joeky
- fix default filename timestamp (#622) @a67878813
- add new extractor: acfun.live
- update GeneralSimple, Bilibili, Douban, DouYin, iQIYI, iXiGua, Huya, Weibo
- move extractor from "le.le" to "le"
- remove Baidu, iXiGua.live


1.8.1.post1
-----------

- fix compatibility bug on Python 3.9 and below (#604)


1.8.1
-----

- add support HTTP cache
- add support interactive mode
- add `--show-all` argument
- improve handling of media title and filename
- bilibili.live API has been changed (#600 @fraic)
- support new sites: iXiGua
- update GeneralSimple, Bilibili, DouYin, YinYueTai


1.8.0
-----

:warning: :warning: :warning: <lots of breaks>

- add Brotli support (extra)
- fix output and update dependencies
- update Bilibili, Douban, Huya, iQIYI, Weibo
- more see early PRE-releases


1.8.0 beta 1
------------

:warning: :warning: :warning: <lots of breaks except CLI>

- code clear and unified code style
- split JSEngine as standalone package
- refactor many core modules, now they become powerful and ease for use
- add support for persistent connection
- add support for crypto M3U
- add support for multi streams in same format, and lower quality fallback
  for `--format`
- remove EOL sites: Bobo, Chushou, Huomao
- fix setup.py bug which wrong pack of wheel
- fixed many bugs
- updated some sites


1.8.0 alpha 2
-------------

- bugfix of alpha 1
- update Douyin, Sina, GeneralSimple
- many improves


1.8.0 alpha 1
-------------

- :warning: <break> update setup interrelated deefef9 10303eb #573
- :warning: <break> change matchall arguments to same as match1 c5229b6
- add new extractor: generalsimple, singlemultimedia e793453
- resolve SSL issues in old OS and package m3u8 1ccfa6b
- fixed dull Ctrl+C fec3a16
- support new sites: Funshion, Heibai #278 #552 thx @airdge
- update Weibo
- remove Xiami


1.7.2
-----

- support new sites: Douyin
- update Huya, Youku, MGTV


1.7.1
-----

- add subtitle support #544
- refactor Weibo
- improved utils html and m3u8
- update Bilibili, Douyu, iQIYI, MGTV, NetEase, PPTV, QQ


1.7.0
-----

- dropped supports of Python 3.4 and below #487
- a lot of improvements with utils #372 a8651a0 #485 d1a6e53 5dfc760 etc.
- extractor class has been changed 641b739 c8c819c
- fixed download name #496
- update AcFun, Bilibili, CCTV/CNTV, Douyu, Huya, iQIYI, JustFun, LeTV, Mango,
  Miaopai, NetEase, PPTV, Qixiu, QQ, Sohu, Weibo, Youku
- remove Dilidili, Panda


1.6.3
-----

- update Sohu, mgtv, sina, etc a lot by @SeaHOH


1.6.2
-----

- update QQ, bilibili, panda a lot by @SeaHOH
- misc updates


1.6.1
-----

- fix youku/tudou, QQ, mgtv, 163, bilibili by @SeaHOH


1.6.0
-----

- new internal proxy for slow video playback. by @SeaHOH
- update youku, many bug fixed.
- update bilibili, new api, playlist bug fixed.
- update HTTP redirection for t.cn
- use cryptodome as default.


1.5.5
-----

- update bilibili bangumi a lot, better
- update youku, support check audio_lang
- update huya, new api
- update acfun, 163 Dj and QQ
- update mpv's default parameters.


1.5.4
-----

- support bilibili bangumi by new extractor
- support new sites: Zhangyu, Chushou
- update QQ, important!! by @SeaHOH
- update Youku, Tudou, not finished.
- update Huomao, douyu, iqiyi
- update sohu and mpv wrapper, thanks to @SeaHOH


1.5.3
-----

- update bilibili, tudou, weibo, etc.
- update mpv wrapper, thanks to @SeaHOH


1.5.2
-----

- update youku, panda, le, zhanqi, longzhu, laifeng, huajiao, etc.
- many updates for windows platform, thanks to @SeaHOH
- README.rst updated.


1.5.1
-----

- update bilibili, youku, quanmin live, 163, douyu, etc.
- support egame.qq.com, finance.le.com
- update player wrapper
- -F/--format now accept int value as level of resolution.


1.5.0
-----

- update videoinfo, add ua/referrer.
- update douyu, bilibili, youku
- cykdl support no proxy


1.4.11
------

- update 163 music, pptv, youku
- update python2 support
- update ffmpeg&mpv wrapper


1.4.10
------

- support new sites: sina open course
- delete: isuntv, instagram, dailymotion, alive, ted
- update bilibili, acfun, sohu, youku, tudou
- update downloader


1.4.9
-----

- support new sites: dilidili
- update letv, youku
- update downloader


1.4.8
-----

- support new sites: ifeng/163 open course
- update QQ, acfun, weibo, ifeng
- update youku, due to api changed
- misc changes


1.4.7
-----

- fix bug when len(urls) == 1
- update mgtv, huomao, bilibili
- restructure ykdl, using setuptools
- misc changes


1.4.6
-----

- acfun: add missing sign
- python2 fix
- using ThreadPoolExecutor for multithread download
- rename short opt for json out to capital J
- add -j --jobs for multithread download jobs number, default is NR_CPUS


1.4.5
-----

- fix iqiyi with code clean
- update bilibili Episode title
- update douyu live room name
- use yield to speedup playlist
- python2 fix


1.4.4
-----

- fix Acfun again
- fix douyu live
- support multithread download, NOTE: this is not finished


1.4.3
-----

- fix Acfun
- fix letv


1.4.2
-----

- change version string to 3 digital
- fix qq, douyu, mgtv, QQ. etc.
- report stream_types in json


1.1.4.1
-------

- fix letv live, cctv, xiami, QQ
- support douyu video, kankannews, Quanmin Live
- update common alias dict


1.1.4
-----

- port PPTV, yizhibo from upstream/PL
- update Bilibili.
- partially support Taobao 


1.1.3.6
-------

- update bilibili playlist.
- update ACfun.
- support youku mp5


1.1.3.5
-------

- update bilibili for eid and title.
- update ACfun for match pattern, and playlist
- update main script to fix bugs, add -O option
- add warning in m3u8_wrapper


1.1.3.4
-------

- update bilibili, ACfun
- update setup script, test makefile


1.1.3.3
-------

- update douyu, QQ, generalembed


1.1.3.2
-------

- update Acfun, huomao, youku
- add gitter


1.1.3.1
-------

- update generalembed, le live, douyu, zhanqi


1.1.3
-----

- update iqiyi
- merge option removed
- get proxy from system proxy settings
- some other update


1.1.2
-----

- refact code a lot
- update iqiyi
- update setup for windows platform


1.1.1.2
-------

- quick fix for youku, find a mistake


1.1.1.1
-------

- update iqiyi support more stream profiles
- update m3u8 download with ffpmeg
- update letv 
- update stream profile code


1.1.1
-----

- fix iqiyi, QQ
- support huajiao live
- remove lots of dead sites, include youtube
- many other updates


1.1.0.4
-------

- update README.rst, CHANGELOG.rst
- support laifeng live
- fix zhanqi
- add travis-ci


1.1.0.3
-------

- misc changes on setup, code refactor


1.1.0.2
-------

- right way to add requirements


1.1.0
-----

- add experimental merge feature.
- video titles are changed for many sites.
- longzhu live is improved.
- live video authors are added when possible.
- subtitle feature is planned but moved to danmu branch.


1.0.9.2
-------

- bug fix for baomihua
- add test for extractors status.


1.0.9.1
-------

- fix unqoute issue in python2, since v1.0.9 is released
- a draft binary release is done. feedback is welcome.


1.0.9
-----

- new sites are supported

    1. huya live and video
    2. longzhu live

- python2 are supported

    almost done

    big change
