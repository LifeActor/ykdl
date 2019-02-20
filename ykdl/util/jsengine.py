#!/usr/bin/env python

'''
    Simple Javascript engines' wrapper
    
    Description:
        This library wraps the system's built-in Javascript interpreter to python.

    Platform:
        macOS:   Use JavascriptCore
        Linux:   Use gjs on Gnome, cjs on Cinnamon or NodeJS if installed
        Windows: Use NodeJS if available
    
    Usage:
    
        from jsengine import JSEngine, javascript_is_supported
        
        if not javascript_is_supported:  # always check this first!
            ......
        
        ctx = JSEngine()
        ctx.eval('1 + 1')  # => 2
    
        ctx2 = JSEngine("""
            function add(x, y) {
            return x + y;
        }
        """)
        ctx2.call("add", 1, 2)  # => 3
'''

from __future__ import print_function
from distutils.spawn import find_executable
from subprocess import Popen, PIPE
import io
import json
import os
import platform
import re
import sys
import tempfile

### Before using this library, check this variable first!!!
javascript_is_supported = True

# Exceptions
class ProgramError(Exception):
    pass

class RuntimeError(Exception):
    pass


# Choose javascript interpreter
# macOS: use built-in JavaScriptCore
if platform.system() == 'Darwin':
    interpreter = ['/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Resources/jsc']

# Windows: prefer Node.js, if not found use Windows Script Host
elif platform.system() == 'Windows':
    if find_executable('node') is not None:
        interpreter = ['node']
    else:
        print('Please install Node.js!', file=sys.stderr)
        javascript_is_supported = False

# Linux: use gjs on Gnome, cjs on Cinnamon or NodeJS if installed
elif platform.system() == 'Linux':
    if find_executable('gjs') is not None:
        interpreter = ['gjs']
    elif find_executable('cjs') is not None:
        interpreter = ['cjs']
    elif find_executable('nodejs') is not None:
        interpreter = ['nodejs']
    elif find_executable('node') is not None:
        interpreter = ['node']
    else:
        print('Please install at least one of the following Javascript interpreter: gjs, cjs, nodejs', file=sys.stderr)
        javascript_is_supported = False
else:
    print('Sorry, the Javascript engine is currently not supported on your system', file=sys.stderr)
    javascript_is_supported = False



# Inject to the script to let it return jsonlized value to python
if interpreter[0] == 'cscript':
    injected_script = r'''
    (function(program, execJS) { execJS(program) })(
    function() {
        return eval(#{encoded_source});
    },
    function(program) {
        #{json2_source}
        var output, print = function(string) {
            string = string.replace(/[^\x00-\x7f]/g, function(ch){
                return '\\u' + ('0000' + ch.charCodeAt(0).toString(16)).slice(-4);
            });
            WScript.Echo(string);
        };
        try {
            result = program();
            print("")
            if (typeof result == 'undefined' && result !== null) {
                print('["ok"]');
            }
            else {
                try {
                    print(JSON.stringify(['ok', result]));
                }
                catch (err) {
                    print('["err", "Script returns a value with an unknown type"]');
                }
            }
        }
        catch (err) {
            print(JSON.stringify(['err', err.name + ': ' + err.message]));
        }
    });
    '''
    json2_source = 'var JSON;if(!JSON){JSON={}}(function(){function f(n){return n<10?"0"+n:n}if(typeof Date.prototype.toJSON!=="function"){Date.prototype.toJSON=function(key){return isFinite(this.valueOf())?this.getUTCFullYear()+"-"+f(this.getUTCMonth()+1)+"-"+f(this.getUTCDate())+"T"+f(this.getUTCHours())+":"+f(this.getUTCMinutes())+":"+f(this.getUTCSeconds())+"Z":null};String.prototype.toJSON=Number.prototype.toJSON=Boolean.prototype.toJSON=function(key){return this.valueOf()}}var cx=/[\\u0000\\u00ad\\u0600-\\u0604\\u070f\\u17b4\\u17b5\\u200c-\\u200f\\u2028-\\u202f\\u2060-\\u206f\\ufeff\\ufff0-\\uffff]/g,escapable=/[\\\\\\"\\x00-\\x1f\\x7f-\\x9f\\u00ad\\u0600-\\u0604\\u070f\\u17b4\\u17b5\\u200c-\\u200f\\u2028-\\u202f\\u2060-\\u206f\\ufeff\\ufff0-\\uffff]/g,gap,indent,meta={"\\b":"\\\\b","\\t":"\\\\t","\\n":"\\\\n","\\f":"\\\\f","\\r":"\\\\r",\'"\':\'\\\\"\',"\\\\":"\\\\\\\\"},rep;function quote(string){escapable.lastIndex=0;return escapable.test(string)?\'"\'+string.replace(escapable,function(a){var c=meta[a];return typeof c==="string"?c:"\\\\u"+("0000"+a.charCodeAt(0).toString(16)).slice(-4)})+\'"\':\'"\'+string+\'"\'}function str(key,holder){var i,k,v,length,mind=gap,partial,value=holder[key];if(value&&typeof value==="object"&&typeof value.toJSON==="function"){value=value.toJSON(key)}if(typeof rep==="function"){value=rep.call(holder,key,value)}switch(typeof value){case"string":return quote(value);case"number":return isFinite(value)?String(value):"null";case"boolean":case"null":return String(value);case"object":if(!value){return"null"}gap+=indent;partial=[];if(Object.prototype.toString.apply(value)==="[object Array]"){length=value.length;for(i=0;i<length;i+=1){partial[i]=str(i,value)||"null"}v=partial.length===0?"[]":gap?"[\\n"+gap+partial.join(",\\n"+gap)+"\\n"+mind+"]":"["+partial.join(",")+"]";gap=mind;return v}if(rep&&typeof rep==="object"){length=rep.length;for(i=0;i<length;i+=1){if(typeof rep[i]==="string"){k=rep[i];v=str(k,value);if(v){partial.push(quote(k)+(gap?": ":":")+v)}}}}else{for(k in value){if(Object.prototype.hasOwnProperty.call(value,k)){v=str(k,value);if(v){partial.push(quote(k)+(gap?": ":":")+v)}}}}v=partial.length===0?"{}":gap?"{\\n"+gap+partial.join(",\\n"+gap)+"\\n"+mind+"}":"{"+partial.join(",")+"}";gap=mind;return v}}if(typeof JSON.stringify!=="function"){JSON.stringify=function(value,replacer,space){var i;gap="";indent="";if(typeof space==="number"){for(i=0;i<space;i+=1){indent+=" "}}else{if(typeof space==="string"){indent=space}}rep=replacer;if(replacer&&typeof replacer!=="function"&&(typeof replacer!=="object"||typeof replacer.length!=="number")){throw new Error("JSON.stringify")}return str("",{"":value})}}if(typeof JSON.parse!=="function"){JSON.parse=function(text,reviver){var j;function walk(holder,key){var k,v,value=holder[key];if(value&&typeof value==="object"){for(k in value){if(Object.prototype.hasOwnProperty.call(value,k)){v=walk(value,k);if(v!==undefined){value[k]=v}else{delete value[k]}}}}return reviver.call(holder,key,value)}text=String(text);cx.lastIndex=0;if(cx.test(text)){text=text.replace(cx,function(a){return"\\\\u"+("0000"+a.charCodeAt(0).toString(16)).slice(-4)})}if(/^[\\],:{}\\s]*$/.test(text.replace(/\\\\(?:["\\\\\\/bfnrt]|u[0-9a-fA-F]{4})/g,"@").replace(/"[^"\\\\\\n\\r]*"|true|false|null|-?\\d+(?:\\.\\d*)?(?:[eE][+\\-]?\\d+)?/g,"]").replace(/(?:^|:|,)(?:\\s*\\[)+/g,""))){j=eval("("+text+")");return typeof reviver==="function"?walk({"":j},""):j}throw new SyntaxError("JSON.parse")}}}());'
    injected_script = injected_script.replace('#{json2_source}', json2_source)
else:
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
                print('["ok"]');
            }
            else {
                try {
                    print(JSON.stringify(['ok', result]));
                }
                catch (err) {
                    print('["err", "Script returns a value with an unknown type"]');
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
        if len(ret) == 1:
            return None
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
            if ret != 0:
                raise RuntimeError('Javascript interpreter returns non-zero value!')
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
