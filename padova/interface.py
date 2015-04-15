#!/usr/bin/env python
# encoding: utf-8
"""
Maps for cmd interface settings

Code adapted from ezpadova - Morgan Fousneau, MIT License
"""

from __future__ import print_function, unicode_literals, division

import sys

if sys.version_info[0] > 2:
    py3k = True
    from urllib.parse import urlencode
    from urllib import request
    from urllib.request import urlopen
    from io import StringIO
    from html import parser
else:
    py3k = False
    from urllib import urlencode
    from urllib2 import urlopen
    from StringIO import StringIO
    import HTMLParser as parser

import zlib
import re

from padova.resultcache import PadovaCache
from padova.utils import compression_type
from padova.isocdata import IsochroneSet


class CMDRequest(object):
    """Python interface to the Padova group's CMD web interface for isochrones.

    Parameters
    ----------
    settings : :class:`padova.settings.Settings`
        A settings instance loaded with user settings.
    """
    def __init__(self, settings):
        super(CMDRequest, self).__init__()
        self._cache = PadovaCache()
        self.settings = settings
        if self.settings in self._cache:
            # Get request from the cache
            # print("Reading from cache")
            self._r = self._cache[self.settings]
        else:
            # Call API and cache it
            self._r = self._request()
            self._cache[self.settings] = self._r
        self._isochrone_set = None

    def _request(self):
        """Request isochromes from CMD."""
        webserver = 'http://stev.oapd.inaf.it'
        # FIXME convert to log
        # print('Requesting from {0}...'.format(webserver))
        url = webserver + '/cgi-bin/cmd'
        q = urlencode(self.settings.settings)
        if py3k:
            req = request.Request(url, q.encode('utf8'))
            c = urlopen(req).read().decode('utf8')
        else:
            c = urlopen(url, q).read()
        # Find the output dataset URL in the HTML that CMD returns
        aa = re.compile('output\d+')
        fname = aa.findall(c)
        if len(fname) > 0:
            url = '{0}/~lgirardi/tmp/{1}.dat'.format(webserver, fname[0])
            # FIXME convert to log
            # print('Downloading data...{0}'.format(url))
            bf = urlopen(url)
            r = bf.read()
            # Decompress the data if necessary
            typ = compression_type(r, stream=True)
            if typ is not None:
                r = zlib.decompress(bytes(r), 15 + 32)
            return r
        else:
            # print(c)
            print(url + q)
            if "errorwarning" in c:
                p = CMDErrorParser()
                p.feed(c)
                print('\n', '\n'.join(p.data).strip())
            raise RuntimeError('Server Response is incorrect')

    @property
    def isochrone_set(self):
        """IsochroneSet table with the isochrones."""
        if self._isochrone_set is None:
            f = StringIO(self._r)
            self._isochrone_set = IsochroneSet(f)
        return self._isochrone_set

    @property
    def data(self):
        return self._r


class CMDErrorParser(parser.HTMLParser):
    """Find error box in the recent version of CMD website."""
    def handle_starttag(self, tag, attrs):
        if (tag == "p") & (dict(attrs).get('class', None) == 'errorwarning'):
            self._record = True
            self.data = []

    def handle_endtag(self, tag):
        if (tag == "p") & getattr(self, '_record', False):
            self._record = False

    def handle_data(self, data):
        if getattr(self, '_record', False):
            self.data.append(data)
