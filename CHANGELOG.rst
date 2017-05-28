Change Log for ykdl
===================

1.4.10
-------

- support new sites: sina open course
- delete: isuntv, instagram, dailymotion, alive, ted
- update bilibili, acfun, sohu, youku, tudou
- update downloader

1.4.9
-------

- support new sites: dilidili
- update letv, youku
- update downloader

1.4.8
-------

- support new sites: ifeng/163 open course
- update QQ, acfun, weibo, ifeng
- update youku, due to api changed
- misc changes

1.4.7
-------

- fix bug when len(urls) == 1
- update mgtv, huomao, bilibili
- restructure ykdl, using setuptools
- misc changes


1.4.6
-------

- acfun: add missing sign
- python2 fix
- using ThreadPoolExecutor for multithread download
- rename short opt for json out to capital J
- add -j --jobs for multithread download jobs number, default is NR_CPUS

1.4.5
-------

- fix iqiyi with code clean
- update bilibili Episode title
- update douyu live room name
- use yield to speedup playlist
- python2 fix


1.4.4
-------

- fix Acfun again
- fix douyu live
- support multithread download, NOTE: this is not finished

1.4.3
-------

- fix Acfun
- fix letv

1.4.2
-------

- change version string to 3 digital
- fix qq, douyu, mgtv, QQ. etc.
- report stream_types in json


1.1.4.1
-------

- fix letv live, cctv, xiami, QQ
- support douyu video, kankannews, Quanmin Live
- update common alias dict

1.1.4
-------

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
-------

- update iqiyi
- merge option removed
- get proxy from system proxy settings
- some other update

1.1.2
-------

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

python3 is first choice, if you don't have python3, python2 is fine.
don't forget to file a bug when using python2
