#!/usr/bin/env python
# encoding: utf-8
"""
Tools for reading CMD-interface tables outputs.
"""

from collections import deque


class BaseReader(object):
    """Baseclass for reading tables produced by the Padova CMD interface."""
    def __init__(self, f):
        super(BaseReader, self).__init__()
        self._f = f  # file handle
        self._read()

    def _prescan_table(self, n_header_lines):
        """Find lines where individual isochrones start."""
        header_lines = []

        data_blocks = []
        hdeque = deque()
        self._f.seek(0)
        block = None
        for i, line in enumerate(self._f):
            if line.startswith('#'):
                # This is a header line
                if block is None:
                    block = {}
                    if len(data_blocks) > 0:
                        data_blocks[-1]['end'] = i - 1
                hdeque.append(line.lstrip('#').strip())
            elif block is not None:
                # This is a data line;
                # Close the block
                block['start'] = i
                block['header_lines'] = [hdeque.pop()
                                         for j in xrange(n_header_lines)][::-1]
                data_blocks.append(block)

                # Treat excess header lines as a global header
                while len(hdeque) > 0:
                    header_lines.append(hdeque.popleft())

                block = None
        data_blocks[-1]['end'] = i
        n_lines = i + 1

        return header_lines, data_blocks, n_lines
