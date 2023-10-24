#!/bin/sh
#PBS -l nodes=1:ppn=96
#PBS -q P9242-8
#PBS -N Analysis
#PBS -j oe
#PBS -o flux_ana_output.log
#PBS -e flux_ana_error.log

export OMP_NUM_THREADS=96

cd $PBS_O_WORKDIR

python /path/to/move_count_across_z_plane.py


