'''A simple XML document parser which used builtin expat, output a dict with
 Python data type, likes json package.'''

from logging import getLogger


logger = getLogger(__name__)

_cdict = {  # special objects
     'true': True,
    'false': False,
      'NaN': float('nan'),
      'INF': float('inf'),
     '-INF': float('-inf')
}
xml_schema_instance = 'http://www.w3.org/2001/XMLSchema-instance'

def _convert(text):
    if text in _cdict:
        return _cdict[text]
    if text.isdecimal():
        return int(text)
    if text.count('e') == 1 or text.count('.') == 1:
        try:
            f = float(text)
        except ValueError:
            pass
        else:
            if text.count('e') and not f % 1:
                return int(f)  # e.g. 2.2e2 => 220
            return f
    return text

def _get1(l):
    # unpack standalone element from list
    if isinstance(l, list) and len(l) == 1:
        o = l[0]
        if not isinstance(o, dict):  # contribute to compatibility
            return o
    return l

def xml2dict(source):
    '''Convert giving XML document to a dict object.'''
    from xml.parsers import expat
    # don't expand namespace, handle them ourself
    parser = expat.ParserCreate(namespace_separator=None)
    parser.buffer_text = True
    root = {'#text': []}
    xml = {  # default properties
        'version': '1.0',
        'encoding': 'UTF-8',
        'standalone': -1,
        'rootname': 'root',
        'root': root,
        }
    parent_nodes = []
    isCDATA = False

    def default(data):
        if data.strip():
            logger.debug('Unhandled XML data: %r', data)

    def startXML(version, encoding, standalone):
        xml['version'] = version
        xml['encoding'] = encoding
        xml['standalone'] = standalone

    def getNSPrefix(ns):
        nodes = parent_nodes.copy()
        while nodes:
            xmlns = nodes.pop().get('@xmlns')
            if ns in xmlns:
                return xmlns[ns]

    def sortAttributes(attributes):
        if not attributes:
            return {}
        xmlns = {}
        attrs = {}
        for k, v in attributes.items():
            ks = k.split(':', 1)
            if ks[0] == 'xmlns':
                if len(ks) == 2 :
                    k = ks[1]
                    assert k, 'Missing namespace declaration prefix!'
                else:
                    k = ''
                xmlns[k] = v
            else:
                attrs['@' + k] = _convert(v)
        if xmlns:
            attrs['@xmlns'] = xmlns
        return attrs

    def startRoot(name, attributes):
        xml['rootname'] = name
        parent_nodes.append(root)
        if attributes:
            root.update(sortAttributes(attributes))

    def startElement(name, attributes):
        if not parent_nodes:
            return startRoot(name, attributes)
        node = sortAttributes(attributes)
        node['#text'] = []
        parent_node = parent_nodes[-1]
        if name not in parent_node:
            parent_node[name] = []
        parent_node[name].append(node)
        parent_nodes.append(node)

    def startCDATA():
        nonlocal isCDATA
        isCDATA = True

    def endCDATA():  # void handle to skip default
        pass

    def characters(data):
        data = data.strip()
        if data:
            parent_nodes[-1]['#text'].append(data)

    def endElement(name):

        def replaceNode(data):
            parent_node = parent_nodes[-1][name]
            assert parent_node.pop() is node, 'Unkown error during endElement()'
            parent_node.append(data)

        nonlocal isCDATA
        node = parent_nodes.pop()
        if node.get('@xsi:nil') in (True, 1) and \
                                    getNSPrefix('xsi') == xml_schema_instance:
            replaceNode(None)
        else:
            text = node.pop('#text')
            if node:
                node.update({k: _get1(v) for k, v in node.items()})
            if text:
                name = parent_nodes and name or None
                if name and not node and len(text) == 1 and not isCDATA:
                    data = _convert(text[0])  # no attributes & sub-elements
                else:
                    data = '\n'.join(text)  # prefer a string than a list
                if name and not node:
                    replaceNode(data)  # no attributes & sub-elements
                else:
                    node['#text'] = data
            elif not node:
                replaceNode('')  # placeholder use to keep the structure
        isCDATA = False  # ends here, not CDATA's end

    parser.DefaultHandler = default
    parser.XmlDeclHandler = startXML
    parser.StartElementHandler = startElement
    parser.EndElementHandler = endElement
    parser.StartCdataSectionHandler = startCDATA
    parser.EndCdataSectionHandler = endCDATA
    parser.CharacterDataHandler = characters

    if isinstance(source, str):
        parser.Parse(source, True)
    elif hasattr(source, 'read'):
        parser.ParseFile(source)
    else:
        for s in source:
            parser.Parse(s, False)
        parser.Parse(type(s)(), True)
    return xml
