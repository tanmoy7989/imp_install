#!/bin/bash

eval "$(conda shell.bash hook)"
conda activate $1

# setup cgal env
CGAL_DIR=$CONDA_PREFIX/lib/cmake/CGAL

# create a new directory in which to build IMP
cd $2
mkdir -p ./imp_release

# build IMP
cd ./imp_release
cmake ../imp \
     -DCGAL_DIR=$CGAL_DIR \
     -DCMAKE_BUILD_TYPE=Release \
     -DCMAKE_PREFIX_PATH=$CONDA_PREFIX \
     -DCMAKE_INCLUDE_PATH=$CONDA_PREFIX/include \
     -DCMAKE_LIBRARY_PATH=$CONDA_PREFIX/lib \
     -DIMP_DISABLED_MODULES=$3

make -j$4
touch .done
