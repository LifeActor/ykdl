# -*- coding: utf-8 -*-

from ._common import *


assert JSEngine, "No JS Interpreter found, can't load byted acrawler!"

js_acrawler = get_pkgdata_str(__name__, '_byted_acrawler.js',
              'https://lf3-cdn-tos.bytescm.com/obj/rc-web-sdk/acrawler.js')

js_dom = '''
var window = this,
    document = {{referrer: '{url}'}},
    location = {{href: '{url}', protocol: 'https'}},
    navigator = {{userAgent: '{ua}'}};
'''

def get_signer(url):
    js_ctx = JSEngine(js_dom.format(url=url, ua=fake_headers['User-Agent']))
    js_ctx.append(js_acrawler)

    def sign(*args):
        return js_ctx.call('byted_acrawler.sign', *args)

    return sign

def get_signed_cookies(url):
    install_cookie()
    get_response(url)
    __ac_nonce = get_cookie(urlsplit(url).hostname, '/', '__ac_nonce').value
    cookies = {
        '__ac_nonce': __ac_nonce,
        '__ac_signature': get_signer(url)('', __ac_nonce),
        '__ac_referer': '__ac_blank'
    }
    uninstall_cookie()
    return ';'.join('='.join(kv) for kv in cookies.items())
