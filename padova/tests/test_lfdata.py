#!/usr/bin/env python
# encoding: utf-8
"""
Tests from the :mod:`lfdata` module.
"""

from astropy.utils.data import get_pkg_data_filename

from ..lfdata import LFTable


def test_read_lfs():
    """Test reading an isochrone table."""
    datpath = get_pkg_data_filename('../data/lf_0019.dat')
    print datpath
    lftable = LFTable(datpath)
    assert len(lftable.lfs) == 36

def test_lf():
    """Test a luminosity function instance."""
    datpath = get_pkg_data_filename('../data/lf_0019.dat')
    print datpath
    lftable = LFTable(datpath)
    lf = lftable.lfs[0]
    assert isinstance(lf.z, float)
    assert lf.z == 0.019
    assert isinstance(lf.info, list)
