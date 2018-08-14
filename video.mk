test_video1: test_youku test_acfun test_bilibili test_ifeng test_163m test_sohutv test_cctv test_tudou
test_video2: test_iqilu test_iqiyi test_joy test_ku6 test_kuwo test_sina test_qq test_sohumy test_baomihua
test_video3: test_xiami test_yinyuetai test_baidu test_douban test_huya test_163v test_le test_mgtv

PYTHON ?= python3

test_youku:
	${PYTHON} -m cykdl -i http://v.youku.com/v_show/id_XMTYwMDIxNDI2MA==.html

test_acfun:
	${PYTHON} -m cykdl -i http://www.acfun.cn/v/ac213736

test_bilibili:
	${PYTHON} -m cykdl -i http://bangumi.bilibili.com/anime/2539/play#63470

test_baomihua:
	${PYTHON} -m cykdl -i http://www.baomihua.com/user/24204_36300935

test_cctv:
	${PYTHON} -m cykdl -i http://tv.cctv.com/2016/06/08/VIDEa0Y5V5HY9MLeoVM5tcQC160608.shtml -t 300

test_ifeng:
	${PYTHON} -m cykdl -i http://v.ifeng.com/video_8632601.shtml

test_iqilu:
	${PYTHON} -m cykdl -i http://v.iqilu.com/shpd/rmxf/2016/0607/4332820.html

test_iqiyi:
	${PYTHON} -m cykdl -i http://www.iqiyi.com/v_19rrle48gg.html

test_joy:
	${PYTHON} -m cykdl -i http://www.joy.cn/video?resourceId=60239051

test_ku6:
	${PYTHON} -m cykdl -i http://www.ku6.com/video/detail?id=lfx8PD61clQ0knUJQad1R4Mbu2w

test_kuwo:
	${PYTHON} -m cykdl -i http://www.kuwo.cn/yinyue/7119332?catalog=yueku2016

test_lizhi:
	${PYTHON} -m cykdl -i http://www.lizhi.fm/202840/29101368624039686

test_sina:
	${PYTHON} -m cykdl -i 'http://video.sina.com.cn/ent/#250623748' -t 300

test_xiami:
	${PYTHON} -m cykdl -li http://www.xiami.com/album/2100285370?spm=a1z1s.3057849.0.0.hAuVwv

test_yinyuetai:
	${PYTHON} -m cykdl -i http://v.yinyuetai.com/video/2832181?f=SY-MKDT-MVSB-1

test_baidu:
	${PYTHON} -m cykdl -li http://music.baidu.com/album/266327865?pst=shoufa

test_douban:
	${PYTHON} -m cykdl -li https://music.douban.com/artists/player/?sid=660498,647629,647625,633870,622482,600594,589516,588385,583322,580114,576350

test_huya:
	${PYTHON} -m cykdl -i http://v.huya.com/play/2209082.html

test_le:
	${PYTHON} -m cykdl -i http://www.le.com/ptv/vplay/26859747.html -t 300

test_163v:
	${PYTHON} -m cykdl -i http://v.163.com/paike/VBI038VCL/VBNERA654.html

test_163m:
	${PYTHON} -m cykdl -li http://music.163.com/playlist?id=396542983

test_qq:
	${PYTHON} -m cykdl -i http://v.qq.com/cover/q/qsm7nxzwbnzc4dp.html?vid=m0305m0ur33

test_sohutv:
	${PYTHON} -m cykdl -i http://tv.sohu.com/20160607/n453456746.shtml

test_sohumy:
	${PYTHON} -m cykdl -i http://my.tv.sohu.com/pl/9090402/84077110.shtml

test_mgtv:
	${PYTHON} -m cykdl -i http://www.mgtv.com/v/2/293140/c/3269011.html

test_tudou:
	${PYTHON} -m cykdl -i http://video.tudou.com/v/XMjc2MTg1MzIzNg==.html
