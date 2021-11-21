# -*- coding: utf-8 -*-

from .._common import *


js_ctx = None

def init_jsengine():
    global js_ctx
    if js_ctx is None:
        assert JSEngine, "No JS Interpreter found, can't use cmd5x!"
        js_ctx = JSEngine(init_global=True)

        # REF: https://zsaim.github.io/2019/08/23/Iqiyi-cmd5x-Analysis/
        #      https://raw.githubusercontent.com/ZSAIm/ZSAIm.github.io/master/misc/2019-08-23/iqiyi_cmd5x.js
        js = get_pkgdata_str(__name__, 'cmd5x.js',
                    'https://raw.githubusercontent.com/zhangn1985/ykdl/master/ykdl/extractors/iqiyi/cmd5x.js')
        js_ctx.append(js)

        # REF: https://github.com/lldy/js
        js = get_pkgdata_str(__name__, 'cmd5x_iqiyi3.js',
                    'https://raw.githubusercontent.com/zhangn1985/ykdl/master/ykdl/extractors/iqiyi/cmd5x_iqiyi3.js')
        js_ctx.append(js)

def md5(s):
    return hash.md5(s)

def md5x(s):
    #sufix = ''
    #for j in range(8):
    #    for k in range(4):
    #        v4 = 13 * (66 * k + 27 * j) % 35
    #        if ( v4 >= 10 ):
    #            v8 = v4 + 88
    #        else:
    #            v8 = v4 + 49
    #        sufix += chr(v8)
    return md5(s + '1j2k2k3l3l4m4m5n5n6o6o7p7p8q8q9r')

def cmd5x(s):
    # the param src below uses salt h2l6suw16pbtikmotf0j79cej4n8uw13
    #    01010031010000000000
    #    01010031010010000000
    #    01080031010000000000
    #    01080031010010000000
    #    03020031010000000000
    #    03020031010010000000
    #    03030031010000000000
    #    03030031010010000000
    #    02020031010000000000
    #    02020031010010000000
    #if len(s) < 6:
    #    return '0'
    #return md5(s + 'h2l6suw16pbtikmotf0j79cej4n8uw13')
    # out of date

    init_jsengine()
    return js_ctx.call('cmd5x_exports.cmd5x', s)

def cmd5x_iqiyi3(s):
    # used for live
    init_jsengine()
    return js_ctx.call('cmd5x', s)
