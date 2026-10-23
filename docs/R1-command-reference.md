# R1: Command reference

Every command used in the workshop, with the flags that matter.

## Submitting and managing jobs

### `sbatch`

```bash
sbatch job.sl                    # submit
sbatch --parsable job.sl         # submit, print only the job ID
JOBID=$(sbatch --parsable job.sl)
sbatch --cpus-per-task 4 job.sl  # override a directive from the command line
```

Command-line options beat `#SBATCH` directives in the file.

### `#SBATCH` directives

| Directive | Asks for |
|---|---|
| `--job-name NAME` | A name, so you can find it in `squeue` |
| `--account CODE` | The project to charge |
| `--time DD-HH:MM:SS` | Wall-clock limit. The job is killed at this point |
| `--cpus-per-task N` | CPU cores |
| `--mem 8GB` | System RAM (not VRAM) |
| `--mem-per-cpu 2GB` | RAM per core, instead of a total |
| `--gpus-per-node TYPE:N` | GPUs, by type |
| `--constraint a100_40gb` | Which A100: `a100_40gb` or `a100_80gb` |
| `--output FILE-%j.out` | Where output goes. `%j` is the job ID |
| `--qos debug` | High priority, strict limits, one job at a time ([Debug QoS](https://docs.nesi.org.nz/Batch_Computing/Debug_QoS/)) |
| `--profile task` | Record resource use for `profile_plot` |
| `--acctg-freq 1` | Take those records once a second |
| `--dependency=afterok:ID` | Start only once job `ID` has succeeded |

### `squeue`

```bash
squeue --me                  # your jobs
squeue --me -t R             # just the running ones
squeue -j 12345              # one job
squeue --me -h               # no header (-h is NOT --help here)
squeue --me --start          # when pending jobs should start (not in the training environment)
```

`ST` column: `PD` pending, `R` running, `CG` completing. For a pending job, the
last column gives the reason it is waiting — see [B3: Long jobs](long-jobs.md#why-is-my-job-pending).

### `scancel`

```bash
scancel 12345                # one job
scancel -u $USER             # all of yours
```

### `scontrol`

```bash
scontrol show job 12345      # everything Slurm knows about a job
```

## Checking a GPU

### `nvidia-smi`

```bash
nvidia-smi                                          # the table
nvidia-smi -L                                       # just list the devices
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv --loop=5
```

Useful `--query-gpu` fields: `name`, `memory.total`, `memory.used`,
`memory.free`, `utilization.gpu`, `utilization.memory`, `temperature.gpu`,
`power.draw`, `compute_cap`.

!!! warning

    `nvidia-smi` is a snapshot. Use it to confirm a GPU is present, not to
    judge whether one is busy.

### `CUDA_VISIBLE_DEVICES`

```bash
echo "CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES}"
```

| Value | Means |
|---|---|
| `0` | One GPU |
| `0,1` | Two |
| empty | **No GPU was requested** |
| unset | Not inside a Slurm job |

### Asking your software

```bash
# PyTorch: is a GPU usable right now?
python -c "import torch; print(torch.cuda.is_available())"

# PyTorch: is this even a GPU-capable build?
python -c "import torch; print(torch.__version__, torch.version.cuda)"
#   2.14.0+cu124  12.4   -> a CUDA build
#   2.14.0+cpu    None   -> a CPU-only build; it will never use a GPU

# TensorFlow
python -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"
```

## Watching a running job

### `svisit`

```bash
svisit                       # your most recent running job
svisit 12345                 # a specific job
svisit 12345 nvtop           # run a command instead of a shell
svisit -t 12345              # show the srun command, do not run it
```

A wrapper around `srun --pty --overlap --jobid=...`.

### `nvtop`

```bash
nvtop
```

| Key | Does |
|---|---|
| `q` | Quit |
| `F2` | Setup |
| `F6` | Sort the process list |
| `F9` | Kill a process |
| `+` / `-` | Change the graph's time window |

## Interactive sessions

### A job that waits

```bash
sbatch hold-gpu.sl           # a job whose only command is: sleep infinity
svisit 12345                 # a terminal inside it, as often as you like
svisit 12345 nvtop           # or straight into a command
exit                         # leave the terminal - the job carries on
scancel 12345                # end the job, and give the GPU back
```

The GPU is held from the moment the job starts until `scancel` or the time
limit, whether you are using it or not.

### `srun --pty`

```bash
srun --gpus-per-node l4:1 --cpus-per-task 2 --mem 4GB --time 00:15:00 --pty bash
```

Asks for the GPU and puts you inside the job in one step. It ends when you
`exit` — or when your connection drops. Not available in the training
environment.

## After a job

### `seff`

```bash
seff 12345
seff -j 12345
seff 12345 12346             # several at once
```

```
Job ID: 12345
State: COMPLETED
Tasks: 1
Cores: 4
Job Wall-time:          3%  00:00:31 of 00:20:00 time limit
Avg CPU Utilisation:   99%  00:00:30 of 00:00:31 core-walltime
Peak Mem Utilisation:   6%  243.67 MB of 4.00 GB
Peak GPU Utilisation:  16%
Peak GPU Memory Util:   4%  9.00 MB of 200 MB
```

**No GPU lines means the job had no GPU.**

### `sacct`

```bash
sacct -j 12345
sacct -u $USER
sacct -j 12345 --format=JobID,JobName,State,Elapsed,MaxRSS
```

The raw records `seff` summarises.

### `profile_plot`

```bash
# with #SBATCH --profile task in the job
profile_plot 12345
```

A graph of resource use over the job, rather than a single average.

## Available in the training environment only

These exist because the environment emulates a GPU.

```bash
gpuemu-ctl status            # is the emulator running?
gpuemu-ctl start
```

```python
from gpuemu.phases import cpu_phase, gpu_phase, report

with cpu_phase("load"):
    data = load()
with gpu_phase("train"):
    step(data)
report()
```

Used by the exercises to show which stage of a script is which. On real
hardware the driver knows this already, so nothing like it is needed.
