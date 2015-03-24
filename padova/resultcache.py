#!/usr/bin/env python
# encoding: utf-8
"""
resultcache manages the cache of results from the CMD and TRILGEGAL
interfaces. To be used internally.
"""

import os


class PadovaCache(object):
    """Cache manager for CMD and TRILEGAL requests."""
    def __init__(self):
        super(PadovaCache, self).__init__()
        self._dir = os.path.expanduser("~/.padova_cache")
        if not os.path.exists(self._dir):
            os.makedirs(self._dir)

    def _cache_path(self, h):
        return os.path.join(self._dir, str(h))

    def __contains__(self, h):
        return os.path.exists(self._cache_path(h))

    def __getitem__(self, h):
        assert self.__contains__(h)
        with open(self._cache_path(h)) as f:
            data = f.read()
        return data

    def __setitem__(self, h, data):
        p = self._cache_path(h)
        if os.path.exists(p):
            os.remove(p)
        with open(p, 'w') as f:
            f.write(data)
