#!/usr/bin/env python
# encoding: utf-8
"""
Tools for reading CMD-interface tables outputs.
"""

import os
import gzip
import linecache


class BaseReader(object):
    """Baseclass for reading tables produced by the Padova CMD interface."""
    def __init__(self, fname):
        super(BaseReader, self).__init__()
        if fname.endswith("gz"):
            # need to make an unzipped copy
            f = gzip.open(fname, 'rb')
            file_content = f.read()
            self.fname = os.path.splitext(fname)[0]
            if os.path.exists(self.fname): os.remove(self.fname)
            f2 = open(os.path.splitext(fname)[0], 'w')
            f2.write(file_content)
            f2.close()
            f.close()
            self._gz = True
        else:
            # input is just a .dat file
            self.fname = fname
            self._gz = False
        self._read()

    def cleanup(self):
        """Delete the temporary unzipped file. If the file was not originally
        gzipped, it will not be deleted.
        """
        if self._gz:
            os.remove(self.fname)

    def _prescan_table(self):
        """Find lines where individual isochrones start."""
        start_lines = []
        with open(self.fname) as f:
            for i, line in enumerate(f):
                if line.startswith("#\t"):
                    start_lines.append(i)
        return start_lines

    def _read_metadata(self, start, stop):
        """Read the metadata header at the top of the isochrone table."""
        metadata = []
        with open(self.fname) as f:
            i = 0
            for i, line in enumerate(f):
                if i < start: continue
                elif i == stop: break
                metadata.append(line.lstrip('#').rstrip('\n'))
        return metadata

    def _linecount(self):
        """Count lines in isochrone table, via the Python Cookbook."""
        count = -1
        for count, line in enumerate(open(self.fname, 'rU')):
            count += 1
        return count

    def _read_header(self, i):
        """Parse the header for the isochrone starting at line `i`.
        
        This method attempts to overcome some of the oddities in the
        CMD isochrone tables.
        """
        # Note that linecache has 1-based lines.
        # Add another to get the header, rather than the age/Z metadata.
        hdr = linecache.getline(self.fname, i + 2).lstrip('#').rstrip().split()
        return hdr
