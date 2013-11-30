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

    def generate_path(self, h, orig_url):
        """Generate a  cache path, given the hash and the original data URL."""
        if orig_url.endswith(".dat.gz"):
            return os.path.join(self._dir, h + ".dat.gz")
        elif orig_url.endswith(".dat"):
            return os.path.join(self._dir, h + ".dat")

    def cached_path(self, h):
        """Returns path to cached data, returns `None` if not in cache."""
        dat_testpath = os.path.join(self._dir, h) + ".dat"
        gz_testpath = dat_testpath + ".gz"
        if os.path.exists(dat_testpath):
            return dat_testpath
        elif os.path.exists(gz_testpath):
            return gz_testpath
        else:
            return None


def main():
    pass


if __name__ == '__main__':
    main()
