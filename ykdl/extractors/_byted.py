# -*- coding: utf-8 -*-

from ._common import *


# result length is incorrect
#
#js_dom = '''
#var window = this,
#    document = {{referrer: 'http://www.douyin.com/'}},
#    location = {{href: '{url}', protocol: 'https'}},
#    navigator = {{userAgent: '{ua}'}};
#'''
#js_acrawler = None
#
#def get_acrawler_signer(url):
#    assert JSEngine, "No JS Interpreter found, can't load byted acrawler!"
#    global js_acrawler
#    if js_acrawler is None:
#        js_acrawler = get_pkgdata_str(__name__, '_byted_acrawler.js',
#                      'https://lf3-cdn-tos.bytescm.com/obj/rc-web-sdk/acrawler.js')
#
#    js_ctx = JSEngine(js_dom.format(url=url, ua=fake_headers['User-Agent']))
#    js_ctx.append(js_acrawler)
#
#    def sign(*args):
#        return js_ctx.call('byted_acrawler.sign', *args)
#
#    return sign
#
#def get_acrawler_cookies(url):
#    assert JSEngine, "No JS Interpreter found, can't load byted acrawler!"
#    install_cookie()
#    __ac_nonce = get_random_id(21)
#    _cookies['signed'] = cookies = {
#        '__ac_nonce': __ac_nonce,
#        '__ac_signature': get_acrawler_signer(url)('', __ac_nonce),
#        '__ac_referer': '__ac_blank'
#    }
#    _get_response(url, headers={'Cookie': cookies}, cache=False)
#    cookies.update(get_cookies_d(url))
#    uninstall_cookie()
#    return cookies


def generate_mstoken():
    ms = base64.b64encode(os.urandom(random.randrange(91,100))) \
                        .decode().replace('+','9').replace('/','9').rstrip('=')
    if len(ms) <= 128:
        ms += '=='
    while len(ms) < 132:
        i = random.randrange(128)
        c = random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
        p = random.choice('-_')
        ms = ms[:i] + ms[i:].replace(c, c+p, 1)
    return ms

def sign_xbogus(params, ua):
    assert JSEngine, "No JS Interpreter found, can't load byted X-Bogus util!"
    if not isinstance(params, str):
        params = urlencode(params)
    js_ctx = JSEngine(get_pkgdata_str(__name__, '_byted_X-Bogus.js'))
    return js_ctx.call('sign', params, ua)

def get_cookies_d(url):
    return {c.name: c.value
            for c in get_cookies(urlsplit(url).hostname, '/')}

def get_nonce_cookies():
    __ac_nonce = get_random_id(21)
    _cookies['nonce'] = cookies = {
        '__ac_nonce': __ac_nonce,
    }
    return cookies

def get_ttwid_cookies(url):
    install_cookie()
    _cookies['ttwid'] = cookies = {
        '__ac_nonce': get_random_id(21),
        'ttwid_date': '1'
    }
    _get_response(url, headers={'Cookie': cookies}, cache=False)
    cookies.update(get_cookies_d(url))
    uninstall_cookie()
    return cookies

_cookies = {}
_get_response = get_response
_get_content = get_content

def get_response(url, *args, **kwargs):
    if 'live.douyin.' in url:
        cookies = _cookies.get('nonce') or get_nonce_cookies(url)
    elif 'ixigua.' in url:
        cookies = _cookies.get('ttwid') or get_ttwid_cookies(url)
    kwargs.setdefault('headers', {})['Cookie'] = cookies
    return _get_response(url, *args, **kwargs)

def get_content(*args, **kwargs):
    response = get_response(*args, **kwargs)
    if kwargs.get('encoding') == 'ignore':
        return response.content
    return response.text
