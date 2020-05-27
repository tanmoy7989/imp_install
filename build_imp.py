"""
This script builds minimal versions of the Sali-lab software IMP. For
doc
"""

import os
import argparse

parser = argparse.ArgumentParser(description="Build IMP")
parser.add_argument("-f", default="linux", help="framework")
