#!/usr/bin/env python
# encoding: utf-8
"""
This :mod:`isocdata` module helps to read Padova isochrone table files,
and split them into individual isochrones.
"""

import linecache

from astropy.table import Table


class IsochroneTable(object):
    """Reads an isochrone table (output from the Padova CMD interface).
    
    Attributes
    ----------

    metadata : list
        List of lines from the metadata found at the top of the ischrone
        table file.

    Parameters
    ----------

    fname : str
        Filename of isochrone table to read.
    """
    def __init__(self, fname):
        super(IsochroneTable, self).__init__()
        self.fname = fname

    def _read(self):
        """Read isochrone table and create Isochrone instances."""
        start_indices = self._prescan_table()
        self._isochrone_specs = self._read_isochrone_specs(start_indices)
        self.metadata = self._read_metadata(0, start_indices[0])
        linecache.clearcache()

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
    
    def _read_isochrone_specs(self, start_indices):
        """Produce a list of the age and metallicity specifications for
        each isochone in the table.
        """
        specs = []
        for i in start_indices:
            line = linecache.getline(self.fname, i + 1).rstrip().split()
            z = float(line[4])
            age = float(line[7])
            specs.append({"Z": z, "age": age})
        return specs
    
    def _read_header(self, i):
        """Parse the header for the isochrone start at line `i`.
        
        This method attempts to overcome some of the oddities in the
        CMD isochrone tables.
        """
        # Note that linecache has 1-based lines.
        # Add another to get the header, rather than the age/Z metadata.
        hdr = linecache.getline(self.fname, i + 2).lstrip('#').rstrip().split()
        return hdr


def main():
    pass


if __name__ == '__main__':
    main()
