#!/bin/bash

# download my version of IMP and post-processing tools
git clone https://github.com/tanmoy7989/imp.git

git clone https://github.com/tanmoy7989/PMI_analysis.git

git clone https://github.com/tanmoy7989/imp-sampcon.git

# create new conda environment from yml file
# this needs to be in the same directory as this script
conda env create -f tsanyal_IMP.yml

# clean up un-necessary tarballs
conda clean -t

# activate this conda environment
conda activate impenv

# setup python env
PYTHON_ROOT=`python -c "import sys; print(sys.prefix)"`
PYTHON_INC=$(python -c "from distutils.sysconfig import get_python_inc; print(get_python_inc())")
PYTHON_LIB=$(python -c "import distutils.sysconfig as sysconfig; print(sysconfig.get_config_var('LIBDIR'))")

# setup cmake env
CMAKE_ROOT=$CONDA_PREFIX
CMAKE_LIB=$CONDA_PREFIX/lib
CMAKE_INC=$CONDA_PREFIX/include

# setup cgal env
CGAL_DIR=$CONDA_PREFIX/lib/cmake/CGAL

# create a new directory in which to build IMP
mkdir ./imp_release

cd ./imp_release

# build IMP
cmake ../imp \
     -DCMAKE_BUILD_TYPE=Release \
     -DPYTHON_LIBRARY=$PYTHON_LIB \
     -DPYTHON_INCLUDE_DIR=$PYTHON_INC \
     -DCMAKE_LIBRARY_PATH=$CMAKE_LIB \
     -DCMAKE_PREFIX_PATH=$CMAKE_ROOT \
     -DCMAKE_INCLUDE_PATH=$CMAKE_INC \
     -DCGAL_DIR=$CGAL_DIR

make -j2
