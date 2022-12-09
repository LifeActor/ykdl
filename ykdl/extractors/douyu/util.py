# -*- coding: utf-8 -*-

from .._common import *

assert JSEngine, "No JS Interpreter found, can't extract douyu live/video!"


# REF: https://cdnjs.com/libraries/crypto-js
js_md5 = get_pkgdata_str(__name__, 'crypto-js-md5.min.js',
        'https://cdnjs.cloudflare.com/ajax/libs/crypto-js/3.1.9-1/crypto-js.min.js')

def get_h5enc(html, rid):
    js_enc = match1(html, '(var vdwdae325w_64we =[\s\S]+?)\s*</script>')
    if js_enc is None or 'ub98484234(' not in js_enc:
        data = get_response('https://www.douyu.com/swf_api/homeH5Enc',
                            params={'rids': rid}).json()
        assert data['error'] == 0, data['msg']
        js_enc = data['data']['room' + rid]
    return js_enc

def ub98484234(js_enc, rid, logger, params):
    names_dict = {
        'debugMessages': get_random_name(8),
        'decryptedCodes': get_random_name(8),
        'patchCode': get_random_name(8),
        'resoult': get_random_name(8),
        '_ub98484234': get_random_name(8),
        'workflow': match1(js_enc, 'function ub98484234\(.+?\Weval\((\w+)\);'),
    }
    js_dom = '''
    {debugMessages} = {{{decryptedCodes}: []}};
    if (!this.window) {{window = {{}};}}
    if (!this.document) {{document = {{}};}}
    '''.format(**names_dict)
    js_patch = ['''
    function {patchCode}(workflow) {{
        let testVari = /(\w+)=(\w+)\([\w\+]+\);.*?(\w+)="\w+";/.exec(workflow);
        if (testVari && testVari[1] == testVari[2]) {{
            workflow += `${{testVari[1]}}[${{testVari[3]}}] = function() {{return true;}};`;
        }}
        let subWorkflow = /(?:\w+=)?eval\((\w+)\)/.exec(workflow);
        if (subWorkflow) {{
            let subPatch = `
                {debugMessages}.{decryptedCodes}.push('sub workflow: ' + subWorkflow);
                subWorkflow = {patchCode}(subWorkflow);
            `.replace(/subWorkflow/g, subWorkflow[1]) + subWorkflow[0];
            workflow = workflow.replace(subWorkflow[0], subPatch);
        }}
        return workflow;
    }}
    '''.format(**names_dict), '''
    {debugMessages}.{decryptedCodes}.push({workflow});
    eval({patchCode}({workflow}));
    '''.format(**names_dict)]
    js_debug = '''
    var {_ub98484234} = ub98484234;
    ub98484234 = function(p1, p2, p3) {{
        try {{
            let resoult = {_ub98484234}(p1, p2, p3);
            {debugMessages}.{resoult} = resoult;
        }} catch(e) {{
            {debugMessages}.{resoult} = e.message;
        }}
        return {debugMessages};
    }};
    '''.format(**names_dict)

    js_ctx = JSEngine()
    js_ctx.append(js_md5)
    js_ctx.append(js_dom)
    if names_dict['workflow']:
        js_ctx.append(js_patch[0])
        js_ctx.append(js_enc.replace('eval({workflow});'.format(**names_dict), js_patch[1]))
    else:
        js_ctx.append(js_enc)
    js_ctx.append(js_debug)

    did = get_random_uuid_hex()
    tt = str(int(time.time()))
    ub98484234 = js_ctx.call('ub98484234', rid, did, tt)
    ub98484234 = {
        'decryptedCodes': ub98484234[names_dict['decryptedCodes']],
        'resoult': ub98484234[names_dict['resoult']]
    }
    logger.debug('ub98484234: %s', ub98484234)
    ub98484234 = ub98484234['resoult']
    params.update({
        'v': match1(ub98484234, 'v=(\d+)'),
        'did': did,
        'tt': tt,
        'sign': match1(ub98484234, 'sign=(\w{32})')
    })
