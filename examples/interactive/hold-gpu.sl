#!/bin/bash -e
#SBATCH --job-name      hold-gpu
#SBATCH --account       nesi99991
#SBATCH --time          00:15:00        # how long you may hold the GPU
#SBATCH --qos           debug           # start now, while you are here
#SBATCH --gpus-per-node l4:1            # the card you want to debug on
#SBATCH --cpus-per-task 2
#SBATCH --mem           4GB
#SBATCH --output        hold-gpu-%j.out

# A job that does nothing but wait.
#
# It asks for a GPU and then sleeps, so the GPU stays allocated to you while
# you work inside the job from a terminal of your own:
#
#   sbatch hold-gpu.sl
#   squeue --me                 # wait until ST is R, and note the JOBID
#   svisit <JOBID>              # a terminal inside the job, with its GPU
#   ...                         # run, check and debug things on the GPU
#   exit                        # leave the job - it keeps running
#   scancel <JOBID>             # give the GPU back
#
# svisit the same job as many times as you like, from as many terminals as you
# like: run your program in one and watch it with nvtop in another.
#
# The GPU is yours from the moment this starts until you scancel it or the
# time limit ends it, whether you are using it or not. Sleeping costs no CPU,
# but it holds a card somebody else could be using, so keep --time short and
# scancel as soon as you are done. The job's own output file stays almost
# empty - everything you run happens in your own terminals instead.

echo "Job ${SLURM_JOB_ID} is holding GPU '${CUDA_VISIBLE_DEVICES}' on ${SLURMD_NODENAME}."
echo "Visit it with:  svisit ${SLURM_JOB_ID}"
echo "Give it back:   scancel ${SLURM_JOB_ID}"

sleep infinity
