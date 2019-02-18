#!/usr/bin/env python

'''
    Simple Javascript engines' wrapper
    
    Description:
        This library wraps the system's built-in Javascript interpreter to python.
        macOS: Use JavascriptCore
        Linux: Use gjs on Gnome, cjs on Cinnamon or NodeJS if installed
        Windows: Currently not implemented
    
    Usage:
        ctx = JSEngine()
        ctx.eval('1 + 1')  # => 2
    
        ctx2 = JSEngine("""
            function add(x, y) {
            return x + y;
        }
        """)
        ctx2.call("add", 1, 2)  # => 3
'''

from subprocess import Popen, PIPE
from os.path import isfile
import io
import json
import os
import platform
import re
import tempfile

# Exceptions
class ProgramError(Exception):
    pass

class RuntimeError(Exception):
    pass


# Choose javascript interpreter
# macOS: use built-in JavaScriptCore
if platform.system() == 'Darwin':
    interpreter = ['/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Resources/jsc']
# Linux: use gjs on Gnome, cjs on Cinnamon or NodeJS if installed
elif platform.system() == 'Linux':
    if isfile('/usr/bin/gjs') or isfile('/usr/local/bin/gjs' or isfile('/app/bin/gjs')):
        interpreter = ['gjs']
    elif isfile('/usr/bin/cjs') or isfile('/usr/local/bin/cjs' or isfile('/app/bin/cjs')):
        interpreter = ['cjs']
    elif isfile('/usr/bin/nodejs') or isfile('/usr/local/bin/nodejs' or isfile('/app/bin/nodejs')):
        interpreter = ['nodejs']
    else:
        raise RuntimeError('Please install at lease one of the following Javascript interpreter: gjs, cjs, nodejs')
else:
    raise RuntimeError('Sorry, the Javascript engine is currently not supported on your system')


# Inject to the script to let it return jsonlized value to python
injected_script = r'''
(function(program, execJS) { execJS(program) })(
function() {
    return eval(#{encoded_source});
},
function(program) {
    var output;
    try {
        result = program();
        print("");
        if (typeof result == 'undefined' && result !== null) {
            print('["ok", 0]');
        }
        else {
            try {
                print(JSON.stringify(['ok', result]));
            }
            catch (err) {
                print('["err", 0]');
            }
        }
    }
    catch (err) {
        print(JSON.stringify(['err', '' + err]));
    }
});
'''

class JSEngine:
    def __init__(self, source = None):
        self._source = source
    
    def call(self, identifier, *args):
        args = json.dumps(args)
        return self.eval("{identifier}.apply(this, {args})".format(identifier=identifier, args=args))
        
    def eval(self, code = None):
        if code is None or not code.strip():
            data = "''"
        else:
            data = "'('+" + json.dumps(code, ensure_ascii=True) + "+')'"
        code = 'return eval({data})'.format(data=data)
        return self._exec(code)
    
    def _exec(self, code):
        if self._source:
            code = self._source + '\n' + code
        code = self._inject_script(code)
        output = self._run_interpreter_with_tempfile(code)
        output = output.replace('\r\n', '\n').replace('\r', '\n')
        last_line = output.split('\n')[-2]
        ret = json.loads(last_line)
        status, value = ret
        if status == 'ok':
            return value
        else:
            raise ProgramError(value)
        
    def _run_interpreter_with_tempfile(self, code):
        (fd, filename) = tempfile.mkstemp(prefix='execjs', suffix='.js')
        os.close(fd)
        try:
            # decoding in python2
            try:
                code = code.decode('utf8')
            except:
                pass
            with io.open(filename, 'w', encoding='utf8') as fp:
                fp.write(code)
            
            cmd = interpreter + [filename]
            p = None
            try:
                p = Popen(cmd, stdout=PIPE, universal_newlines=True)
                stdoutdata, stderrdata = p.communicate()
                ret = p.wait()
            finally:
                del p
            return stdoutdata
        finally:
            os.remove(filename)

    def _inject_script(self, source):
        encoded_source = \
            "(function(){ " + \
            encode_unicode_codepoints(source) + \
            " })()"
        return injected_script.replace('#{encoded_source}', json.dumps(encoded_source))


def encode_unicode_codepoints(str):
    codepoint_format = '\\u{0:04x}'.format
    def codepoint(m):
        return codepoint_format(ord(m.group(0)))
    return re.sub('[^\x00-\x7f]', codepoint, str)
