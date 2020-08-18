#$ -S /bin/bash
#$ -cwd
#
#$ -r n
#$ -j y
#$ -R y
#
#$ -l mem_free=4G
#$ -l h_rt=10:00:00
#$ -l scratch=200G
#
#$ -pe smp 8
#$ -N imp_install
#$ -o /wynton/scratch/tsanyal/
#$ -e /wynton/scratch/tsanyal/

hostname
date

# get a decent c compiler
module load Sali
module load gcc/7.3.1

# run build script
python build_imp.py -n impenv -o $HOME/mysoftware/salilab -m -np 8  

hostname
date

qstat -j $JOB_ID
