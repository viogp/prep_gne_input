#!/bin/bash -l

#Run: sbatch slurm.sh
#Check: squeue -u dc-gonz3  or showq | grep dc-gonz3

#SBATCH -n 1 # Number of cores needed
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=4096
#SBATCH -J prep_galform_input # Job name
#SBATCH -o standard_output_file.%J.out
#SBATCH -e standard_error_file.%J.err
#SBATCH -p cosma5 # Partition/queue, e.g. cosma, cosma8, etc.
#SBATCH -A durham # Project, e.g. dp004
#SBATCH -t 72:00:00
#SBATCH --mail-type=END # notifications for job done &fail
#SBATCH --mail-user=violetagp@protonmail.com

module purge
#load the modules used to build your program.
module load cosma
module load python

#Run the program
python prep_galform_input.py

