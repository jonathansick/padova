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

    def cached_path(self, h):
        """Returns path to cached data, returns `None` if not in cache."""
        testpath = os.path.join(self._dir, h)
        if os.path.exists(testpath):
            return testpath
        else:
            return None


def main():
    pass


if __name__ == '__main__':
    main()
