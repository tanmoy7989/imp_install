## Conda+Python-3 based IMP install for production or development

![](xkcd.png) 

This script builds Python-3 compatible minimal versions of the Sali-lab
software IMP. For quick-and-dirty builds as well as more extensive protocols,
please see the [IMP documentation](https://integrativemodeling.org/2.13.0/doc/manual/installation.html)

It supports either a development mode where IMP is built from scratch, so that
you can add to it and do tests, or a production mode which simply pulls the
latest stable pre-built binary available from conda.

### Required

Python-3 Anaconda (or Miniconda) distribution.
This is an entirely conda based installation, so it'll create its own
environment. Together with IMP, post-processing and analysis tools imp-sampcon
and PMI_Analysis are also installed.

### Supported platforms

a) Linux (tested on Ubuntu 16.04 / 18.04, Fedora-31)
b) Mac OSX (tested on Mojave)
c) UCSF Wynton cluster (not working fully: WIP)

### Directory structure

The top-dir can be optionally specified and defaults to ./salilab.
IMP, PMI_Analysis and imp-sampcon are extracted respectively into topdir/imp,
topdir/pmi_analysis and topdir/imp-sampcon. IMP is built into todir/imp_release

### Author

Tanmoy Sanyal,
Sali lab