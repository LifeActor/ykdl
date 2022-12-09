# -*- coding: utf-8 -*-

from ..._common import *

from Crypto.Cipher import AES


#consts here
first_key = '0CoJUm6Qyw8W8jud'
iv = '0102030405060708'

def pksc7_padding(string):
    aes_block_size = 16
    padding_size = aes_block_size - len(string) % 16
    return string.ljust(len(string)+padding_size, chr(padding_size))

def make_json_data(url_id):
    fixed = {}
    fixed['br'] = 128000
    fixed['csrf_token'] = '' #in the cookie
    fixed['ids'] = '[{}]'.format(url_id)
    return json.dumps(fixed, separators=(',', ':'))

def RSA_string(input_str):
    modular = 157794750267131502212476817800345498121872783333389747424011531025366277535262539913701806290766479189477533597854989606803194253978660329941980786072432806427833685472618792592200595694346872951301770580765135349259590167490536138082469680638514416594216629258349130257685001248172188325316586707301643237607
    exp = 65537

    #first do LE packing
    to_number = 0
    rev_str = input_str[::-1]
    for i in rev_str:
        to_number = to_number * 256 + ord(i)
    #then calc ras with exp and modular
    encSecKey = hex(pow(to_number, exp, modular))[2:]
    return encSecKey.rjust(256, '0')

def AES_128_CBC_b64_wrapper(data, key, iv):
    obj = AES.new(key.encode(), AES.MODE_CBC, iv.encode())
    input_data = pksc7_padding(data)
    out = obj.encrypt(input_data.encode())
    return base64.b64encode(out).decode()

def netease_req(ids='468490608', snd_key=None, encSecKey=None):
    data = make_json_data(ids)
    if snd_key is None:
        snd_key = get_random_str(16, 'snd_key')
        encSecKey = RSA_string(snd_key)
    first_pass = AES_128_CBC_b64_wrapper(data, first_key, iv)
    second_pass = AES_128_CBC_b64_wrapper(first_pass, snd_key, iv)

    payload = {}
    payload['params'] = second_pass
    payload['encSecKey'] = encSecKey

    return payload

class NeteaseMusicBase(Extractor):

    def prepare_mid(self):
        return match1(self.url, r'\bid=(\w+)', 'song/(\d+)')

    def prepare(self):
        info = MediaInfo(self.name)

        data = get_response(self.api_url, params={
                                              'id': self.mid,
                                             'ids': self.mid,
                                      'csrf_token': ''
                                          }).json()
        data = self.get_music(data)
        self.logger.debug('data:\n%s', data)

        info.title = data['name']
        info.artist = data['artists'][0]['name']

        real_id = data['id']
        snd_key = get_random_str(16, 'snd_key')
        encSecKey = RSA_string(snd_key)
        payload = netease_req(real_id, snd_key, encSecKey)
        data = get_response(
            'http://music.163.com/weapi/song/enhance/player/url?csrf_token=',
            data=payload).json()['data'][0]
        self.logger.debug('mp3 data:\n%s', data)

        info.streams['current'] =  {
            'container': data['type'],
            'profile': 'current',
            'src' : [data['url']],
            'size': data['size']
        }

        return info
