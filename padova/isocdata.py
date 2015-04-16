#!/usr/bin/env python
# encoding: utf-8
"""
This :mod:`isocdata` module helps to read Padova isochrone table files,
and split them into individual isochrones.
"""

import os
from collections import OrderedDict

import numpy as np
from astropy.table import Table, join

from padova.basereader import BaseReader


class IsochroneSet(BaseReader):
    """Reads an isochrone table (output from the Padova CMD interface).

    Parameters
    ----------
    fname :
        File handle of dataset to read
    """
    def __init__(self, f):
        self._isochrones = []
        super(IsochroneSet, self).__init__(f)
        self._current = 0

    def __iter__(self):
        return self

    def next(self):
        try:
            isoc = self._isochrones[self._current]
            self._current += 1
        except IndexError:
            self._current = 0
            raise StopIteration
        return isoc

    def __getitem__(self, index):
        return self._isochrones[index]

    def __len__(self):
        return len(self._isochrones)

    @property
    def isochrones(self):
        return self._isochrones

    def _read(self):
        """Read isochrone table and create Isochrone instances."""
        self._isochrones = []
        self._header_lines, blocks, n_lines = self._prescan_table(2)

        # Load the entire dataset
        colnames = self._parse_colnames(blocks[0]['header_lines'][-1])
        # skip first column because it's a blank tab
        usecols = [i + 1 for i, c in enumerate(colnames)]
        dt = []
        for cname in colnames:
            if cname == 'stage':
                dt.append((cname, np.int))
            elif cname == 'pmode':
                dt.append((cname, np.int))
            else:
                dt.append((cname, np.float))
        self._f.seek(0)
        data = np.genfromtxt(self._f,
                             dtype=np.dtype(dt),
                             delimiter='\t',
                             autostrip=True,
                             comments='#',
                             usecols=usecols)

        # Find where age or metallicity changed
        age_diffs = np.diff(data['logageyr'])
        z_diffs = np.diff(data['Z'])
        changed = np.where((age_diffs >= 0.0001) | (z_diffs >= 0.000001))[0]
        changed += 1  # needed to get indexes right below
        assert len(changed) + 1 == len(blocks)

        # Do this so we can iterate all blocks uniformly
        changed = np.concatenate([[0], changed, [len(data) + 1]])

        # Build individual isochrone tables
        for i, (idx0, block) in enumerate(zip(changed[:-1], blocks)):
            idx1 = changed[i + 1]
            isoc_data = data[idx0:idx1]
            meta = self._parse_meta(block['header_lines'][0])
            meta['header'] = self._header_lines
            tbl = Isochrone(isoc_data, meta=meta)
            isoc = Isochrone(tbl)
            self._isochrones.append(isoc)

    def _parse_colnames(self, header):
        header = header.replace('\t', ' ')
        parts = header.split()
        return parts

    def _parse_meta(self, header):
        header = header.replace('\t', ' ')
        header = header.replace('=', ' ')
        parts = header.split()[1:-1]
        vals = [float(p) for p in parts[1::2]]
        meta = OrderedDict(zip(parts[::2], vals))
        return meta


class Isochrone(Table):
    """Holds a single isochrone (single age, and metallicity).

    An :class:`Isochrone` is a :class:`astropy.table.Table`, but with
    additional attributes and methods.
    """
    def __init__(self, *args, **kwargs):
        super(Isochrone, self).__init__(*args, **kwargs)

    @property
    def z(self):
        """Metallicity of this isochrone."""
        return self.meta['Z']

    @property
    def age(self):
        """Age of this isochrone (yr)."""
        return self.meta['Age']

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
        return self.meta['header']

    @property
    def filter_names(self):
        """A list of (column) names of the filters included in this isochrone.
        """
        _non_mag_names = self.non_mag_names
        # Normally I'd use sets, but column ordering is important
        return [name for name in self.colnames
                if name not in _non_mag_names]

    @property
    def non_mag_names(self):
        """A list of all column names that are not bandpasses."""
        possible = ['log(age/yr)', 'M_ini', 'M_act', 'logL/Lo', 'logTe',
                    'logG', 'mbol', 'C/O', 'M_hec', 'period', 'pmode',
                    'logMdot',
                    'int_IMF', 'stage',
                    'Z', 'logageyr', 'logLLo']
        return [n for n in possible if n in self.colnames]

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
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        if os.path.exists(output_path):
            os.remove(output_path)
        fmt = {'m_ini': "%10.7f"}  # table writer formatting
        if bands is None:
            bandnames = self.filter_names
            for name in bandnames:
                fmt[name] = "%8.6f"
        else:
            bandnames = [n for n in bands if n in self.filter_names]
        self.write(output_path,
                   format='ascii.fixed_width_no_header',
                   formats=fmt,
                   delimiter=' ',
                   delimiter_pad=None,
                   bookend=False,
                   include_names=['M_ini'] + bandnames)


def join_isochrone_sets(left_set, right_set,
                        right_bands=None, left_bands=None):
    """Join two isochrone sets

    The expected use of this function is to combine filter sets (`photsys`)
    in two isochrone requests that otherwise have the same settings.

    Parameters
    ----------
    left_set : :class:`IsochroneSet`
        IsochroneSet on the 'left-side' of the join
    right_set : :class:`IsochroneSet`
        IsochroneSet on the 'right-side' of the join
    left_bands : list
        Bands to keep from the left side isochrones. Defaults to all minus
        those on the right side.
    right_bands : list
        Bands to keep from the right side isochrones. Defaults to all.

    Returns
    -------
    left_set : :class:`IsochroneSet`
        The joined-and-modified left isochrone set
    """
    itr = enumerate(zip(left_set.isochrones, right_set.isochrones))
    for i, (left_isoc, right_isoc) in itr:
        new_isoc = join_isochrones(left_isoc, right_isoc,
                                   right_bands=right_bands,
                                   left_bands=left_bands)
        left_set._isochrones[i] = new_isoc
    return left_set


def join_isochrones(left_isoc, right_isoc, right_bands=None, left_bands=None):
    """Join two isochrone tables.

    The expected use of this function is to combine filter sets (`photsys`)
    in two isochrone tables.

    Parameters
    ----------
    left_isoc : :class:`Isochrone`
        Isochrone on the 'left-side' of the join
    right_isoc : :class:`Isochrone`
        Isochrone on the 'right-side' of the join
    left_bands : list
        Bands to keep from the left side isochrones. Defaults to all minus
        those on the right side.
    right_bands : list
        Bands to keep from the right side isochrones. Defaults to all.

    Returns
    -------
    t : :class:`Isochrone`
        The joined isochrone table.
    """
    t_left = Isochrone(left_isoc)
    t_right = Isochrone(right_isoc)
    if right_bands is None:
        left_bands = t_left.filter_names

    if left_bands is not None:
        removed_bands = list(set(t_left.filter_names)
                             - set(left_bands))
        t_left.remove_columns(removed_bands)

    # Also remove bands from left that appear on the right
    left_bands = t_left.filter_names
    removed_bands = [b for b in left_bands if b in right_bands]
    t_left.remove_columns(removed_bands)

    # Trim the right table
    t_right.keep_columns(['M_ini'] + right_bands)

    t = Isochrone(join(t_left, t_right, join_type='left', keys='M_ini'))
    return t
