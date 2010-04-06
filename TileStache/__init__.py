""" A stylish alternative for caching your tiles.


"""

import re

from os import environ
from cgi import parse_qs
from sys import stderr, stdout
from StringIO import StringIO

from ModestMaps.Core import Coordinate

import IO

# regular expression for PATH_INFO
_pathinfo_pat = re.compile(r'^/(?P<l>.+)/(?P<z>\d+)/(?P<x>\d+)/(?P<y>\d+)\.(?P<e>\w+)$')

def handleRequest(layer, coord, extension):
    """ Get a type string and image binary for a given request layer, coordinate, and file extension.
    
        This is the main entry point, after site configuration has been loaded
        and individual tiles need to be rendered.
    """
    mimetype, format = IO.getTypeByExtension(extension)
    
    body = layer.config.cache.read(layer, coord, format)
    
    if body is None:
        out = StringIO()
        img = layer.render(coord)
        img.save(out, format)
        body = out.getvalue()
        
        layer.config.cache.save(body, layer, coord, format)

    return mimetype, body

def cgiHandler(debug=False):
    """ Load up configuration and talk to stdout by CGI.
    """
    if debug:
        import cgitb
        cgitb.enable()
    
    path = _pathinfo_pat.match(environ['PATH_INFO'])
    layer, row, column, zoom, extension = [path.group(p) for p in 'lyxze']
    config = IO.parseConfigfile('tilestache.cfg')
    
    coord = Coordinate(int(row), int(column), int(zoom))
    query = parse_qs(environ['QUERY_STRING'])
    layer = config.layers[layer]
    
    mimetype, content = handleRequest(layer, coord, extension)
    
    print >> stdout, 'Content-Length: %d' % len(content)
    print >> stdout, 'Content-Type: %s\n' % mimetype
    print >> stdout, content
