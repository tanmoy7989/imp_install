"""
## Conda+Python-3 based IMP install

This script builds Python-3 compatible minimal versions of the Sali-lab
software IMP. For quick-and-dirty builds as well as more extensive protocols,
please see the [IMP documentation](https://integrativemodeling.org/2.13.0/doc/manual/installation.html)

You can disable certain IMP modules in the build process. Some 'heavy' modules
can be auto-disabled with the ```-m``` [--minimal_install]``` option.

### Required
Python-3 Anaconda (or Miniconda) distribution.
This is an entirely conda based installation, so it'll create its own
environment. Together with IMP, post-processing and analysis tools imp-sampcon
and PMI_Analysis are also installed.

### Supported platforms:
a) Linux (tested on Fedora-31, WIP: Ubuntu-20.04, Wynton cluster)
b) Mac OSX Mojave (WIP)

### Output directory structure:
The outdir can be optionally specified and defaults to ```./salilab```.
IMP, PMI_Analysis and imp-sampcon are extracted respectively into ```outdir/imp```,
```outdir/pmi_analysis``` and ```outdir/imp-sampcon```.
IMP is built into ```outdir/imp_release```

### Author:
Tanmoy Sanyal,
Sali lab
"""

import os
import subprocess
import argparse
from datetime import datetime


# has conda?
try:
    import conda
except ImportError:
    print("Error: Anaconda or Miniconda distribution not found")

# has python-3?
import sys
version = sys.version_info
if not version.major == 3:
    raise TypeError("This script is exclusively meant for Python-3 installs")

# parse input
parser = argparse.ArgumentParser(description=__doc__,
                           formatter_class=argparse.RawDescriptionHelpFormatter)

parser.add_argument("-n", "--envname", default="impenv",
                    help="IMP conda env name")
parser.add_argument("-o", "--outdir", default="salilab",
                    help="Master dir where everything will be installed"
                         "for dev mode installs")
parser.add_argument("-np", "--nproc", type=int, default=1,
                    help="Number of processors for parallel build")
parser.add_argument("-d", "--disabled_modules", nargs="+", default=[],
                    help="list of IMP modules to *NOT* build")
parser.add_argument("-m", "--minimal_install", action="store_true",
                    help="True to do a minimal install. This disables build of heavy modules "
                         "multifit:membrane:spb:npc:foxs:saxs_merge:npctransport")

args = parser.parse_args()
envname = args.envname
dev_mode = args.dev_mode
outdir = os.path.abspath(args.outdir)
nproc = args.nproc
disabled_modules = set(args.disabled_modules)
minimal_install = args.minimal_install
if minimal_install:
    heavy_modules = ["multifit", "membrane", "spb", "npc", "npctransport",
                     "foxs", "saxs_merge"]
    disabled_modules |= set(heavy_modules)


# create the output dir
os.makedirs(outdir, exist_ok=True)

# extract from salilab repos
sources = ["https://github.com/salilab/imp.git",
           "https://github.com/salilab/PMI_analysis.git",
           "https://github.com/salilab/imp-sampcon.git"]

sinks = ["imp", "pmi_analysis", "imp_sampcon"]

for (x, y) in zip(sources, sinks):
    print("Extracting %s" % y)
    print("-----------------------")
    cmd = "git clone -b master %s %s" % (x, os.path.join(outdir, y))
    os.system(cmd)
    if y == "imp":
        cmd_next = "cd %s && git submodule update --init && ./setup_git.py"
        os.system(cmd_next % os.path.join(outdir, y))
    print("\n\n")

# write the env yml file to topdir
yml_dict = {"ENVNAME": envname}
env_fn = os.path.join(outdir, "impenv.yml")
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

# detect platform
platform = os.uname().sysname.lower()
if platform == "linux":
    script = "make_imp_linux.sh"
elif platform == "darwin":
    script = "make_imp_macosx.sh"
else:
    raise NotImplementedError("Not tested for platform %s" % platform)

# get disabled modules
disabled_modules_str = ":".join(disabled_modules)
if not disabled_modules_str:
    disabled_modules_str = '""'
log_str = """
IMP build specs:
>>platform=%s
>>base conda env=%s
>>build from scratch=True
>>number of processors for parallel build=%d
>>disabled modules= %s
>>minimal install=%s
""" % (platform, os.environ["CONDA_PREFIX"], nproc,
       disabled_modules_str, minimal_install)

print(log_str)
print("\nPress any key to start the build...")
input()

# build!
cmd = "bash %s %s %s %s %d" % \
      (script, envname, outdir, disabled_modules_str, nproc)
os.system(cmd)

# check if successful
success = os.path.isfile(os.path.join(outdir, ".done"))
log_str += """
>>success=%s
""" % success

# write build log to file
timestamp = datetime.now().strftime("%d%B%Y_%I:%M_%p")
log_fn = os.path.join(outdir, "IMP_build_spec_%s.txt" % timestamp)
with open(log_fn, "w") as of:
    of.write(log_str)

# add necessary env variables to bashrc
if success:
    bashrc_s = """
export PYTHONPATH=$PYTHONPATH:%s/pmi_analysis/pyext/src
IMPENV=%s/imp_release/setup_environment.sh
    """ % (outdir, outdir)
    
    with open(os.path.expanduser("~/.bashrc"), "a") as of:
        of.write(s)