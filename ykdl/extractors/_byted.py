# -*- coding: utf-8 -*-

from ._common import *


js_dom = '''
var window = this,
    document = {{referrer: '{url}'}},
    location = {{href: '{url}', protocol: 'https'}},
    navigator = {{userAgent: '{ua}'}};
'''
js_acrawler = None

def get_cookies_d(url):
    return {c.name: c.value
            for c in get_cookies(urlsplit(url).hostname, '/')}

def get_signer(url):
    assert JSEngine, "No JS Interpreter found, can't load byted acrawler!"
    global js_acrawler
    if js_acrawler is None:
        js_acrawler = get_pkgdata_str(__name__, '_byted_acrawler.js',
                      'https://lf3-cdn-tos.bytescm.com/obj/rc-web-sdk/acrawler.js')

    js_ctx = JSEngine(js_dom.format(url=url, ua=fake_headers['User-Agent']))
    js_ctx.append(js_acrawler)

    def sign(*args):
        return js_ctx.call('byted_acrawler.sign', *args)

    return sign

def get_signed_cookies(url):
    #assert JSEngine, "No JS Interpreter found, can't load byted acrawler!"
    __ac_nonce = get_random_id(21)
    _cookies['signed'] = cookies = {
        '__ac_nonce': __ac_nonce,
        #'__ac_signature': get_signer(url)('', __ac_nonce),
        #'__ac_referer': '__ac_blank'
    }
    return cookies

def get_ttwid_cookies(url):
    install_cookie()
    _cookies['ttwid'] = cookies = {
        '__ac_nonce': get_random_id(21),
        'ttwid_date': '1'
    }
    get_response(url, headers={'Cookie': cookies})
    cookies.update(get_cookies_d(url))
    uninstall_cookie()
    return cookies

_cookies = {}
_get_content = get_content

def get_content(url):
    if 'douyin.' in url:
        cookies = _cookies.get('signed') or get_signed_cookies(url)
    elif 'ixigua.' in url:
        cookies = _cookies.get('ttwid') or get_ttwid_cookies(url)
    return _get_content(url, headers={'Cookie': cookies})
