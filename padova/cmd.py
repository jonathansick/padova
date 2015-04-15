#!/usr/bin/env python
# encoding: utf-8
"""
Python interface to the Padova group's CMD web interface for isochrones.
"""

from __future__ import print_function, unicode_literals, division

from padova.settings import Settings
from padova.interface import CMDRequest


class IsochroneRequest(CMDRequest):
    """Request a single isochrone.

    Parameters
    ----------
    z : float
        The metallicity, fraction of metals in stellar composition.
    log_age : float
        The age, :math:`\log_{10} (A/\mathrm{yr})`.
    kwargs :
        Keyword arguments, see TODO
    """
    def __init__(self, z=0.0, log_age=9., **kwargs):
        kwargs['isoc_val'] = "0"  # declare single isochrone request
        kwargs['isoc_zeta'] = z
        kwargs['isoc_age'] = 10. ** log_age
        s = Settings.load_package_settings(**kwargs)
        super(IsochroneRequest, self).__init__(s)

    @property
    def isochrone(self):
        """The :class:`padova.isocdata.Isochrone` instance, an Astropy Table.
        """
        return self.isochrone_set.isochrones[0]


class AgeGridRequest(CMDRequest):
    """Request a grid of single-Z isochrones spanning an age range.

    Parameters
    ----------
    z : float
        The metallicity, fraction of metals in stellar composition.
    min_log_age : float
        Youngest isochrone, :math:`\log_{10} (A/\mathrm{yr})`.
    max_log_age : float
        Oldest isochrone, :math:`\log_{10} (A/\mathrm{yr})`.
    delta_log_age : float
        Isochrone age step size, in log-years.
    kwargs :
        Keyword arguments, see TODO
    """
    def __init__(self, z=0.0,
                 min_log_age=6.6, max_log_age=10.13, delta_log_age=0.05,
                 **kwargs):
        kwargs['isoc_val'] = "1"  # declare age grid request
        kwargs['isoc_lage0'] = min_log_age
        kwargs['isoc_lage1'] = max_log_age
        kwargs['isoc_dlage'] = delta_log_age
        kwargs['isoc_zeta0'] = z
        s = Settings.load_package_settings(**kwargs)
        super(AgeGridRequest, self).__init__(s)


class MetallicityGridRequest(CMDRequest):
    """Request a grid of single-age isochrones spanning a metallicity range.

    Parameters
    ----------
    log_age : float
        The age, :math:`\log_{10} (A/\mathrm{yr})`.
    min_z : float
        The minimum metallicity of the grid (fraction of composition).
    max_z : float
        The maximum metallicity of the grid (fraction of composition).
    delta_z : float
        The metallicity step size (fraction of composition).
    kwargs :
        Keyword arguments, see TODO
    """
    def __init__(self, log_age=9.,
                 min_z=0.0001, max_z=0.03, delta_z=0.0001,
                 **kwargs):
        kwargs['isoc_val'] = "2"  # declare Z grid request
        kwargs['isoc_age0'] = 10. ** log_age
        kwargs['isoc_z0'] = min_z
        kwargs['isoc_z1'] = max_z
        kwargs['isoc_dz'] = delta_z
        s = Settings.load_package_settings(**kwargs)
        super(MetallicityGridRequest, self).__init__(s)
