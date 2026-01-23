#!/bin/sh
# author: Santiago Arranz Sanz
# usage: ./slurm_taurus.sh

# Nombre base del job
bn="prep_galform_input"

# Crear el script de envío SLURM
echo "#!/bin/sh
#SBATCH -A 16cores
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --job-name=$bn
#SBATCH --error=$bn.err
#SBATCH --output=$bn.out
##SBATCH --mem=600000
#SBATCH --partition=all
#SBATCH --time=30-00:00:00
#
export OMP_NUM_THREADS=16
srun python prep_galform_input.py" > submit_$bn

# Enviar el trabajo
sbatch submit_$bn
