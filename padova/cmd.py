#!/usr/bin/env python
# encoding: utf-8
"""
Python interface to the Padova group's CMD web interface for isochrones.
"""

import hashlib
from HTMLParser import HTMLParser
from urlparse import urljoin

import mechanize

from .resultcache import PadovaCache


class CMD(object):
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
    isoc_zeta : 
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
    def __init__(self, isoc_kind="parsec_CAF09_v1.1",
            photsys_file="tab_mag_odfnew/tab_mag_2mass_spitzer.dat",
            kind_cspecmag="loidl01",
            dust_sourceM="nodustM",
            dust_sourceC="nodustC",
            extinction_av="0.0",
            imf_file="tab_imf/imf_salpeter.dat",
            isoc_val="1",
            isoc_age="1e9",
            isoc_zeta="0.019",
            isoc_zeta0="0.0001",
            isoc_lage0="6.6",
            isoc_lage1="10.13",
            isoc_dlage="0.05",
            isoc_z0="0.0001",
            isoc_z1="0.03",
            isoc_dz="0.0001",
            output_kind="0",
            output_evstage=True,
            output_gzip=True,
            lf_maginf="20.0",
            lf_magsup="-20.0",
            lf_deltamag="0.2"):
        super(CMD, self).__init__()
        self._settings = {
                "isoc_kind": isoc_kind,
                "photsys_file": photsys_file,
                "kind_cspecmag": kind_cspecmag,
                "dust_sourceM": dust_sourceM,
                "dust_sourceC": dust_sourceC,
                "extinction_av": extinction_av,
                "imf_file": imf_file,
                "isoc_val": isoc_val,
                "isoc_age": isoc_age,
                "isoc_zeta": isoc_zeta,
                "isoc_zeta0": isoc_zeta0,
                "isoc_lage0": isoc_lage0,
                "isoc_lage1": isoc_lage1,
                "isoc_dlage": isoc_dlage,
                "isoc_z0": isoc_z0,
                "isoc_z1": isoc_z1,
                "isoc_dz": isoc_dz,
                "output_evstage": output_evstage,
                "output_gzip": output_gzip,
                "lf_maginf": lf_maginf,
                "lf_magsup": lf_magsup,
                "lf_deltamag": lf_deltamag
        }

        self._cache = PadovaCache()
        self._br = mechanize.Browser()

    def get(self):
        """Submit a form and get the result."""
        h = self._hash_settings()
        cache_path = self._cache.cached_path(h)  # test the cache
        if cache_path is not None:
            return cache_path  # Perhaps return the file object instead?
        self._br.open("http://stev.oapd.inaf.it/cgi-bin/cmd")
        print "self._br", self._br
        print "self._br.forms()", self._br.forms()
        for form in self._br.forms():
            break  # Get first form. Can't find a good way to do this.
        self._br.form = list(self._br.forms())[0]
        print "form", self._br.form
        self._fill_form()
        # request = self._br.form.submit()  # mechanize.Request object
        response = self._br.submit(name='submit_form', label='Submit')
        html = response.read()
        print "html:\n"
        # TODO do something with the html to download result

    def _fill_form(self):
        """Fill out controls in the form."""
        seq_types = ['imf_file', 'photsys_file', 'isoc_kind', 'kind_cspecmag',
                'dust_sourceM', 'dust_sourceC', 'isoc_val', 'output_kind']
        for k, v in self._settings.iteritems():
            print k, v
            if k in ['output_evstage', 'output_gzip']: continue
            if k in seq_types:
                self._br[k] = [v]
            else:
                self._br[k] = v

        for k in ['output_evstage', 'output_gzip']:
            if self._settings[k]:
                self._br.find_control(k).items[0].selected = True
            else:
                self._br.find_control(k).items[0].selected = False

    def _hash_settings(self):
        """Build a hash given the current settings."""
        keys = self._settings.keys()
        keys.sort()
        # String to build hash against
        obj = "".join([str(self._settings[k]) for k in keys])
        m = hashlib.md5()
        m.update(obj)
        return m.hexdigest()


class CmdResponseParser(HTMLParser):

    data_url = None

    def handle_starttag(self, tag, attrs):
        # print "Start tag:", tag
        for attr in attrs:
            # print "     attr:", attr
            if len(attr) > 1:
                if isinstance(attr[1], str):
                    # Look for either gziped or plain result URL
                    if attr[1].endswith(".dat") or attr[1].endswith(".dat.gz"):
                        relurl = attr[1]
                        self.data_url = urljoin(
                                'http://stev.oapd.inaf.it/cgi-bin/cmd_2.5',
                                relurl)


def main():
    pass


if __name__ == '__main__':
    main()
