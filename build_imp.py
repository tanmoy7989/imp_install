"""
Conda+Python-3 based IMP install for production or development

This script builds Python-3 compatible minimal versions of the Sali-lab
software IMP. For quick-and-dirty builds as well as more extensive protocols,
please see the IMP documentation:
https://integrativemodeling.org/2.13.0/doc/manual/installation.html

It supports either a development mode where IMP is built from scratch, so that
you can add to it and do tests, or a production mode which simply pulls the
latest stable pre-built binary available from conda.

Required:
Python-3 Anaconda (or Miniconda) distribution.
This is an entirely conda based installation, so it'll create its own
environment. Together with IMP, post-processing and analysis tools imp-sampcon
and PMI_Analysis are also installed.

Supported platforms:
a) Linux (tested on Ubuntu 16.04/18.04)
b) Mac OSX (tested on Mojave)
c) UCSF Wynton cluster (not working fully: WIP)

Directory structure:
The top-dir can be optionally specified and defaults to ./salilab.
IMP, PMI_Analysis and imp-sampcon are extracted respectively into topdir/imp,
topdir/pmi_analysis and topdir/imp-sampcon. IMP is built into todir/imp_release

Author:
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
parser.add_argument("-dev", "--dev_mode", action="store_true",
                    help="True to do a 'dev-mode' install of IMP from scratch")
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


def _do_production_mode():
    #TODO: imp and openmpi conda installs have a conflict!
    #clone from source
    sources = ["https://github.com/salilab/PMI_analysis.git",
               "https://github.com/salilab/imp-sampcon.git"]

    sinks = ["pmi_analysis", "imp_sampcon"]

    for (x, y) in zip(sources, sinks):
        print("Extracting %s" % y)
        print("-----------------------")
        cmd = "git clone -b master %s %s" % (x, os.path.join(outdir, y))
        os.system(cmd)
        print("\n\n")

    # write the env yml file to a temp-file
    yml_dict = {"ENVNAME": envname}
    env_fn = os.path.join(outdir, "impenv.yml")
    with open("impenv.yml.template", "r") as of:
        s = of.read()
    with open(env_fn, "w") as of:
        of.write(s % yml_dict)

    # create and populate this conda environment
    print("Creating and populating production conda env: %s" % envname)
    cmd = """
    conda env create -f %s
    conda clean -t
        """ % env_fn
    os.system(cmd)

    # add analysis script paths to bashrc
    s = """
export PYTHONPATH=$PYTHONPATH:%s/pmi_analysis/pyext/src
    """ % outdir
    with open(os.path.expanduser("~/.bashrc"), "a") as of:
        of.write(s)


def _do_dev_mode():
    # create the top-dir
    global disabled_modules_str
    os.makedirs(outdir, exist_ok=True)

    #clone from my forked repositories
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
    with open("impenv_dev.yml.template", "r") as of:
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

    # write build log to file
    timestamp = datetime.now().strftime("%d%B%Y_%I:%M_%p")
    log_fn = os.path.join(outdir, "IMP_build_spec_%s.txt" % timestamp)
    with open(log_fn, "w") as of:
        of.write(log_str)

    # add necessary env variables to bashrc
    s = """
export PYTHONPATH=$PYTHONPATH:%s/pmi_analysis/pyext/src
IMPENV=%s/imp_release/setup_environment.sh
    """ % (outdir, outdir)
    
    with open(os.path.expanduser("~/.bashrc"), "a") as of:
        of.write(s)



if __name__ == "__main__":
    if dev_mode:
        _do_dev_mode()
    else:
        _do_production_mode()
