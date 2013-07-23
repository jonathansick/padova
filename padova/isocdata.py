#!/usr/bin/env python
# encoding: utf-8
"""
This :mod:`isocdata` module helps to read Padova isochrone table files,
and split them into individual isochrones.
"""

import linecache

import numpy as np
from astropy.table import Table


class IsochroneTable(object):
    """Reads an isochrone table (output from the Padova CMD interface).
    
    Attributes
    ----------

    metadata : list
        List of lines from the metadata found at the top of the ischrone
        table file.
    isochrones : list
        List of :class:`Isochrone` instances read from the table.

    Parameters
    ----------

    fname : str
        Filename of isochrone table to read.
    """
    def __init__(self, fname):
        super(IsochroneTable, self).__init__()
        self.fname = fname
        self._read()

    def _read(self):
        """Read isochrone table and create Isochrone instances."""
        start_indices = self._prescan_table()
        self._isochrone_specs = self._read_isochrone_specs(start_indices)
        self.metadata = self._read_metadata(0, start_indices[0])
        self.isochrones = self._read_isochrones(start_indices)
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

    def _read_isochrones(self, start_indices):
        """Extract isochrones from the table, creating individual
        :class:`Isochrone` instances.
        """
        isocs = []
        for i, (start_index, meta) in enumerate(
                zip(start_indices, self._isochrone_specs)):
            if i < len(start_indices) - 1:
                end_index = start_indices[i + 1]
            else:
                end_index = self._linecount()
            isoc = self._read_isochrone(start_index, end_index, meta)
            isocs.append(isoc)
        return isocs
    
    def _linecount(self):
        """Count lines in isochrone table, via the Python Cookbook."""
        count = -1
        for count, line in enumerate(open(self.fname, 'rU')):
            pass
            count += 1
        return count

    def _read_isochrone(self, start_index, end_index, meta):
        """Read a single isochrone, between `start_index` and `end_index`."""
        header = self._read_header(start_index)
        dt = []
        for cname in header:
            if cname == 'stage':
                dt.append((cname, 'S40'))
            elif cname == 'pmode':
                dt.append((cname, np.int))
            else:
                dt.append((cname, np.float))
        ncols = len(dt)
        data = np.empty(end_index - start_index - 2, dtype=np.dtype(dt))
        for j, i in enumerate(xrange(start_index + 2, end_index)):
            parts = linecache.getline(self.fname, i + 1).rstrip('\n').split()
            # print parts
            if len(parts) == ncols - 1:
                parts.append(' ')  # likely missing a 'stage' column here
            for val, (cname, typ) in zip(parts, dt):
                if typ == np.float:
                    data[cname][j] = float(val)
                elif typ == np.int:
                    data[cname][j] = int(val)
                else:
                    data[cname][j] = val
        tbl = Table(data,
                meta={"header": self.metadata,
                      "Z": meta['Z'],
                      'age': meta['age']})
        isoc = Isochrone(tbl)
        return isoc


class Isochrone(object):
    """Holds a single isochrone (single age, and metallicity).
    
    Parameters
    ----------

    table : :class:`astropy.table.Table` instance
        A table with isochrone data. This table must also have metadata
        with age and metallicity information. This table is typically
        generated by :class:`IsochroneTable`.
    """
    def __init__(self, table):
        super(Isochrone, self).__init__()
        self.table = table

    @property
    def z(self):
        """Metallicity of this isochrone."""
        return self.table.meta['Z']

    @property
    def age(self):
        """Age of this isochrone (yr)."""
        return self.table.meta['age']

    @property
    def info(self):
        """Info about how this isochrone was generated
        (header from CMD output).
        """
        return self.table.meta['header']


def main():
    pass


if __name__ == '__main__':
    main()
