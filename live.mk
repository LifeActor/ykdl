test_live: test_bobo test_douyu test_huomao test_longzhu test_panda test_zhanqi test_bililive test_huyalive test_lelive test_cc test_qqlive

test_bobo:
	${PYTHON} bin/ykdl.py -i http://www.bobo.com/612624?f=pHome.Hot_anchor.1

test_douyu:
	${PYTHON} bin/ykdl.py -i http://www.douyu.com/58428

test_huomao:
	${PYTHON} bin/ykdl.py -i http://www.huomaotv.cn/live/845

test_longzhu:
	${PYTHON} bin/ykdl.py -i http://star.longzhu.com/133097?from=challcontent

test_panda:
	${PYTHON} bin/ykdl.py -i http://www.panda.tv/60995

test_zhanqi:
	${PYTHON} bin/ykdl.py -i http://www.zhanqi.tv/djs

test_bililive:
	${PYTHON} bin/ykdl.py -i http://live.bilibili.com/3

test_huyalive:
	${PYTHON} bin/ykdl.py -i http://www.huya.com/lengsimo

test_lelive:
	${PYTHON} bin/ykdl.py -i http://live.le.com/lunbo/play/index.shtml?channel=224

test_cc:
	${PYTHON} bin/ykdl.py -i http://cc.163.com/30348786/

test_qqlive:
	${PYTHON} bin/ykdl.py -i http://live.qq.com/10001075
