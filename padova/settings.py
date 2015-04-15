#!/usr/bin/env python
# encoding: utf-8
"""
CMD Settings.

This module assists with documenting, validating and storing settings for
the CMD web api.
"""

import sys
import os
from collections import OrderedDict
import hashlib

if sys.version_info[0] > 2:
    from urllib.parse import urlencode
else:
    from urllib import urlencode

from pkg_resources import resource_stream
import pytoml as toml


class Settings(object):
    """Store user settings and validate against the schema for the Padova
    CMD web app.

    Parameters
    ----------
    f : stream-like
        A file stream to the TOML settings file.
    kwargs :
        User settings
    """
    def __init__(self, f, **kwargs):
        super(Settings, self).__init__()
        d = toml.load(f)
        # Ordering is import to consistently build a hash for caching
        self._schema = OrderedDict(sorted(d.items(), key=lambda t: t[0]))
        self._aliases = self._index_aliases()
        self._user_settings = {}
        # Self-validate
        self.validate()
        # Add any user settings
        self.update(kwargs)

    @classmethod
    def load_package_settings(cls, name="cmd_2_6.toml", **kwargs):
        """Load a settings file that ships with `Padova`.

        Parameters
        ----------
        name : str
            Name of the TOML file.
        kwargs :
            User settings
        """
        f = resource_stream(__name__,
                            os.path.join("data", "settings", name))
        return cls(f, **kwargs)

    def _index_aliases(self):
        """Build a hash of alias names back to full names."""
        aliases = {}
        for k, table in self._schema.iteritems():
            if 'alias' in table:
                aliases[table['alias']] = k
        return aliases

    def _resolve_key(self, k):
        if k in self._schema:
            key = k
        elif k in self._aliases:
            key = self._aliases[k]
        else:
            raise KeyError('Unknown settings key: {0}'.format(k))
        return key

    def _format_value(self, key, table, v):
        if 'format' in table:
            return table['format'].format(**{key: v})
        else:
            return v

    def _validate(self, key, v):
        k = self._resolve_key(key)
        table = self._schema[k]
        if table['kind'] == 'static':
            assert v == table['default'], 'Cannot override {0}'.format(key)
        elif table['kind'] == 'choices':
            assert v in table['choices'], '{0}: {1} invalid'.format(key, v)
        elif table['kind'] == 'range':
            r = table['range']
            assert (v >= min(r)) and (v <= max(r)), '{0}: {1} outside range'.\
                format(key, v)

    def validate(self):
        """Validates all settings: defaults or user overrides."""
        for k, v in self.iteritems():
            self._validate(k, v)

    def __setattr__(self, name, value):
        # Attempt to add a user's setting as an attribute
        try:
            k = self._resolve_key(name)
            self._validate(k, value)
            self._user_settings[k] = value
        except (AttributeError, KeyError):
            super(Settings, self).__setattr__(name, value)

    def __delattr__(self, name):
        # Attempt to delete a user's setting first
        try:
            k = self._resolve_key(name)
            if k in self._user_settings:
                del self._user_settings[k]
        except KeyError:
            super(Settings, self).__delattr__(name)

    def __len__(self):
        return len(self._schema)

    def __getitem__(self, key):
        k = self._resolve_key(key)
        try:
            return self._user_settings[k]
        except KeyError:
            return self._schema[k]['default']

    def __setitem__(self, key, value):
        k = self._resolve_key(key)
        self._validate(k, value)
        self._user_settings[k] = value

    def __delitem__(self, key):
        # Only delete user settings
        k = self._resolve_key(key)
        if k in self._user_settings:
            del self._user_settings[k]

    def __hash__(self):
        """Build a hash given the current settings."""
        # String to build hash against
        q = urlencode(self.settings)
        m = hashlib.md5()
        m.update(q)
        return m.hexdigest()

    @property
    def defaults(self):
        """A dict of the formatted default settings."""
        defs = OrderedDict()
        for k, table in self._schema.iteritems():
            key = self._resolve_key(k)
            v = table['default']
            val = self._format_value(key, table, v)
            defs[key] = val
        return defs

    @property
    def settings(self):
        """A dict of the formatted settings (including user settings)."""
        s = OrderedDict()
        for k, v in self.iteritems():
            table = self._schema[k]
            s[k] = self._format_value(k, table, v)
        return s

    def iteritems(self):
        """Iterate through all setting key-value pairs.

        Note: the values are *unformatted*.
        """
        for k, table in self._schema.iteritems():
            if k in self._user_settings:
                yield k, self._user_settings[k]
            else:
                yield k, table['default']

    def update(self, h):
        """Update the user settings with a dict-like."""
        for k, v in h.iteritems():
            key = self._resolve_key(k)
            self._validate(key, v)
            self._user_settings[key] = v
