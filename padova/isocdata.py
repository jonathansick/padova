#!/usr/bin/env python
# encoding: utf-8
"""
This :mod:`isocdata` module helps to read Padova isochrone table files,
and split them into individual isochrones.
"""

import linecache
import os

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
    def z_code(self):
        """Code string for the metallicity. This is a 4-digit code for the
        metallicity (with leading zeros). E.g. ``z=0.012`` will be ``0120``.
        """
        z_str = "%.4f" % self.z
        z_str = z_str[2:]
        return z_str

    @property
    def age_code(self):
        """Code string for the age. This is in format ``tt.tt`, giving the
        log age.
        """
        return "%05.2f" % np.log10(self.age)

    @property
    def info(self):
        """Info about how this isochrone was generated
        (header from CMD output).
        """
        return self.table.meta['header']

    @property
    def filter_names(self):
        """A list of (column) names of the filters included in this isochrone.
        """
        cnames = self.table.colnames
        non_mag_cnames = ['log(age/yr)', 'M_ini', 'M_act', 'logL/Lo', 'logTe',
                'logG', 'mbol', 'C/O', 'M_hec', 'period', 'pmode', 'logMdot',
                'int_IMF', 'stage']
        # Normally I'd use sets, but column ordering is important
        return [name for name in cnames if name not in non_mag_cnames]

    def export_for_starfish(self, output_dir, bands=None):
        """Export the isochrone in a format useful for StarFISH `mklib`.
        
        Parameters
        ----------

        output_dir : str
            Directory where the isochrone file will be saved. The full
            filename is generated by the method to conform to the standard
            naming scheme: ``<output_dir>/zNNNN_tt.tt.dat`` where ``NNNN``
            is a 4-digit code for the metallicity (with leading zeros) and
            ``tt.tt`` is the log of the age.
        bands : list
            List of bands to include in isochrone output. Only necessary for
            exporting a subset of the bands in the full isochrone dataset.
        """
        filename = "z%s_%s" % (self.z_code, self.age_code)
        output_path = os.path.join(output_dir, filename)
        if not os.path.exists(output_dir): os.makedirs(output_dir)
        if os.path.exists(output_path): os.remove(output_path)
        fmt = {'m_ini': "%10.7f"}  # table writer formatting
        if bands is None:
            bandnames = self.filter_names
            for name in bandnames:
                fmt[name] = "%8.6f"
        else:
            bandnames = [n for n in bands if n in self.filter_names]
        self.table.write(output_path,
                format='ascii.fixed_width_no_header',
                formats=fmt,
                delimiter=' ',
                include_names=['M_ini'] + bandnames)


def main():
    pass


if __name__ == '__main__':
    main()
