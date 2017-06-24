#coding: utf8
#modified on https://gist.github.com/debugzxcv/85bb2750d8a5e29803f2686c47dc236b
#which I believe is interpreted from DouyuHTML5Player of spacemeowx2
#so this file follows MIT license



import hashlib
import binascii
import base64
b64_table = b'5pJMxr0Ns7H2ZFA93PTqvKJoCM+LCY9rF9CcWwt9AW1PmkflUrQlLVfyP4asv3gW08Eu/7cm31w566CwslMv53zzPkqE1sReq/Ffr5XUav0Q/J/AegT6pR8dxRojTp3VcJCF4nZDICwARdETKN3eM9K594f1u55lpK6ToZgCD1gHqNsrDHmIBmKXQpGbgiJdzI51WsiDyu+NMZmMGBl04TXNJGnaSG7CFccRIWM4RgVxDlk2lIG4fom+Ou6jex7g6EFm2VEUZ7VsPDQ7uslLp0mq+TcwKnLkqZbLJ87DVa1NMlT71wphgHdz2Iq24/7pGynsVhJg8Kb47X9EQBxvAw=='


def stupidMD5(s):
    hashstr = dy_md5(s)
    hash_raw = binascii.unhexlify(hashstr)
    mid = list(hash_raw)
    encrypt(list(s.encode('utf8')), mid)
    hash_val = ''.join('{:02x}'.format(x) for x in mid)
    return hash_val


def encrypt(key, s):
    table = base64.b64decode(b64_table)
#s is 32 bytes so unecessary code removed
    locTable = []
    for i in range(10):
        for j in range(256):
            locTable.append(table[j ^ key[i]] ^ 0x45)
    i = 0
    j = len(s) >> 3
    for j in range(j, 0, -1):
        block(s, i, locTable)
        i = i + 8

def safeAdd(x, y):
    x = 0x100000000 + x if x < 0 else x
    y = 0x100000000 + y if y < 0 else y
    x &= 0xffffffff
    y &= 0xffffffff
    return (x + y) & 0xffffffff


def bitRotateLeft(num, cnt):
    return (num << cnt & 0xffffffff) | ((num & 0xffffffff) >> (32 - cnt))

def md5cmn(q, a, b, x, s, t):
    return safeAdd(bitRotateLeft(safeAdd(safeAdd(a, q), safeAdd(x, t)), s), b)


#HERE is the change of std md5
#K table or FF GG HH II must be patched
def md5ff(a, b, c, d, x, s, t):
    return md5cmn(b & c | ~b & d, a, b, x, s, t + 1)


def md5gg(a, b, c, d, x, s, t):
    return md5cmn(b & d | c & ~d, a, b, x, s, t - 1)


def md5hh(a, b, c, d, x, s, t):
    return md5cmn(b ^ c ^ d, a, b, x, s, t + 1)


def md5ii(a, b, c, d, x, s, t):
    return md5cmn(c ^ (b | ~d), a, b, x, s, t - 1)


# Calculate the MD5 of an array of little-endian words, and a bit length.
def binlMD5(x, lens):

    # append padding
    x[lens >> 5] |= 0x80 << lens % 32
    x.extend([0] * (((lens + 64) >> 9 << 4) + 14 - len(x) + 1))
    x[(lens + 64 >> 9 << 4) + 14] = lens

    a = 1732584193
    b = -271733879
    c = -1732584194
    d = 271733878
    for i in range(0, len(x), 16):
        olda = a
        oldb = b
        oldc = c
        oldd = d
        a = md5ff(a, b, c, d, x[i], 7, -680876936)
        d = md5ff(d, a, b, c, x[i + 1], 12, -389564586)
        c = md5ff(c, d, a, b, x[i + 2], 17, 606105819)
        b = md5ff(b, c, d, a, x[i + 3], 22, -1044525330)
        a = md5ff(a, b, c, d, x[i + 4], 7, -176418897)
        d = md5ff(d, a, b, c, x[i + 5], 12, 1200080426)
        c = md5ff(c, d, a, b, x[i + 6], 17, -1473231341)
        b = md5ff(b, c, d, a, x[i + 7], 22, -45705983)
        a = md5ff(a, b, c, d, x[i + 8], 7, 1770035416)
        d = md5ff(d, a, b, c, x[i + 9], 12, -1958414417)
        c = md5ff(c, d, a, b, x[i + 10], 17, -42063)
        b = md5ff(b, c, d, a, x[i + 11], 22, -1990404162)
        a = md5ff(a, b, c, d, x[i + 12], 7, 1804603682)
        d = md5ff(d, a, b, c, x[i + 13], 12, -40341101)
        c = md5ff(c, d, a, b, x[i + 14], 17, -1502002290)
        if i + 15 == len(x):
            b = md5ff(b, c, d, a, 0, 22, 1236535329)
        else:
            b = md5ff(b, c, d, a, x[i + 15], 22, 1236535329)
        a = md5gg(a, b, c, d, x[i + 1], 5, -165796510)
        d = md5gg(d, a, b, c, x[i + 6], 9, -1069501632)
        c = md5gg(c, d, a, b, x[i + 11], 14, 643717713)
        b = md5gg(b, c, d, a, x[i], 20, -373897302)
        a = md5gg(a, b, c, d, x[i + 5], 5, -701558691)
        d = md5gg(d, a, b, c, x[i + 10], 9, 38016083)
        if i + 15 == len(x):
            c = md5gg(c, d, a, b, 0, 14, -660478335)
        else:
            c = md5gg(c, d, a, b, x[i + 15], 14, -660478335)
        b = md5gg(b, c, d, a, x[i + 4], 20, -405537848)
        a = md5gg(a, b, c, d, x[i + 9], 5, 568446438)
        d = md5gg(d, a, b, c, x[i + 14], 9, -1019803690)
        c = md5gg(c, d, a, b, x[i + 3], 14, -187363961)
        b = md5gg(b, c, d, a, x[i + 8], 20, 1163531501)
        a = md5gg(a, b, c, d, x[i + 13], 5, -1444681467)
        d = md5gg(d, a, b, c, x[i + 2], 9, -51403784)
        c = md5gg(c, d, a, b, x[i + 7], 14, 1735328473)
        b = md5gg(b, c, d, a, x[i + 12], 20, -1926607734)

        a = md5hh(a, b, c, d, x[i + 5], 4, -378558)
        d = md5hh(d, a, b, c, x[i + 8], 11, -2022574463)
        c = md5hh(c, d, a, b, x[i + 11], 16, 1839030562)
        b = md5hh(b, c, d, a, x[i + 14], 23, -35309556)
        a = md5hh(a, b, c, d, x[i + 1], 4, -1530992060)
        d = md5hh(d, a, b, c, x[i + 4], 11, 1272893353)
        c = md5hh(c, d, a, b, x[i + 7], 16, -155497632)
        b = md5hh(b, c, d, a, x[i + 10], 23, -1094730640)
        a = md5hh(a, b, c, d, x[i + 13], 4, 681279174)
        d = md5hh(d, a, b, c, x[i], 11, -358537222)
        c = md5hh(c, d, a, b, x[i + 3], 16, -722521979)
        b = md5hh(b, c, d, a, x[i + 6], 23, 76029189)
        a = md5hh(a, b, c, d, x[i + 9], 4, -640364487)
        d = md5hh(d, a, b, c, x[i + 12], 11, -421815835)
        if i + 15 == len(x):
            c = md5hh(c, d, a, b, 0, 16, 530742520)
        else:
            c = md5hh(c, d, a, b, x[i + 15], 16, 530742520)
        b = md5hh(b, c, d, a, x[i + 2], 23, -995338651)

        a = md5ii(a, b, c, d, x[i], 6, -198630844)
        d = md5ii(d, a, b, c, x[i + 7], 10, 1126891415)
        c = md5ii(c, d, a, b, x[i + 14], 15, -1416354905)
        b = md5ii(b, c, d, a, x[i + 5], 21, -57434055)
        a = md5ii(a, b, c, d, x[i + 12], 6, 1700485571)
        d = md5ii(d, a, b, c, x[i + 3], 10, -1894986606)
        c = md5ii(c, d, a, b, x[i + 10], 15, -1051523)
        b = md5ii(b, c, d, a, x[i + 1], 21, -2054922799)
        a = md5ii(a, b, c, d, x[i + 8], 6, 1873313359)
        if i + 15 == len(x):
            d = md5ii(d, a, b, c, 0, 10, -30611744)
        else:
            d = md5ii(d, a, b, c, x[i + 15], 10, -30611744)
        c = md5ii(c, d, a, b, x[i + 6], 15, -1560198380)
        b = md5ii(b, c, d, a, x[i + 13], 21, 1309151649)
        a = md5ii(a, b, c, d, x[i + 4], 6, -145523070)
        d = md5ii(d, a, b, c, x[i + 11], 10, -1120210379)
        c = md5ii(c, d, a, b, x[i + 2], 15, 718787259)
        b = md5ii(b, c, d, a, x[i + 9], 21, -343485551)


        a = safeAdd(a, olda)
        b = safeAdd(b, oldb)
        c = safeAdd(c, oldc)
        d = safeAdd(d, oldd)

    return [a, b, c, d]


# Convert an array of little-endian words to a string
def md5_unpack(data):
    result_list = []
    for num in data:
        if num < 0:
            num = 0x100000000 + num
        hex_s = '{:08x}'.format(num)
        result_list.append(hex_s[6:8])
        result_list.append(hex_s[4:6])
        result_list.append(hex_s[2:4])
        result_list.append(hex_s[:2])
    return ''.join(result_list)

def binl2rstr(input):
    # bp()
    output = ''
    length32 = len(input) * 32

    for i in range(0, length32, 8):
        output += chr(input[i >> 5] >> i % 32 & 0xFF)

    return output


# Convert a raw string to an array of little-endian words
# Characters >255 have their high-byte silently ignored.
def rstr2binl(input):
    output = [0] * ((len(input) >> 2) + 1)
    length8 = len(input) * 8
    for i in range(0, length8, 8):
        output[i >> 5] |= (ord(input[int(i / 8)]) & 0xFF) << i % 32

    return output


def dy_md5(s):
    digest = binlMD5(rstr2binl(s), len(s) * 8)
    return md5_unpack(digest)


def block(bstr, index, table):

    def si8(val, pos):
        bstr[index + pos] = val & 0xFF

    def li8(pos):
        if pos >= 100:
            return table[pos - 100]
        else:
#actually pos < 8
            return bstr[index + pos]

    # method body index: 983 method index: 1105
    _loc3_ = 0
    _loc5_ = 0
    _loc9_ = 0
    _loc11_ = 0
    _loc13_ = 0
    _loc15_ = 0
    _loc17_ = 0
    _loc19_ = 0
    _loc6_ = 0
    _loc4_ = 0
    _loc10_ = 0
    _loc8_ = 0
    _loc14_ = 0
    _loc12_ = 0
    _loc18_ = 0
    _loc16_ = 0
    _loc21_ = 0
    _loc20_ = 0
    tab = 100
    src = 0
    dest = 0
    _loc3_ = li8(src + 1)
    _loc5_ = li8(src)

    _loc5_ = _loc5_ << 8
    _loc5_ = _loc5_ | _loc3_

    _loc3_ = int(tab + _loc3_)
    _loc3_ = li8(_loc3_)
    _loc3_ = _loc3_ << 8
    _loc5_ = _loc3_ ^ _loc5_

    _loc3_ = int(_loc5_ >> 8)
    _loc9_ = int(tab + 256)
    _loc3_ = int(_loc9_ + _loc3_)
    _loc3_ = li8(_loc3_)
    _loc5_ = _loc5_ ^ _loc3_
    _loc11_ = _loc5_ & 255
    _loc3_ = int(tab + 512)
    _loc11_ = int(_loc3_ + _loc11_)
    _loc11_ = li8(_loc11_)
    _loc11_ = _loc11_ << 8
    _loc11_ = _loc11_ ^ _loc5_
    _loc13_ = int(_loc11_ >> 8)
    _loc5_ = int(tab + 768)
    _loc13_ = int(_loc5_ + _loc13_)
    _loc13_ = li8(_loc13_)
    _loc15_ = _loc11_ ^ _loc13_
    _loc11_ = li8(src + 7)
    _loc13_ = li8(src + 6)
    _loc13_ = _loc13_ << 8
    _loc11_ = _loc13_ | _loc11_
    _loc11_ = _loc11_ ^ _loc15_
    _loc11_ = _loc11_ ^ 1
    _loc13_ = _loc11_ & 255
    _loc17_ = int(tab + 1024)
    _loc13_ = int(_loc17_ + _loc13_)
    _loc13_ = li8(_loc13_)
    _loc13_ = _loc13_ << 8
    _loc11_ = _loc11_ ^ _loc13_
    _loc13_ = int(_loc11_ >> 8)
    _loc19_ = int(tab + 1280)
    _loc13_ = int(_loc19_ + _loc13_)
    _loc13_ = li8(_loc13_)
    _loc11_ = _loc11_ ^ _loc13_
    _loc6_ = _loc11_ & 255
    _loc13_ = int(tab + 1536)
    _loc6_ = int(_loc13_ + _loc6_)
    _loc6_ = li8(_loc6_)
    _loc6_ = _loc6_ << 8
    _loc6_ = _loc11_ ^ _loc6_
    _loc4_ = int(_loc6_ >> 8)
    _loc11_ = int(tab + 1792)
    _loc4_ = int(_loc11_ + _loc4_)
    _loc4_ = li8(_loc4_)
    _loc10_ = _loc6_ ^ _loc4_
    _loc6_ = li8(src + 5)
    _loc4_ = li8(src + 4)
    _loc4_ = _loc4_ << 8
    _loc6_ = _loc4_ | _loc6_
    _loc6_ = _loc6_ ^ _loc10_
    _loc6_ = _loc6_ ^ 2
    _loc8_ = _loc6_ & 255
    _loc4_ = int(tab + 2048)
    _loc8_ = int(_loc4_ + _loc8_)
    _loc8_ = li8(_loc8_)
    _loc8_ = _loc8_ << 8
    _loc8_ = _loc6_ ^ _loc8_
    _loc14_ = int(_loc8_ >> 8)
    _loc6_ = int(tab + 2304)
    _loc14_ = int(_loc6_ + _loc14_)
    _loc14_ = li8(_loc14_)
    _loc8_ = _loc8_ ^ _loc14_
    _loc14_ = _loc8_ & 255
    _loc14_ = int(tab + _loc14_)
    _loc14_ = li8(_loc14_)
    _loc14_ = _loc14_ << 8
    _loc8_ = _loc8_ ^ _loc14_
    _loc14_ = int(_loc8_ >> 8)
    _loc14_ = int(_loc9_ + _loc14_)
    _loc14_ = li8(_loc14_)
    _loc8_ = _loc8_ ^ _loc14_
    _loc14_ = li8(src + 3)
    src = li8(src + 2)
    src = src << 8
    src = src | _loc14_
    src = src ^ _loc8_
    src = src ^ 3
    _loc14_ = src & 255
    _loc14_ = int(_loc3_ + _loc14_)
    _loc14_ = li8(_loc14_)
    _loc14_ = _loc14_ << 8
    src = src ^ _loc14_
    _loc14_ = int(src >> 8)
    _loc14_ = int(_loc5_ + _loc14_)
    _loc14_ = li8(_loc14_)
    src = src ^ _loc14_
    _loc14_ = src & 255
    _loc14_ = int(_loc17_ + _loc14_)
    _loc14_ = li8(_loc14_)
    _loc14_ = _loc14_ << 8
    src = src ^ _loc14_
    _loc14_ = int(src >> 8)
    _loc14_ = int(_loc19_ + _loc14_)
    _loc14_ = li8(_loc14_)
    _loc14_ = src ^ _loc14_
    _loc15_ = _loc15_ ^ _loc14_
    _loc15_ = _loc15_ ^ 4
    src = _loc15_ & 255
    src = int(_loc13_ + src)
    src = li8(src)
    src = src << 8
    _loc15_ = _loc15_ ^ src
    src = int(_loc15_ >> 8)
    src = int(_loc11_ + src)
    src = li8(src)
    _loc15_ = _loc15_ ^ src
    src = _loc15_ & 255
    src = int(_loc4_ + src)
    src = li8(src)
    src = src << 8
    _loc15_ = _loc15_ ^ src
    src = int(_loc15_ >> 8)
    src = int(_loc6_ + src)
    src = li8(src)
    _loc15_ = _loc15_ ^ src
    src = _loc10_ ^ _loc15_
    src = src ^ 5
    _loc10_ = src & 255
    _loc10_ = int(tab + _loc10_)
    _loc10_ = li8(_loc10_)
    _loc10_ = _loc10_ << 8
    src = src ^ _loc10_
    _loc10_ = int(src >> 8)
    _loc10_ = int(_loc9_ + _loc10_)
    _loc10_ = li8(_loc10_)
    src = src ^ _loc10_
    _loc10_ = src & 255
    _loc10_ = int(_loc3_ + _loc10_)
    _loc10_ = li8(_loc10_)
    _loc10_ = _loc10_ << 8
    src = src ^ _loc10_
    _loc10_ = int(src >> 8)
    _loc10_ = int(_loc5_ + _loc10_)
    _loc10_ = li8(_loc10_)
    src = src ^ _loc10_
    _loc10_ = _loc8_ ^ src
    _loc10_ = _loc10_ ^ 6
    _loc8_ = _loc10_ & 255
    _loc8_ = int(_loc17_ + _loc8_)
    _loc8_ = li8(_loc8_)
    _loc8_ = _loc8_ << 8
    _loc10_ = _loc10_ ^ _loc8_
    _loc8_ = int(_loc10_ >> 8)
    _loc8_ = int(_loc19_ + _loc8_)
    _loc8_ = li8(_loc8_)
    _loc10_ = _loc10_ ^ _loc8_
    _loc8_ = _loc10_ & 255
    _loc8_ = int(_loc13_ + _loc8_)
    _loc8_ = li8(_loc8_)
    _loc8_ = _loc8_ << 8
    _loc10_ = _loc10_ ^ _loc8_
    _loc8_ = int(_loc10_ >> 8)
    _loc8_ = int(_loc11_ + _loc8_)
    _loc8_ = li8(_loc8_)
    _loc8_ = _loc10_ ^ _loc8_
    _loc10_ = _loc14_ ^ _loc8_
    _loc10_ = _loc10_ ^ 7
    _loc14_ = _loc10_ & 255
    _loc14_ = int(_loc4_ + _loc14_)
    _loc14_ = li8(_loc14_)
    _loc14_ = _loc14_ << 8
    _loc10_ = _loc10_ ^ _loc14_
    _loc14_ = int(_loc10_ >> 8)
    _loc14_ = int(_loc6_ + _loc14_)
    _loc14_ = li8(_loc14_)
    _loc10_ = _loc10_ ^ _loc14_
    _loc14_ = _loc10_ & 255
    _loc14_ = int(tab + _loc14_)
    _loc14_ = li8(_loc14_)
    _loc14_ = _loc14_ << 8
    _loc10_ = _loc10_ ^ _loc14_
    _loc14_ = int(_loc10_ >> 8)
    _loc14_ = int(_loc9_ + _loc14_)
    _loc14_ = li8(_loc14_)
    _loc14_ = _loc15_ ^ _loc14_
    _loc10_ = _loc14_ ^ _loc10_
    _loc10_ = _loc10_ ^ 8
    _loc14_ = _loc10_ & 255
    _loc14_ = int(_loc3_ + _loc14_)
    _loc14_ = li8(_loc14_)
    _loc14_ = _loc14_ << 8
    _loc10_ = _loc10_ ^ _loc14_
    _loc14_ = int(_loc10_ >> 8)
    _loc14_ = int(_loc5_ + _loc14_)
    _loc14_ = li8(_loc14_)
    _loc10_ = _loc10_ ^ _loc14_
    _loc14_ = _loc10_ & 255
    _loc14_ = int(_loc17_ + _loc14_)
    _loc14_ = li8(_loc14_)
    _loc14_ = _loc14_ << 8
    _loc10_ = _loc10_ ^ _loc14_
    _loc14_ = int(_loc10_ >> 8)
    _loc14_ = int(_loc19_ + _loc14_)
    _loc14_ = li8(_loc14_)
    _loc14_ = src ^ _loc14_
    _loc10_ = _loc14_ ^ _loc10_
    _loc10_ = _loc10_ ^ 10
    _loc14_ = _loc10_ & 255
    _loc14_ = int(_loc4_ + _loc14_)
    _loc14_ = li8(_loc14_)
    _loc14_ = _loc14_ << 8
    _loc14_ = _loc14_ ^ _loc10_
    _loc12_ = int(_loc14_ >> 8)
    _loc12_ = int(_loc6_ + _loc12_)
    _loc12_ = li8(_loc12_)
    _loc14_ = _loc14_ ^ _loc12_
    _loc12_ = _loc14_ & 255
    _loc12_ = int(tab + _loc12_)
    _loc12_ = li8(_loc12_)
    _loc12_ = _loc12_ << 8
    _loc14_ = _loc12_ ^ _loc14_
    _loc12_ = int(_loc14_ >> 8)
    _loc12_ = int(_loc9_ + _loc12_)
    _loc18_ = li8(_loc12_)
    _loc12_ = src & 255
    _loc12_ = int(_loc13_ + _loc12_)
    _loc12_ = li8(_loc12_)
    _loc12_ = _loc12_ << 8
    src = _loc12_ ^ src
    _loc12_ = int(src >> 8)
    _loc12_ = int(_loc11_ + _loc12_)
    _loc12_ = li8(_loc12_)
    src = src ^ _loc12_
    _loc12_ = src & 255
    _loc12_ = int(_loc4_ + _loc12_)
    _loc12_ = li8(_loc12_)
    _loc12_ = _loc12_ << 8
    src = _loc12_ ^ src
    _loc12_ = int(src >> 8)
    _loc12_ = int(_loc6_ + _loc12_)
    _loc12_ = li8(_loc12_)
    _loc12_ = _loc8_ ^ _loc12_
    src = _loc12_ ^ src
    _loc12_ = src ^ 11
    src = _loc12_ ^ _loc18_
    src = src ^ _loc14_
    src = src ^ 14
    _loc14_ = src & 255
    _loc14_ = int(_loc17_ + _loc14_)
    _loc14_ = li8(_loc14_)
    _loc14_ = _loc14_ << 8
    src = _loc14_ ^ src
    _loc14_ = int(src >> 8)
    _loc14_ = int(_loc19_ + _loc14_)
    _loc14_ = li8(_loc14_)
    src = src ^ _loc14_
    _loc14_ = src & 255
    _loc14_ = int(_loc13_ + _loc14_)
    _loc14_ = li8(_loc14_)
    _loc14_ = _loc14_ << 8
    src = _loc14_ ^ src
    _loc14_ = int(src >> 8)
    _loc14_ = int(_loc11_ + _loc14_)
    _loc14_ = li8(_loc14_)
    src = src ^ _loc14_
    _loc14_ = _loc8_ & 255
    _loc14_ = int(tab + _loc14_)
    _loc14_ = li8(_loc14_)
    _loc14_ = _loc14_ << 8
    _loc8_ = _loc14_ ^ _loc8_
    _loc14_ = int(_loc8_ >> 8)
    _loc14_ = int(_loc9_ + _loc14_)
    _loc14_ = li8(_loc14_)
    _loc8_ = _loc8_ ^ _loc14_
    _loc14_ = _loc8_ & 255
    _loc14_ = int(_loc3_ + _loc14_)
    _loc14_ = li8(_loc14_)
    _loc14_ = _loc14_ << 8
    _loc8_ = _loc14_ ^ _loc8_
    _loc14_ = int(_loc8_ >> 8)
    _loc14_ = int(_loc5_ + _loc14_)
    _loc14_ = li8(_loc14_)
    _loc14_ = _loc15_ ^ _loc14_
    _loc8_ = _loc14_ ^ _loc8_
    _loc14_ = _loc8_ ^ 13
    _loc8_ = _loc12_ & 255
    _loc8_ = int(_loc3_ + _loc8_)
    _loc8_ = li8(_loc8_)
    _loc8_ = _loc8_ << 8
    _loc8_ = _loc8_ ^ _loc12_
    _loc12_ = int(_loc8_ >> 8)
    _loc12_ = int(_loc5_ + _loc12_)
    _loc12_ = li8(_loc12_)
    _loc8_ = _loc8_ ^ _loc12_
    _loc12_ = _loc8_ & 255
    _loc12_ = int(_loc17_ + _loc12_)
    _loc12_ = li8(_loc12_)
    _loc12_ = _loc12_ << 8
    _loc8_ = _loc12_ ^ _loc8_
    _loc12_ = int(_loc8_ >> 8)
    _loc12_ = int(_loc19_ + _loc12_)
    _loc12_ = li8(_loc12_)
    _loc12_ = _loc14_ ^ _loc12_
    _loc8_ = _loc12_ ^ _loc8_
    _loc8_ = _loc8_ ^ src
    _loc8_ = _loc8_ ^ 30
    _loc12_ = _loc8_ & 255
    _loc12_ = int(_loc4_ + _loc12_)
    _loc12_ = li8(_loc12_)
    _loc12_ = _loc12_ << 8
    _loc8_ = _loc8_ ^ _loc12_
    _loc12_ = int(_loc8_ >> 8)
    _loc12_ = int(_loc6_ + _loc12_)
    _loc12_ = li8(_loc12_)
    _loc8_ = _loc8_ ^ _loc12_
    _loc12_ = _loc8_ & 255
    _loc12_ = int(tab + _loc12_)
    _loc12_ = li8(_loc12_)
    _loc12_ = _loc12_ << 8
    _loc8_ = _loc8_ ^ _loc12_
    _loc12_ = int(_loc8_ >> 8)
    _loc12_ = int(_loc9_ + _loc12_)
    _loc12_ = li8(_loc12_)
    _loc8_ = _loc8_ ^ _loc12_
    _loc15_ = _loc15_ ^ 1
    _loc12_ = _loc15_ & 255
    _loc12_ = int(_loc17_ + _loc12_)
    _loc12_ = li8(_loc12_)
    _loc12_ = _loc12_ << 8
    _loc15_ = _loc12_ ^ _loc15_
    _loc12_ = int(_loc15_ >> 8)
    _loc12_ = int(_loc19_ + _loc12_)
    _loc12_ = li8(_loc12_)
    _loc15_ = _loc15_ ^ _loc12_
    _loc12_ = _loc15_ & 255
    _loc12_ = int(_loc13_ + _loc12_)
    _loc12_ = li8(_loc12_)
    _loc12_ = _loc12_ << 8
    _loc15_ = _loc12_ ^ _loc15_
    _loc12_ = int(_loc15_ >> 8)
    _loc12_ = int(_loc11_ + _loc12_)
    _loc12_ = li8(_loc12_)
    _loc10_ = _loc10_ ^ _loc12_
    _loc15_ = _loc10_ ^ _loc15_
    _loc15_ = _loc15_ ^ 13
    _loc10_ = _loc14_ & 255
    _loc10_ = int(_loc13_ + _loc10_)
    _loc10_ = li8(_loc10_)
    _loc10_ = _loc10_ << 8
    _loc10_ = _loc10_ ^ _loc14_
    _loc14_ = int(_loc10_ >> 8)
    _loc14_ = int(_loc11_ + _loc14_)
    _loc14_ = li8(_loc14_)
    _loc10_ = _loc10_ ^ _loc14_
    _loc14_ = _loc10_ & 255
    _loc14_ = int(_loc4_ + _loc14_)
    _loc14_ = li8(_loc14_)
    _loc14_ = _loc14_ << 8
    _loc10_ = _loc14_ ^ _loc10_
    _loc14_ = int(_loc10_ >> 8)
    _loc14_ = int(_loc6_ + _loc14_)
    _loc14_ = li8(_loc14_)
    _loc14_ = _loc15_ ^ _loc14_
    _loc10_ = _loc14_ ^ _loc10_
    _loc10_ = _loc10_ ^ _loc8_
    _loc10_ = _loc10_ ^ 2
    _loc14_ = _loc10_ & 255
    _loc14_ = int(_loc3_ + _loc14_)
    _loc14_ = li8(_loc14_)
    _loc14_ = _loc14_ << 8
    _loc10_ = _loc10_ ^ _loc14_
    _loc14_ = int(_loc10_ >> 8)
    _loc14_ = int(_loc5_ + _loc14_)
    _loc14_ = li8(_loc14_)
    _loc10_ = _loc10_ ^ _loc14_
    _loc14_ = _loc10_ & 255
    _loc14_ = int(_loc17_ + _loc14_)
    _loc14_ = li8(_loc14_)
    _loc14_ = _loc14_ << 8
    _loc10_ = _loc10_ ^ _loc14_
    _loc14_ = int(_loc10_ >> 8)
    _loc14_ = int(_loc19_ + _loc14_)
    _loc14_ = li8(_loc14_)
    _loc14_ = _loc10_ ^ _loc14_
    _loc10_ = _loc15_ & 255
    _loc10_ = int(tab + _loc10_)
    _loc10_ = li8(_loc10_)
    _loc10_ = _loc10_ << 8
    _loc15_ = _loc10_ ^ _loc15_
    _loc10_ = int(_loc15_ >> 8)
    _loc10_ = int(_loc9_ + _loc10_)
    _loc10_ = li8(_loc10_)
    _loc15_ = _loc15_ ^ _loc10_
    _loc10_ = _loc15_ & 255
    _loc10_ = int(_loc3_ + _loc10_)
    _loc10_ = li8(_loc10_)
    _loc10_ = _loc10_ << 8
    _loc15_ = _loc10_ ^ _loc15_
    _loc10_ = int(_loc15_ >> 8)
    _loc10_ = int(_loc5_ + _loc10_)
    _loc10_ = li8(_loc10_)
    _loc15_ = _loc10_ ^ _loc15_
    _loc15_ = _loc15_ ^ _loc14_
    _loc15_ = _loc15_ ^ 19
    _loc10_ = _loc15_ & 255
    _loc10_ = int(_loc13_ + _loc10_)
    _loc10_ = li8(_loc10_)
    _loc10_ = _loc10_ << 8
    _loc15_ = _loc15_ ^ _loc10_
    _loc10_ = int(_loc15_ >> 8)
    _loc10_ = int(_loc11_ + _loc10_)
    _loc10_ = li8(_loc10_)
    _loc15_ = _loc15_ ^ _loc10_
    _loc10_ = _loc15_ & 255
    _loc10_ = int(_loc4_ + _loc10_)
    _loc10_ = li8(_loc10_)
    _loc10_ = _loc10_ << 8
    _loc15_ = _loc15_ ^ _loc10_
    _loc10_ = int(_loc15_ >> 8)
    _loc10_ = int(_loc6_ + _loc10_)
    _loc10_ = li8(_loc10_)
    _loc12_ = _loc15_ ^ _loc10_
    _loc15_ = src ^ _loc12_
    _loc15_ = _loc15_ ^ 20
    src = _loc15_ & 255
    src = int(tab + src)
    src = li8(src)
    src = src << 8
    _loc15_ = _loc15_ ^ src
    src = int(_loc15_ >> 8)
    src = int(_loc9_ + src)
    src = li8(src)
    _loc15_ = _loc15_ ^ src
    src = _loc15_ & 255
    src = int(_loc3_ + src)
    src = li8(src)
    src = src << 8
    _loc15_ = _loc15_ ^ src
    src = int(_loc15_ >> 8)
    src = int(_loc5_ + src)
    src = li8(src)
    _loc15_ = _loc15_ ^ src
    src = _loc8_ ^ _loc15_
    src = src ^ 21
    _loc10_ = src & 255
    _loc10_ = int(_loc17_ + _loc10_)
    _loc10_ = li8(_loc10_)
    _loc10_ = _loc10_ << 8
    src = src ^ _loc10_
    _loc10_ = int(src >> 8)
    _loc10_ = int(_loc19_ + _loc10_)
    _loc10_ = li8(_loc10_)
    src = src ^ _loc10_
    _loc10_ = src & 255
    _loc10_ = int(_loc13_ + _loc10_)
    _loc10_ = li8(_loc10_)
    _loc10_ = _loc10_ << 8
    src = src ^ _loc10_
    _loc10_ = int(src >> 8)
    _loc10_ = int(_loc11_ + _loc10_)
    _loc10_ = li8(_loc10_)
    _loc10_ = src ^ _loc10_
    src = _loc14_ ^ _loc10_
    src = src ^ 22
    _loc8_ = src & 255
    _loc8_ = int(_loc4_ + _loc8_)
    _loc8_ = li8(_loc8_)
    _loc8_ = _loc8_ << 8
    src = src ^ _loc8_
    _loc8_ = int(src >> 8)
    _loc8_ = int(_loc6_ + _loc8_)
    _loc8_ = li8(_loc8_)
    src = src ^ _loc8_
    _loc8_ = src & 255
    _loc8_ = int(tab + _loc8_)
    _loc8_ = li8(_loc8_)
    _loc8_ = _loc8_ << 8
    src = src ^ _loc8_
    _loc8_ = int(src >> 8)
    _loc8_ = int(_loc9_ + _loc8_)
    _loc8_ = li8(_loc8_)
    src = src ^ _loc8_
    _loc8_ = _loc12_ ^ src
    _loc8_ = _loc8_ ^ 23
    _loc14_ = _loc8_ & 255
    _loc14_ = int(_loc3_ + _loc14_)
    _loc14_ = li8(_loc14_)
    _loc14_ = _loc14_ << 8
    _loc8_ = _loc8_ ^ _loc14_
    _loc14_ = int(_loc8_ >> 8)
    _loc14_ = int(_loc5_ + _loc14_)
    _loc14_ = li8(_loc14_)
    _loc8_ = _loc8_ ^ _loc14_
    _loc14_ = _loc8_ & 255
    _loc14_ = int(_loc17_ + _loc14_)
    _loc14_ = li8(_loc14_)
    _loc14_ = _loc14_ << 8
    _loc8_ = _loc8_ ^ _loc14_
    _loc14_ = int(_loc8_ >> 8)
    _loc14_ = int(_loc19_ + _loc14_)
    _loc14_ = li8(_loc14_)
    _loc14_ = _loc15_ ^ _loc14_
    _loc8_ = _loc14_ ^ _loc8_
    _loc8_ = _loc8_ ^ 24
    _loc14_ = _loc8_ & 255
    _loc14_ = int(_loc13_ + _loc14_)
    _loc14_ = li8(_loc14_)
    _loc14_ = _loc14_ << 8
    _loc8_ = _loc8_ ^ _loc14_
    _loc14_ = int(_loc8_ >> 8)
    _loc14_ = int(_loc11_ + _loc14_)
    _loc14_ = li8(_loc14_)
    _loc8_ = _loc8_ ^ _loc14_
    _loc14_ = _loc8_ & 255
    _loc14_ = int(_loc4_ + _loc14_)
    _loc14_ = li8(_loc14_)
    _loc14_ = _loc14_ << 8
    _loc8_ = _loc8_ ^ _loc14_
    _loc14_ = int(_loc8_ >> 8)
    _loc14_ = int(_loc6_ + _loc14_)
    _loc14_ = li8(_loc14_)
    _loc14_ = _loc10_ ^ _loc14_
    _loc8_ = _loc14_ ^ _loc8_
    _loc12_ = _loc8_ ^ 26
    _loc8_ = _loc12_ & 255
    _loc8_ = int(_loc3_ + _loc8_)
    _loc8_ = li8(_loc8_)
    _loc8_ = _loc8_ << 8
    _loc8_ = _loc8_ ^ _loc12_
    _loc14_ = int(_loc8_ >> 8)
    _loc14_ = int(_loc5_ + _loc14_)
    _loc14_ = li8(_loc14_)
    _loc8_ = _loc8_ ^ _loc14_
    _loc14_ = _loc8_ & 255
    _loc14_ = int(_loc17_ + _loc14_)
    _loc14_ = li8(_loc14_)
    _loc14_ = _loc14_ << 8
    _loc8_ = _loc14_ ^ _loc8_
    _loc14_ = int(_loc8_ >> 8)
    _loc14_ = int(_loc19_ + _loc14_)
    _loc18_ = li8(_loc14_)
    _loc14_ = _loc10_ & 255
    _loc14_ = int(tab + _loc14_)
    _loc14_ = li8(_loc14_)
    _loc14_ = _loc14_ << 8
    _loc10_ = _loc14_ ^ _loc10_
    _loc14_ = int(_loc10_ >> 8)
    _loc14_ = int(_loc9_ + _loc14_)
    _loc14_ = li8(_loc14_)
    _loc10_ = _loc10_ ^ _loc14_
    _loc14_ = _loc10_ & 255
    _loc14_ = int(_loc3_ + _loc14_)
    _loc14_ = li8(_loc14_)
    _loc14_ = _loc14_ << 8
    _loc10_ = _loc14_ ^ _loc10_
    _loc14_ = int(_loc10_ >> 8)
    _loc14_ = int(_loc5_ + _loc14_)
    _loc14_ = li8(_loc14_)
    _loc14_ = src ^ _loc14_
    _loc10_ = _loc14_ ^ _loc10_
    _loc14_ = _loc10_ ^ 27
    _loc10_ = _loc14_ ^ _loc18_
    _loc8_ = _loc10_ ^ _loc8_
    _loc10_ = int(_loc8_ >> 8)
    _loc18_ = _loc15_ ^ 1
    _loc16_ = _loc18_ & 255
    _loc16_ = int(_loc4_ + _loc16_)
    _loc16_ = li8(_loc16_)
    _loc16_ = _loc16_ << 8
    _loc18_ = _loc16_ ^ _loc18_
    _loc16_ = int(_loc18_ >> 8)
    _loc16_ = int(_loc6_ + _loc16_)
    _loc16_ = li8(_loc16_)
    _loc18_ = _loc18_ ^ _loc16_
    _loc16_ = _loc18_ & 255
    _loc16_ = int(tab + _loc16_)
    _loc16_ = li8(_loc16_)
    _loc16_ = _loc16_ << 8
    _loc18_ = _loc16_ ^ _loc18_
    _loc16_ = int(_loc18_ >> 8)
    _loc16_ = int(_loc9_ + _loc16_)
    _loc16_ = li8(_loc16_)
    _loc12_ = _loc12_ ^ _loc16_
    _loc12_ = _loc12_ ^ _loc18_
    _loc12_ = _loc12_ ^ 29
    _loc18_ = _loc12_ & 255
    _loc18_ = int(_loc17_ + _loc18_)
    _loc18_ = li8(_loc18_)
    _loc18_ = _loc18_ << 8
    _loc18_ = _loc18_ ^ _loc12_
    _loc16_ = int(_loc18_ >> 8)
    _loc16_ = int(_loc19_ + _loc16_)
    _loc16_ = li8(_loc16_)
    _loc18_ = _loc18_ ^ _loc16_
    _loc16_ = _loc18_ & 255
    _loc16_ = int(_loc13_ + _loc16_)
    _loc16_ = li8(_loc16_)
    _loc16_ = _loc16_ << 8
    _loc18_ = _loc16_ ^ _loc18_
    _loc16_ = int(_loc18_ >> 8)
    _loc21_ = int(_loc11_ + _loc16_)
    _loc21_ = li8(_loc21_)
    _loc20_ = src & 255
    _loc17_ = int(_loc17_ + _loc20_)
    _loc17_ = li8(_loc17_)
    _loc17_ = _loc17_ << 8
    _loc17_ = _loc17_ ^ src
    src = int(_loc17_ >> 8)
    _loc19_ = int(_loc19_ + src)
    _loc19_ = li8(_loc19_)
    _loc17_ = _loc17_ ^ _loc19_
    _loc19_ = _loc17_ & 255
    _loc19_ = int(_loc13_ + _loc19_)
    _loc19_ = li8(_loc19_)
    _loc19_ = _loc19_ << 8
    _loc17_ = _loc19_ ^ _loc17_
    _loc19_ = int(_loc17_ >> 8)
    _loc19_ = int(_loc11_ + _loc19_)
    _loc19_ = li8(_loc19_)
    _loc19_ = _loc15_ ^ _loc19_
    _loc17_ = _loc19_ ^ _loc17_
    _loc17_ = _loc17_ ^ 29
    _loc19_ = _loc17_ & 255
    tab = int(tab + _loc19_)
    tab = li8(tab)
    tab = tab << 8
    tab = tab ^ _loc17_
    _loc19_ = int(tab >> 8)
    _loc9_ = int(_loc9_ + _loc19_)
    _loc9_ = li8(_loc9_)
    _loc9_ = tab ^ _loc9_
    tab = _loc9_ & 255
    _loc3_ = int(_loc3_ + tab)
    _loc3_ = li8(_loc3_)
    _loc3_ = _loc3_ << 8
    _loc3_ = _loc3_ ^ _loc9_
    _loc9_ = int(_loc3_ >> 8)
    _loc5_ = int(_loc5_ + _loc9_)
    _loc5_ = li8(_loc5_)
    _loc9_ = _loc14_ & 255
    _loc9_ = int(_loc13_ + _loc9_)
    _loc9_ = li8(_loc9_)
    _loc9_ = _loc9_ << 8
    _loc9_ = _loc9_ ^ _loc14_
    tab = int(_loc9_ >> 8)
    tab = int(_loc11_ + tab)
    tab = li8(tab)
    _loc9_ = _loc9_ ^ tab
    tab = _loc9_ & 255
    tab = int(_loc4_ + tab)
    tab = li8(tab)
    tab = tab << 8
    _loc9_ = tab ^ _loc9_
    tab = int(_loc9_ >> 8)
    tab = int(_loc6_ + tab)
    _loc11_ = li8(tab)
    tab = dest
    si8(_loc10_, tab)
    _loc13_ = _loc8_ ^ 30
    si8(_loc13_, tab + 1)
    si8(_loc16_, tab + 2)
    _loc13_ = _loc18_ ^ _loc21_
    si8(_loc13_, tab + 3)
    _loc5_ = _loc12_ ^ _loc5_
    _loc5_ = _loc5_ ^ _loc3_
    _loc3_ = int(_loc5_ >> 8)
    si8(_loc3_, tab + 4)
    _loc5_ = _loc5_ ^ 32
    si8(_loc5_, tab + 5)
    _loc5_ = _loc17_ ^ _loc11_
    _loc5_ = _loc5_ ^ _loc9_
    _loc3_ = int(_loc5_ >> 8)
    si8(_loc3_, tab + 6)
    _loc5_ = _loc5_ ^ 31
    si8(_loc5_, tab + 7)
