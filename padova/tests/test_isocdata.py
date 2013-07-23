#!/usr/bin/env python
# encoding: utf-8
"""
Tests from the :mod:`isocdata` module.
"""

from astropy.utils.data import get_pkg_data_filename

from ..isocdata import IsochroneTable


def test_prescan():
    """Test the pre-scan done by IsochroneTable."""
    datpath = get_pkg_data_filename('../data/isocz0120.dat')
    print datpath
    isoctable = IsochroneTable(datpath)
    start_lines = isoctable._prescan_table()
    isoctable._read_isochrone_specs(start_lines)
    assert start_lines[0] == 11
    assert len(start_lines) == 71

def test_read_isochrones():
    """Test reading an isochrone table."""
    datpath = get_pkg_data_filename('../data/isocz0120.dat')
    print datpath
    isoctable = IsochroneTable(datpath)
    assert len(isoctable.isochrones) == 71

def test_isochrone():
    """Test an isochrone instance"""
    datpath = get_pkg_data_filename('../data/isocz0120.dat')
    print datpath
    isoctable = IsochroneTable(datpath)
    isoc = isoctable.isochrones[0]
    assert isinstance(isoc.z, float)
    assert isoc.z == 0.012
    assert isinstance(isoc.age, float)
    assert isoc.age == 3981000.0
    assert isinstance(isoc.info, list)

def test_isochrone_starfish():
    """Test the export-for-starfish feature of Isochrone."""
    datpath = get_pkg_data_filename('../data/isocz0120.dat')
    print datpath
    isoctable = IsochroneTable(datpath)
    isoc = isoctable.isochrones[0]
    for n, m in zip(isoc.filter_names, ['J', 'H', 'Ks']):
        assert n == m
    isoc.export_for_starfish("_test")
