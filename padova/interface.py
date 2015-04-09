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
import hashlib
import re

from padova.resultcache import PadovaCache
from padova.utils import compression_type
from padova.isocdata import IsochroneSet

from padova.settings import INTERP, PHOT, MODELS, CARBON_STARS, \
    CIRCUM_MSTARS, CIRCUM_CSTARS, ISOC_VAL, get_defaults


class CMDRequest(object):
    """Python interface to the Padova group's CMD web interface for isochrones.

    Parameters for this CMD interface match those of the web form.

    Parameters
    ----------
    isoc_kind : str
        Base isochrone evolution tracks. Can be:
        - ``'parsec_CAF09_v1.1'``
        - ``'parsec_CAF09_v1.0'``
        - ``'gi10a'``
        - ``'gi10b'``
        - ``'ma08'``
        - ``'gi2000'``
    photsys_file : str
        Filename of filter set.
    kind_cspecmag : str
        Carbon star bolometric corrections.
    dust_sourceM : str
        Circumstellar dust for M-type AGB stars.
    dust_sourceC : str
        Circumstellar dust for C-type AGB stars.
    extinction_av : float or str
        Extinction, in V-band.
    imf_file : str
        Filename of IMF specification.
    isoc_val : int
        Select type of output.
        - ``0``: single age/metallicity isochrone.
        - ``1``: sequence of isochrones of constant metallicity.
        - ``2``: sequence of isochrones of constant age.
    isoc_age : float or str
        Log age of isochrone if ``isoc_val == 0``.
    isoc_zeta : float or str
        Metallicity of isochrone if ``isoc_val == 0``.
    isoc_zeta : int
        Metallicity of isochrones if ``isoc_val == 1``.
    isoc_lage0 : float or str
        Initial log(age) of isochrones if ``isoc_val == 1``.
    isoc_lage1 : float or str
        Final log(age) of isochrones if ``isoc_val == 1``.
    isoc_dlage : float or str
        Bin width in log(age) of isochrone grid if ``isoc_val == 1``.
    isoc_age0 : float or str
        Age (in years) of isochrones if ``isoc_val == 2``.
    isoc_z0 : float or str
        Initial metallicity of isochrones if ``isoc_val == 2``.
    isoc_z1 : float or str
        Final metallicity of isochrones if ``isoc_val == 2``.
    isoc_dz : float or str
        Metallicity step size if ``isoc_val == 2``.
    output_kind : int
        Output type. Can be:
        - ``0``: isochrone tables
        - ``1``: Luminosity functions
        - ``2``: SSP integrated magnitudes
    output_evstage : bool
        Output evolutionary stages with isochrone files.
    output_gzip : bool
        Output will be gziped.
    lf_maginf : float or str
        Dim limit of luminosity function, if ``output_kind == 1``.
    lf_magsup : float or str
        Bright limit of luminosity function, if ``output_kind == 1``.
    lf_deltamag : float or str
        Bin width of luminosity function, if ``output_kind == 1``.
    """
    def __init__(self, **kwargs):
        super(CMDRequest, self).__init__()
        self._cache = PadovaCache()
        self._settings = self._update_settings(kwargs)
        if self.__hash__() in self._cache:
            # Get request from the cache
            print("Reading from cache")
            self._r = self._cache[self.__hash__()]
        else:
            # Call API and cache it
            self._r = self._query(self._settings)
            self._cache[self.__hash__()] = self._r

    def _update_settings(self, kwargs):
        settings = get_defaults()
        settings.update(kwargs)

        if 'model' in kwargs:
            v = kwargs.pop('model')
            settings['isoc_kind'] = MODELS[v][0]
            if 'parsec' in v.lower():
                settings['output_evstage'] = 1
            else:
                settings['output_evstage'] = 0

        if 'carbon' in kwargs:
            v = kwargs.pop('carbon')
            settings['kind_cspecmag'] = CARBON_STARS[v][0]

        if 'interp' in kwargs:
            v = kwargs.pop('interp')
            settings['kind_interp'] = INTERP[v]

        if 'dust' in kwargs:
            v = kwargs.pop('dust')
            settings['dust_source'] = CIRCUM_MSTARS[v]

        if 'cdust' in kwargs:
            v = kwargs.pop('cdust')
            settings['dust_sourceC'] = CIRCUM_CSTARS[v]

        if 'mdust' in kwargs:
            v = kwargs.pop('mdust')
            settings['dust_sourceM'] = CIRCUM_MSTARS[v]

        if 'phot' in kwargs:
            v = kwargs.pop('phot')
            assert v in PHOT
            settings['photsys_file'] = 'tab_mag_odfnew/tab_mag_{0}.dat'.\
                format(v)

        for k, v in kwargs.items():
            if k in settings:
                settings[k] = v

        return settings

    def _query(self, request_data):
        """ Communicate with the CMD website """
        webserver = 'http://stev.oapd.inaf.it'
        print('Requesting from {0}...'.format(webserver))
        url = webserver + '/cgi-bin/cmd'
        q = urlencode(request_data)
        if py3k:
            req = request.Request(url, q.encode('utf8'))
            c = urlopen(req).read().decode('utf8')
        else:
            c = urlopen(url, q).read()
        aa = re.compile('output\d+')
        fname = aa.findall(c)
        if len(fname) > 0:
            url = '{0}/~lgirardi/tmp/{1}.dat'.format(webserver, fname[0])
            print('Downloading data...{0}'.format(url))
            bf = urlopen(url)
            r = bf.read()
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

    def __hash__(self):
        """Build a hash given the current settings."""
        # String to build hash against
        q = urlencode(self._settings)
        m = hashlib.md5()
        m.update(q)
        return m.hexdigest()

    @property
    def isochrone_set(self):
        """IsochroneSet table with the isochrones."""
        f = StringIO(self._r)
        t = IsochroneSet(f)
        return t

    @property
    def data(self):
        return self._r


class CMDErrorParser(parser.HTMLParser):
    """ find error box in the recent version of CMD website """
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
