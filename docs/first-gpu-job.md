# 2. Your first GPU job

!!! clipboard-list "Lesson Objectives"

    - Know which `#SBATCH` lines a GPU job needs
    - Know which of them are real decisions, and where each is explained
    - Submit a GPU job, and read what it was given

!!! clipboard-question "Questions"

    - What goes in a GPU submit script?
    - Which lines actually matter?

## A submit script for a GPU job

Consider that you have a program that you would like to run on one or several
GPUs. A submit script like the one below will let you do that:

```bash
#!/bin/bash -e
#SBATCH --job-name      my-gpu-job
#SBATCH --account       nesi99991
#SBATCH --time          00:15:00
#SBATCH --gpus-per-node l4:1      (1)
#SBATCH --cpus-per-task 4         (2)
#SBATCH --mem           32GB      (3)
#SBATCH --output        my-job-%j.out

# Write the commands for running your GPU job in here
```

1. **The decision.** Which GPU, and how many.
2. **A decision.** CPU cores, which feed the GPU.
3. **A decision.** System RAM — *not* GPU memory.

Three lines in this script are real decisions, and the next part of the
workshop is about getting each of them right:

* `--gpus-per-node`: which GPU should you choose?
* `--cpus-per-task`: how many CPUs should you ask for?
* `--mem`: how much memory should you ask for?

Briefly, here is what each one is for.

---

## `--gpus-per-node` — which GPU

```bash
#SBATCH --gpus-per-node <type>:<how many>
```

The type of GPU, and how many of them. Different cards differ by more than
speed: they have different amounts of memory, and some are dramatically slower
at double-precision arithmetic than others. Getting this wrong is the single
most expensive mistake available, and it produces no error message.

**Always name the type.** Leaving it out gets you whatever happens to be free,
which makes runs impossible to compare with one another. (The two A100s share
a type, and need a `--constraint` as well.)

```bash
#SBATCH --gpus-per-node l4:1
```

**Ask for one.** Request more only if your software explicitly documents that
it can use more than one — most cannot, and a second GPU it ignores sits idle
for the whole job while somebody else waits for it.

→ [Which GPU: precision](precision.md) and
[Which GPU: will it fit?](gpu-memory.md)

## `--cpus-per-task` — how many CPU cores

```bash
#SBATCH --cpus-per-task 4
```

CPU cores for the job. A GPU job still needs them: the GPU cannot fetch its own
work, so the CPU reads and prepares every batch before the GPU sees it. Too few
cores and the GPU spends most of its time waiting.

→ [How many CPUs do I need?](how-many-cpus.md)

## `--mem` — how much system memory

```bash
#SBATCH --mem 8GB
```

Ordinary system RAM, attached to the CPU. **This is not the memory on the GPU**,
which you cannot request at all — it comes with whichever card you chose.
Confusing the two is the most common source of "I asked for more memory and it
did not help".

→ [How much CPU memory should I request?](cpu-memory.md)

## Run one

The files for this chapter are in `~/gpu-training/first-job`, and also
[on GitHub](https://github.com/nesi/reannz-intro-gpu-workshop/tree/main/examples/first-job){: target="_blank" rel="noopener" } to read outside the training environment.

!!! dumbbell "Exercise: your first GPU job"

    ```bash
    cd ~/gpu-training/first-job
    cat hello-gpu.sl
    sbatch hello-gpu.sl
    squeue --me
    ```

    It takes a few seconds. Once `squeue --me` no longer lists it, read what
    it printed:

    ```bash
    cat hello-gpu-<JobID>.out
    ```

    ??? "What you should see"

        ```
        Job 1000 is running on gpunode001
        Slurm gave this job GPU number: '0'
        ```

        followed by a table from `nvidia-smi`, with one card in it:

        ```
        |   0  NVIDIA L4                      On  |   00000000:00:04.0 Off |                    0 |
        | N/A   38C    P8             12W /  72W  |       1MiB /    200MiB |      0%      Default |
        ```

        Two things to notice. `CUDA_VISIBLE_DEVICES` is `0`: Slurm gave the
        job one GPU, and inside the job the GPUs it was given are numbered from
        0. And `nvidia-smi` shows one card, the L4 the script asked for.

        Neither of those proves that your *program* used it. That is the next
        chapter.

!!! graduation-cap "Keypoints"

    - Three lines are the real decisions: `--gpus-per-node`, `--cpus-per-task`
      and `--mem`.
    - `--gpus-per-node` picks the card, and cards differ in memory and in
      double-precision speed, not just in speed.
    - A GPU job still needs CPU cores, because the CPU feeds the GPU.
    - `--mem` is system RAM. There is **no flag for GPU memory** — it comes
      with the card you pick.
