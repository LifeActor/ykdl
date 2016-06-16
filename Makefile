include video.mk
include live.mk

test: unittest

test_video: test_video1 test_video2 test_video3

unittest:
	python tests/ykdl_test.py
