test_live: test_bobo test_douyu test_huomao test_longzhu test_panda test_zhanqi test_bililive test_huyalive test_lelive test_cc test_qqlive

PYTHON ?= python3

test_bobo:
	${PYTHON} -m cykdl -i http://www.bobo.com/10003822?f=pHome.Hot_anchor.1

test_douyu:
	${PYTHON} -m cykdl -i http://www.douyu.com/58428

test_huomao:
	${PYTHON} -m cykdl -i http://www.huomaotv.cn/live/845

test_longzhu:
	${PYTHON} -m cykdl -i http://star.longzhu.com/133097?from=challcontent

test_panda:
	${PYTHON} -m cykdl -i http://www.panda.tv/60995

test_zhanqi:
	${PYTHON} -m cykdl -i https://www.zhanqi.tv/naigege

test_bililive:
	${PYTHON} -m cykdl -i http://live.bilibili.com/3

test_huyalive:
	${PYTHON} -m cykdl -i http://www.huya.com/lengsimo

test_lelive:
	${PYTHON} -m cykdl -i http://live.le.com/lunbo/play/index.shtml?channel=224

test_cc:
	${PYTHON} -m cykdl -i http://cc.163.com/30348786/

test_qqlive:
	${PYTHON} -m cykdl -i http://live.qq.com/10001075
