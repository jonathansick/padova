#!/usr/bin/env python
# encoding: utf-8
"""
Python interface to the Padova group's CMD web interface for isochrones.
"""


import mechanize


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
            output_gzip=False,
            lf_maginf="20.0",
            lf_magsup="-20.0",
            lf_deltamag="0.2"):
        super(CMD, self).__init__()
        self.isoc_kind = isoc_kind  # Generation of evolutionary tracks
        self.photsys_file = photsys_file
        self.kind_cspecmag = kind_cspecmag
        self.dust_sourceM = dust_sourceM
        self.dust_sourceC = dust_sourceC
        self.extinction_av = extinction_av
        self.imf_file = imf_file
        self.isoc_val = isoc_val
        self.isoc_age = isoc_age
        self.isoc_zeta = isoc_zeta
        self.isoc_zeta0 = isoc_zeta0
        self.isoc_lage0 = isoc_lage0
        self.isoc_lage1 = isoc_lage1
        self.isoc_dlage = isoc_dlage
        self.isoc_z0 = isoc_z0
        self.isoc_z1 = isoc_z1
        self.isoc_dz = isoc_dz
        self.output_evstage = output_evstage
        self.output_gzip = output_gzip
        self.lf_maginf = lf_maginf
        self.lf_magsup = lf_magsup
        self.lf_deltamag = lf_deltamag

        self._br = mechanize.Browser()

    def get(self):
        """Submit a form and get the result."""
        self._br.open("http://stev.oapd.inaf.it/cgi-bin/cmd")
        form = self._br.forms()[0]
        self._fill_form(form)
        request = form.click()  # mechanize.Request object
        try:
            response = mechanize.urlopen(request)
        except mechanize.HTTPError, response:
            pass
        print response.geturl()
        result_page = response.read()  # body
        response.close()

    def _fill_form(self, form):
        """Fill out controls in the form."""
        form.set_value([self.isoc_kind], name="isoc_kind")
        form.set_value([self.photsys_file], name="photsys_file")
        form.set_value([self.dust_sourceM], name="dust_sourceM")
        form.set_value([self.dust_sourceC], name="dust_sourceC")
        form.set_value([self.extinction_av], name="extinction_av")
        form.set_value([self.imf_file], name="imf_file")
        form.set_value([self.isoc_val], name="isoc_val")
        form.set_value([self.isoc_age], name="isoc_age")
        form.set_value([self.isoc_zeta], name="isoc_zeta")
        form.set_value([self.isoc_zeta0], name="isoc_zeta0")
        form.set_value([self.isoc_lage0], name="isoc_lage0")
        form.set_value([self.isoc_lage1], name="isoc_lage1")
        form.set_value([self.isoc_dlage], name="isoc_dlage")
        form.set_value([self.isoc_z0], name="isoc_z0")
        form.set_value([self.isoc_z1], name="isoc_z1")
        form.set_value([self.isoc_dz], name="isoc_dz")
        form.find_control("output_evstage").items[0].selected \
                = self.output_evstage
        form.find_control("output_gzip").items[0].selected = self.output_gzip
        form.set_value([self.lf_maginf], name="lf_maginf")
        form.set_value([self.lf_magsup], name="lf_magsup")
        form.set_value([self.lf_deltamag], name="lf_deltamag")


def main():
    pass


if __name__ == '__main__':
    main()
