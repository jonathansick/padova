#!/usr/bin/env python
# encoding: utf-8
"""
Tests for parsing the result HTML.
"""

from astropy.utils.data import get_pkg_data_filename

from ..cmd import CmdResponseParser


def test_parse():
    """Test CmdResponseParser for getting .dat results from reponse HTML."""
    truth = "http://stev.oapd.inaf.it/~lgirardi/tmp/output657220915964.dat"
    htmlpath = get_pkg_data_filename("../data/cmd_isoc_output.html")
    with open(htmlpath, 'r') as f:
        html = f.read()
        p = CmdResponseParser()
        p.feed(html)
        url = p.data_url
    assert url == truth
