#!/usr/bin/env python
# encoding: utf-8
"""
Tests for padova.settings
"""

import pytest


@pytest.fixture
def settings():
    from padova.settings import Settings
    return Settings.load_package_settings()


def test_alias(settings):
    assert settings['photsys'] == settings['photsys_file']
