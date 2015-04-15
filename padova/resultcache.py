#!/usr/bin/env python
# encoding: utf-8
"""
resultcache manages the cache of results from the CMD and TRILGEGAL
interfaces. To be used internally.
"""

import os


class PadovaCache(object):
    """Cache manager for CMD and TRILEGAL requests.

    The cache takes :class:`padova.settings.Settings` instances to hash
    results in the cache.
    """
    def __init__(self):
        super(PadovaCache, self).__init__()
        self._dir = os.path.expanduser("~/.padova_cache")
        if not os.path.exists(self._dir):
            os.makedirs(self._dir)

    def _cache_path(self, settings):
        return os.path.join(self._dir, str(settings.__hash__()))

    def __contains__(self, settings):
        return os.path.exists(self._cache_path(settings))

    def __getitem__(self, settings):
        assert self.__contains__(settings)
        with open(self._cache_path(settings)) as f:
            data = f.read()
        return data

    def __setitem__(self, settings, data):
        p = self._cache_path(settings)
        if os.path.exists(p):
            os.remove(p)
        with open(p, 'w') as f:
            f.write(data)
