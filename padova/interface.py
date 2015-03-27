#!/usr/bin/env python
# encoding: utf-8
"""
Maps for cmd interface settings

Code adapted from ezpadova - Morgan Fousneau, MIT License
"""

from __future__ import print_function, unicode_literals, division

import sys
from collections import OrderedDict

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


# interpolation
INTERP = {'default': 0,
          'improved': 1}


PHOT = {
    "2mass_spitzer": " 2MASS + Spitzer (IRAC+MIPS)",
    "2mass_spitzer_wise": " 2MASS + Spitzer (IRAC+MIPS) + WISE",
    "2mass": " 2MASS JHKs",
    "ubvrijhk": "UBVRIJHK (cf. Maiz-Apellaniz 2006 + Bessell 1990)",
    "bessell": "UBVRIJHKLMN (cf. Bessell 1990 + Bessell & Brett 1988)",
    "akari": "AKARI",
    "batc": "BATC",
    "megacam": "CFHT/Megacam u*g'r'i'z'",
    "dcmc": "DCMC",
    "denis": "DENIS",
    "dmc14": "DMC 14 filters",
    "dmc15": "DMC 15 filters",
    "eis": "ESO/EIS (WFI UBVRIZ + SOFI JHK)",
    "wfi": "ESO/WFI",
    "wfi_sofi": "ESO/WFI+SOFI",
    "wfi2": "ESO/WFI2",
    "galex": "GALEX FUV+NUV (Vega) + Johnson's UBV",
    "galex_sloan": "GALEX FUV+NUV + SDSS ugriz (all AB) ",
    "UVbright": "HST+GALEX+Swift/UVOT UV filters",
    "acs_hrc": "HST/ACS HRC",
    "acs_wfc": "HST/ACS WFC",
    "nicmosab": "HST/NICMOS AB",
    "nicmosst": "HST/NICMOS ST",
    "nicmosvega": "HST/NICMOS vega",
    "stis": "HST/STIS imaging mode",
    "wfc3ir": "HST/WFC3 IR channel (final throughputs)",
    "wfc3uvis1": "HST/WFC3 UVIS channel, chip 1 (final throughputs)",
    "wfc3uvis2": "HST/WFC3 UVIS channel, chip 2 (final throughputs)",
    "wfc3_medium": "HST/WFC3 medium filters (UVIS1+IR, final throughputs)",
    "wfc3": "HST/WFC3 wide filters (UVIS1+IR, final throughputs)",
    "wfpc2": "HST/WFPC2 (Vega, cf. Holtzman et al. 1995)",
    "kepler": "Kepler + SDSS griz + DDO51 (in AB)",
    "kepler_2mass": "Kepler + SDSS griz + DDO51 (AB) + 2MASS (~Vega)",
    "ogle": "OGLE-II",
    "panstarrs1": "Pan-STARRS1",
    "sloan": "SDSS ugriz",
    "sloan_2mass": "SDSS ugriz + 2MASS JHKs",
    "sloan_ukidss": "SDSS ugriz + UKIDSS ZYJHK",
    "swift_uvot": "SWIFT/UVOT UVW2, UVM2, UVW1,u (Vega) ",
    "spitzer": "Spitzer IRAC+MIPS",
    "stroemgren": "Stroemgren-Crawford",
    "suprimecam": "Subaru/Suprime-Cam (AB)",
    "tycho2": "Tycho VTBT",
    "ukidss": "UKIDSS ZYJHK (Vega)",
    "visir": "VISIR",
    "vista": "VISTA ZYJHKs (Vega)",
    "washington": "Washington CMT1T2",
    "washington_ddo51": "Washington CMT1T2 + DDO51"}


# available tracks
MODELS = {
    'parsec12s': ('parsec_CAF09_v1.2S',
                  'PARSEC version 1.2S,  Tang et al. (2014), '
                  'Chen et al. (2014)'),
    'parsec11': ('parsec_CAF09_v1.1',
                 'PARSEC version 1.1, With revised diffusion+overshooting in '
                 'low-mass stars, and improvements in interpolation scheme.'),
    'parsec10': ('parsec_CAF09_v1.0', 'PARSEC version 1.0'),
    '2010': ('gi10a',
             'Marigo et al. (2008) with the Girardi et al. (2010) '
             'Case A correction for low-mass, low-metallicity AGB tracks'),
    '2010b': ('gi10b',
              'Marigo et al. (2008) with the Girardi et al. (2010) '
              'Case B correction for low-mass, low-metallicity AGB tracks'),
    '2008': ('ma08',
             'Marigo et al. (2008): Girardi et al. (2000) up to early-AGB '
             '+ detailed TP-AGB from Marigo & Girardi (2007) '
             '(for M <= 7 Msun) + Bertelli et al. (1994) (for M > 7 Msun) + '
             'additional Z=0.0001 and Z=0.001 tracks.'),
    '2002': ('gi2000',
             'Basic set of Girardi et al. (2002) : Girardi et al. (2000) '
             '+ simplified TP-AGB (for M <= 7 Msun) '
             '+ Bertelli et al. (1994) (for M > 7 Msun) '
             '+ additional Z=0.0001 and Z=0.001 tracks.')
}


CARBON_STARS = {
    'loidl': ('loidl01',
              'Loidl et al. (2001) (as in Marigo et al. (2008) and '
              'Girardi et al. (2008))'),
    'aringer': ('aringer09',
                "Aringer et al. (2009) (Note: The interpolation scheme has "
                "been slightly improved w.r.t. to the paper's Fig. 19.")
}


CIRCUM_MSTARS = {
    'nodustM': ('no dust', ''),
    'sil': ('Silicates', 'Bressan et al. (1998)'),
    'AlOx': ('100% AlOx', 'Groenewegen (2006)'),
    'dpmod60alox40': ('60% Silicate + 40% AlOx', 'Groenewegen (2006)'),
    'dpmod': ('100% Silicate', 'Groenewegen (2006)')
}


CIRCUM_CSTARS = {
    'nodustC': ('no dust', ''),
    'gra': ('Graphites', 'Bressan et al. (1998)'),
    'AMC': ('100% AMC', 'Groenewegen (2006)'),
    'AMCSIC15': ('85% AMC + 15% SiC', 'Groenewegen (2006)')
}


ISOC_VAL = {
    0: ('Single isochrone', ''),
    1: ('Sequence of isochrones at constant Z', ''),
    2: ('Sequence of isochrones at constant t (variable Z)',
        'Groenewegen (2006)')
}


def get_defaults():
    v = (('binary_frac', 0.3),
         ('binary_kind', 1),
         ('binary_mrinf', 0.7),
         ('binary_mrsup', 1),
         ('cmd_version', 2.3),
         ('dust_source', 'nodust'),
         ('dust_sourceC', 'AMCSIC15'),
         ('dust_sourceM', 'dpmod60alox40'),
         ('eta_reimers', 0.2),
         ('extinction_av', 0),
         ('icm_lim', 4),
         ('imf_file', 'tab_imf/imf_chabrier_lognormal.dat'),
         ('isoc_age', 1e7),
         ('isoc_age0', 12.7e9),
         ('isoc_dlage', 0.05),
         ('isoc_dz', 0.0001),
         ('isoc_kind', 'parsec_CAF09_v1.2S'),
         ('isoc_lage0', 6.6),
         ('isoc_lage1', 10.13),
         ('isoc_val', 0),
         ('isoc_z0', 0.0001),
         ('isoc_z1', 0.03),
         ('isoc_zeta', 0.02),
         ('isoc_zeta0', 0.008),
         ('kind_cspecmag', 'aringer09'),
         ('kind_dust', 0),
         ('kind_interp', 1),
         ('kind_mag', 2),
         ('kind_postagb', -1),
         ('kind_pulsecycle', 0),
         ('kind_tpagb', 3),
         ('lf_deltamag', 0.2),
         ('lf_maginf', 20),
         ('lf_magsup', -20),
         ('mag_lim', 26),
         ('mag_res', 0.1),
         ('output_evstage', 0),
         ('output_gzip', 0),
         ('output_kind', 0),
         ('photsys_file', 'tab_mag_odfnew/tab_mag_bessell.dat'),
         ('photsys_version', 'yang'),
         ('submit_form', 'Submit'))
    return OrderedDict(v)


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
