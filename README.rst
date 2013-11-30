======
Padova
======

Padova is a small python package for working with the so-called `Padova evolutionary tracks <http://stev.oapd.inaf.it/cgi-bin/cmd>`_ produced by Girardi and collaborators.
Padova is compatible with the `Astropy`_ project.

Padova submits requests to the CMD 2.5 interface, downloads resulting data files, and provides tools to read those isochrone/luminosity function outputs into `Astropy`_ Table instances.

Please use this project *responsibly*. Don't push the CMD servers with too many requests.


Dependencies
------------

- astropy (including numpy, scipy, cython)
- mechanize


Tests
-----

You can run tests via:

    python setup.py test

The tests are located in ``padova/tests/``. Test data sets are 


Info
----

Copyright 2013 Jonathan Sick (@jonathansick)
Licensed BSD 2-clause.

.. _Astropy: http://www.astropy.org/
