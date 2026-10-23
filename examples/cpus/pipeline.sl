#!/bin/bash -e
#SBATCH --job-name      pipeline
#SBATCH --account       nesi99991
#SBATCH --time          00:20:00
#SBATCH --cpus-per-task 2
#SBATCH --mem           4GB
#SBATCH --gpus-per-node l4:1
#SBATCH --output        pipeline-%j.out

# The job scan-cpus.sh submits, once for each core count.
#
# Options given to sbatch on the command line win over the #SBATCH lines in
# the script, so
#
#   sbatch --cpus-per-task 4 pipeline.sl
#
# runs this same job on four cores. pipeline.py prepares its data with as many
# workers as the job has cores.

module purge
module load PyTorch/2.13.0-foss-2026-Python-3.14.4-CUDA-13.2.1

python3 pipeline.py --batches 40
