# Summary and checklist

Everything from the workshop, on one page.

## The four questions

Everything else exists to answer these.

| # | Question | Measure it with |
|---|---|---|
| 1 | Does my software need double precision (fp64)? | Its documentation |
| 2 | How much VRAM does my work need? | Arithmetic, then `seff` |
| 3 | How many CPU cores keep the GPU fed? | Submit at 1, 2, 4, 8 and compare |
| 4 | What fraction of my runtime is on the GPU? | Timers around your stages |

## A GPU job script, annotated

```bash
#!/bin/bash -e
#SBATCH --job-name      my-job
#SBATCH --account       nesi99991
#SBATCH --time          01:00:00     # from a measured run, plus a margin
#SBATCH --cpus-per-task 4            # measured: the point GPU util stopped rising
#SBATCH --mem           8GB          # RAM. From seff's Peak Mem Utilisation
#SBATCH --gpus-per-node l4:1         # smallest card your work fits in
#SBATCH --output        my-job-%j.out

# Record what this job could see. Costs nothing, settles arguments later.
echo "CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES}"
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader

module load CUDA/11.0.2               # if your software needs it
srun my_program --use-gpu
```

## The workflow

1. **Check your software supports GPUs.** Most does not. Requesting a GPU does
   not make a program use one.
2. **Request one**, naming the type: `--gpus-per-node l4:1`.
3. **Confirm you got it** — `CUDA_VISIBLE_DEVICES` is not empty, and your
   *software* reports a device, not just `nvidia-smi`.
4. **Watch it live** the first time: `squeue --me` → `svisit <jobid>` → `nvtop`.
5. **Read `seff`** afterwards. Every time.
6. **Adjust and repeat.**

## Which tool, when

| Question | Tool | Not |
|---|---|---|
| Is there a GPU I can use? | `nvidia-smi` | |
| Did my software find it? | Ask the software | `nvidia-smi` |
| Is it busy *right now*? | `nvtop`, via `svisit` | `nvidia-smi` — one sample proves nothing |
| Was it busy *overall*? | `seff` | `nvidia-smi` |
| Did this job have a GPU at all? | `seff` — no GPU lines means no GPU | |
| How much VRAM did it use? | `seff`'s `Peak GPU Memory Util` | |
| How much RAM did it use? | `seff`'s `Peak Mem Utilisation` | |

## Reading seff

```
Job Wall-time:          3%  00:00:31 of 00:20:00 time limit
Avg CPU Utilisation:   99%  00:00:30 of 00:00:31 core-walltime
Peak Mem Utilisation:   6%  243.67 MB of 4.00 GB
Peak GPU Utilisation:  16%
Peak GPU Memory Util:   1%  9.00 MB of 1 GB
```

| Reading | Means | Do |
|---|---|---|
| No GPU lines | The job had no GPU | Add `--gpus-per-node` |
| GPU util under 10% | The GPU did nothing | Ask whether you need one |
| GPU util 10–40% | Starved | More cores; check storage |
| GPU util above 80% | GPU-bound | A faster card would help |
| CPU 100% + GPU low | Starved | More cores |
| CPU low + GPU high | Too many cores | Request fewer |
| GPU memory under 25% | Card too big | Use a smaller one |
| GPU memory over 95% | Nearly out | Smaller batch, or bigger card |
| Wall-time 100% | **Killed, not finished** | More `--time` |

## The five mistakes

1. **Forgetting `--gpus-per-node`.** No error. The job runs on CPU, thirty
   times slower, and only `seff` will tell you.
2. **Confusing RAM and VRAM.** `--mem` will never fix "CUDA out of memory".
3. **Trusting one `nvidia-smi` reading.** It is a snapshot. Use `nvtop` or
   `seff`.
4. **Starving the GPU of CPU cores.** The commonest inefficiency there is.
5. **Running fp64 work on an L4 or RTX PRO 6000.** Up to sixty times slower,
   with no error message.

## The GPUs

| GPU | VRAM | Per node | fp64 | Request | Good for |
|---|---|---|---|---|---|
| L4 | 24 GB | 4 | 1:62 | `l4:1` | fp32 work that fits. Shortest queue |
| A100 | 80 GB | 4 | **1:2** | `a100:1` | fp64, and large models |
| H100 NVL | 94 GB | 2 | **1:2** | `h100:1` | fp64 and the largest models |
| RTX PRO 6000 | 96 GB | 2 | 1:63 | `pro_6000:1` | Large fp32/fp16 work. Not fp64 |

**Take the smallest card your work fits in.** Shorter queue, fairer share, same
result.

## Before you queue anything long

```bash
#SBATCH --qos debug
#SBATCH --time 00:15:00
```

Run it short, `seff` it, then commit. Fifteen minutes saves days.

!!! graduation-cap "If you remember five things"

    1. **Software has to support GPUs.** Requesting one changes nothing on its own.
    2. **`seff` after every job.** No GPU lines means no GPU.
    3. **RAM and VRAM are different pools.** `--mem` is not GPU memory.
    4. **A GPU needs CPUs to feed it.** Start at 2, then measure.
    5. **fp64 work belongs on an A100 or H100.** Nothing else comes close.

## Where to go next

- [Using GPUs](https://docs.nesi.org.nz/Batch_Computing/Using_GPUs/) — the
  cluster's own reference, including application-specific pages
- [Hardware](https://docs.nesi.org.nz/Batch_Computing/Hardware/) — the full
  node and GPU specifications
- Application pages for
  [TensorFlow](https://docs.nesi.org.nz/Software/Available_Applications/TensorFlow/),
  [AlphaFold](https://docs.nesi.org.nz/Software/Available_Applications/AlphaFold/),
  [ABAQUS](https://docs.nesi.org.nz/Software/Available_Applications/ABAQUS/)
  and
  [ont-guppy-gpu](https://docs.nesi.org.nz/Software/Available_Applications/ont-guppy-gpu/)
- [NVIDIA GPU containers](https://docs.nesi.org.nz/Software/Containers/NVIDIA_GPU_Containers/),
  if your software is easier to get as a container
- [Slurm native profiling](https://docs.nesi.org.nz/Software/Profiling_and_Debugging/Slurm_Native_Profiling/)
  — `--profile task` and `profile_plot`, for when an average is not enough
