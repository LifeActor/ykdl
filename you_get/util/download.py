import os
from urllib import request
import sys
from .html import fake_headers, add_header


def simple_hook(arg1, arg2, arg3):
    if arg3 > 0:
        percent = int(arg1 * arg2 * 100 / arg3)
        if percent > 100:
            percent = 100
        sys.stdout.write('\r %3d' % percent + '%')
        sys.stdout.flush()
    else:
        sys.stdout.write('\r' + str(round(arg1 * arg2 / 1048576, 1)) + 'MB')
        sys.stdout.flush()

def save_url(url, name, reporthook = simple_hook):
    bs = 1024*8
    size = -1
    read = 0
    blocknum = 0
    req = request.Request(url, headers = fake_headers)
    response = request.urlopen(req, None)
    if "content-length" in response.headers:
        size = int(response.headers["Content-Length"])
    reporthook(blocknum, bs, size)
    tfp = open(name, 'wb')
    while True:
        block = response.read(bs)
        if not block:
            break
        read += len(block)
        tfp.write(block)
        blocknum += 1
        reporthook(blocknum, bs, size)

def save_urls(urls, name, ext):
    no = 0
    for u in urls:
        print("Download: " + name + " part %d" % no)
        n = name + '_%02d_.' % no + ext
        if os.path.exists(n):
            print('Skipping Part %d: file already exists', no)
        else:
            save_url(u, n)
            print()
        no += 1
