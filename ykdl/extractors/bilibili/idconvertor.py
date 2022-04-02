# -*- coding: utf-8 -*-

'''Bilibili VID convertor, AV <=> BV.

Origin by mcft:
  https://www.zhihu.com/question/381784377/answer/1099438784

Modified by SeaHOH
'''


__all__ = ['bv2av', 'av2bv']

tablec = list('fZodR9XQDSUm21yCkr6zBqiveYah8bt4xsWpHnJE7jL5VG3guMTKNPAwcF')
tablei = {c: i for i, c in enumerate(tablec)}
bvtl = list('BV1**4*1*7**')
bvco = [9, 8, 1, 6, 2, 4]  # av >= 29460791296 ( 2^35 - 2^32 - 2^29 - 2^26 )
                           # ? [9, 8, 1, 6, 2, 4, 0, 7, 3, 5]
                           # ? [9, 8, 1, 6, 2, 4, 5, 7, 3, 0]
xor = 177451812
add = []
_d = 100618342136696320
while _d:
    _d, _m = divmod(_d, 58)
    add.append(_m)


def bv2av(bv):
    r = 0
    x = list(bv[-10:])
    for p, i in enumerate(bvco):
        r += (tablei[x[i]] - add[p]) * 58 ** p
    return str(r ^ xor)

def av2bv(av):
    if isinstance(av, str):
        av = av.lstrip('av')
    r = bvtl.copy()
    x = int(av) ^ xor
    for p, i in enumerate(bvco):
        x, m = divmod(x + add[p], 58)
        r[i + 2] = tablec[m]
    return ''.join(r)

