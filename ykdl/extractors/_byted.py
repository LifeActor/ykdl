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

def cd2cs(cd):
    return ';'.join('='.join(kv) for kv in cd.items())

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
    assert JSEngine, "No JS Interpreter found, can't load byted acrawler!"
    install_cookie()
    get_response(url)
    cookies = get_cookies_d(url)
    cookies.update({
        '__ac_signature': get_signer(url)('', cookies['__ac_nonce']),
        '__ac_referer': '__ac_blank'
    })
    uninstall_cookie()
    return cd2cs(cookies)

def get_ttwid_cookies(url):
    install_cookie()
    get_response(url)
    cookies = get_cookies_d(url)
    cookies['ttwid_date'] = '1'
    get_response(url, headers={'Cookie': cd2cs(cookies)})
    cookies = get_cookies_d(url)
    uninstall_cookie()
    return cd2cs(cookies)

cookies = None
_get_content = get_content

def get_content(url):
    global cookies
    if cookies is None:
        if 'douyin.' in url:
            cookies = get_signed_cookies(url)
        elif 'ixigua.' in url:
            cookies = get_ttwid_cookies(url)
    return _get_content(url, headers={'Cookie': cookies})
