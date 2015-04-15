======
Padova
======

Padova is a small python package for working with the so-called `Padova evolutionary tracks <http://stev.oapd.inaf.it/cgi-bin/cmd>`_ produced by Girardi and collaborators.
Padova is compatible with the `Astropy`_ project.

Take a look at this `Jupyter notebook <http://nbviewer.ipython.org/github/jonathansick/padova/blob/master/notebooks/demo.ipynb>`_ to see what Padova can do.

Of course, please use this project *responsibly*.
Don't abuse the CMD servers.


Features
--------

- Simple interfaces to obtain either single isochrones or grids of isochrones.
- Validation of settings before requesting data from the CMD servers.
- Caching of requests so you don't hit the CMD servers when you ask for an isochrone set you already have.
- Isochrones are provided as `Astropy`_ tables with metadata.


Dependencies
------------

- numpy
- `Astropy`_
- Requests
- pytoml
- setuptools


Tests
-----

You can run tests via:

    python setup.py test

The tests are located in ``padova/tests/``.


Credits
-------

- Padova provides data from the CMD web site, which is a produce of Leo Girardi and collaborators.
- Padova takes inspiration from `ezpadova`_ by Morgan Fouesneau.


Info
----

Copyright 2013-2015 Jonathan Sick (@jonathansick).

Some parts are adapted from `ezpadova`_, Copyright 2015 Morgan Fouesneau.

Padova is MIT licensed.

.. _Astropy: http://www.astropy.org/
.. _ezpadova: https://github.com/mfouesneau/ezpadova
