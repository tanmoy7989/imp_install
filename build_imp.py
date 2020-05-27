"""
##Conda+Python-3 based IMP install

This script builds Python-3 compatible minimal versions of the Sali-lab
software IMP. For quick-and-dirty builds as well as more extensive protocols,
please see the IMP documentation:
https://integrativemodeling.org/2.13.0/doc/manual/installation.html

###Required
Python-3 Anaconda (or Miniconda) distribution.
This is an entirely conda based installation, so it'll create its own
environment. Together with IMP, post-processing and analysis tools imp-sampcon
and PMI_Analysis are also installed.

###Supported platforms
a) Linux (tested on Ubuntu 16.04/18.04)
b) Mac OSX (tested on Mojave)
c) UCSF Wynton cluster (not working fully: WIP)

###AUTHOR
Tanmoy Sanyal,
Sali lab
"""

import os
import argparse

# parse input
parser = argparse.ArgumentParser(description=__doc__,
                           formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument("-p", "--platform", default="linux", help="platform")
parser.add_argument("-n", "--envname", default="impenv",
                    help="IMP conda env name")
parser.add_argument("-d", "--topdir", default="salilab",
                    help="Master dir where everything will be installed")

args = parser.parse_args()
platform = args.platform
envname = args.envname
topdir = os.path.abspath(args.topdir)

# create the top-dir
os.makedirs(topdir, exist_ok=True)

# clone from my forked repositories
sources = ["https://github.com/tanmoy7989/imp.git",
           "https://github.com/tanmoy7989/PMI_analysis.git"
           "https://github.com/tanmoy7989/imp-sampcon.git"]

sinks = ["imp", "pmi_analysis", "imp_sampcon"]

for (x, y) in zip(sources, sinks):
    print("Extracting %s" % y)
    print("-----------------------")
    cmd = "git clone %s %s" % (x, os.path.join(topdir, y))
    os.system(cmd)
    print("\n\n")

# write the env yml file to topdir
yml_dict = {"ENVNAME": envname}
yml_fn = os.path.join(topdir, "impenv.yml")
with open("impenv.yml.template", "r") as of:
    s = of.read()
with open(yml_fn, "w") as of:
    of.write(s % yml_fn)



