#!/usr/bin/env python
# encoding: utf-8
"""
Python interface to the Padova group's CMD web interface for isochrones.

Code adapted from ezpadova - Morgan Fousneau, MIT License
"""

from __future__ import print_function, unicode_literals, division

from padova.interface import CMDRequest
from padova.isocdata import IsochroneTable

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


class IsochroneRequest(CMDRequest):
    """Request a single isochrone."""
    def __init__(self, **kwargs):
        super(IsochroneRequest, self).__init__(**kwargs)

    @property
    def table(self):
        """Astropy table with the isochrone."""
        f = StringIO(self._r)
        t = IsochroneTable(f)
        return t

    @property
    def data(self):
        return self._r


class AgeGridRequest(CMDRequest):
    """Request a grid of single-Z isochrones spanning an age range."""
    def __init__(self, **kwargs):
        super(AgeGridRequest, self).__init__(**kwargs)


class MetallicityGridRequest(CMDRequest):
    """Request a grid of single-age isochrones spanning a metallicity range."""
    def __init__(self, **kwargs):
        super(MetallicityGridRequest, self).__init__(**kwargs)
