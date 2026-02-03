#!/bin/sh
# Template for SLURM job submission
# This file serves as a reference - the actual template is embedded in generate_input_slurm.py
# Placeholders: JOB_NAME, SIM_NAME, SNAP_NUM, SUBVOLS_LIST, VERBOSE

#SBATCH -A 16cores
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --job-name=JOB_NAME
#SBATCH --error=output/JOB_NAME.err
#SBATCH --output=output/JOB_NAME.out
##SBATCH --mem=600000
#SBATCH --partition=all
#SBATCH --time=30-00:00:00
#
export OMP_NUM_THREADS=16
srun python -c "
from src.prep_input import prep_input
prep_input('SIM_NAME', SNAP_NUM, SUBVOLS_LIST, validate_files=False, generate_files=True, verbose=VERBOSE)
"
