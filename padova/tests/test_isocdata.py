#!/usr/bin/env python
# encoding: utf-8
"""
Tests from the :mod:`isocdata` module.
"""

from astropy.utils.data import get_pkg_data_filename

from ..isocdata import IsochroneTable


def test_prescan():
    """Test reading an ischrone table."""
    datpath = get_pkg_data_filename('../data/isocz0120.dat')
    print datpath
    isoctable = IsochroneTable(datpath)
    start_lines = isoctable._prescan_table()
    isoctable._read_isochrone_specs(start_lines)
    assert start_lines[0] == 11
    assert len(start_lines) == 71
