#!/bin/bash -e
#SBATCH --job-name      vram
#SBATCH --account       nesi99991
#SBATCH --time          00:10:00
#SBATCH --cpus-per-task 2
#SBATCH --mem           4GB
#SBATCH --gpus-per-node l4:1
#SBATCH --output        vram-%j.out

# Both memory demonstrations, in a job.
#
# Note the deliberate mismatch in this script's own request: 4 GB of --mem,
# and a GPU whose VRAM is whatever an L4 has. Those two numbers have nothing
# to do with each other, which is the point of the first script.

module purge
module load PyTorch/2.13.0-foss-2026-Python-3.14.4-CUDA-13.2.1

echo "=== Two separate pools ==="
python3 two_pools.py

echo
echo "=== Sizing and exhausting VRAM ==="
python3 how_much_vram.py

echo
echo "Afterwards, run 'seff ${SLURM_JOB_ID}'."
echo "Peak Mem Utilisation is the RAM line, and Peak GPU Memory Util the VRAM"
echo "line: two pools, counted separately. The VRAM line may well miss the"
echo "moment the card was full. seff only sees memory when it is sampled, and"
echo "this job filled the card for a fraction of a second."
