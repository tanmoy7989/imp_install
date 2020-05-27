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

####Directory structure
The top-dir can be optionally specified and defaults to ./salilab.
IMP, PMI_Analysis and imp-sampcon are extracted respectively into topdir/imp,
topdir/pmi_analysis and topdir/imp-sampcon. IMP is built into todir/imp_release

###AUTHOR
Tanmoy Sanyal,
Sali lab
"""

import os
import subprocess
import argparse


# has conda?
try:
    import conda
except ImportError:
    print("Error: Anaconda or Miniconda distribution not found")

# has python-3?
import sys
version = sys.version_info
if not version.major == 3:
    print("Python-3 not is recommended. Since this installed has not been tested"
          "with Python-2, it will quit")
    exit()

# parse input
parser = argparse.ArgumentParser(description=__doc__,
                           formatter_class=argparse.RawDescriptionHelpFormatter)

parser.add_argument("-n", "--envname", default="impenv",
                    help="IMP conda env name")
parser.add_argument("-d", "--topdir", default="salilab",
                    help="Master dir where everything will be installed")
parser.add_argument("-np", "--nproc", type=int, default=1,
                    help="Number of processors for parallel build")

args = parser.parse_args()
envname = args.envname
topdir = os.path.abspath(args.topdir)
nproc = args.nproc

# create the top-dir
os.makedirs(topdir, exist_ok=True)

# clone from my forked repositories
sources = ["https://github.com/salilab/imp.git",
           "https://github.com/tanmoy7989/PMI_analysis.git",
           "https://github.com/tanmoy7989/imp-sampcon.git"]

sinks = ["imp", "pmi_analysis", "imp_sampcon"]

for (x, y) in zip(sources, sinks):
    print("Extracting %s" % y)
    print("-----------------------")
    cmd = "git clone -b master %s %s" % (x, os.path.join(topdir, y))
    os.system(cmd)
    if y == "imp":
        cmd_next = "cd %s && git submodule update --init && ./setup_git.py"
        #os.system(cmd_next % os.path.join(topdir, y))
    print("\n\n")

# write the env yml file to topdir
yml_dict = {"ENVNAME": envname}
env_fn = os.path.join(topdir, "impenv.yml")
with open("impenv.yml.template", "r") as of:
    s = of.read()
with open(env_fn, "w") as of:
    of.write(s % yml_dict)

# create and populate this conda environment
print("Creating and populating conda env: %s" % envname)
cmd = """
conda env create -f %s
conda clean -t
""" % env_fn
os.system(cmd)

# run platform specific install-scripts
print("\n\nBuilding IMP")
platform = os.uname().sysname.lower()
if platform == "linux":
    print("Linux detected\n")
    cmd = "bash make_linux.sh %s %s %d" % (envname, topdir, nproc)
    os.system(cmd)



