# 1. The submit script

!!! clipboard-list "Lesson Objectives"

    - Know which `#SBATCH` lines a GPU job needs
    - Know which of them are real decisions, and where each is explained

!!! clipboard-question "Questions"

    - What goes in a GPU submit script?
    - Which lines actually matter?

## Setting up a slurm script for testing GPU efficiency

Consider that you have a program that you would like to run on one or several GPUs. 
A submit script like the one shown below will allow you to do this as quickly as possible
before running your GPU job fully on an HPC. 

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

There are three component of this slurm script that we will tune in order
to optimise the resources you are asking for as well as to optimise the 
efficiency and performance of the GPUs for your job. These are:

* `--gpus-per-node`: Which GPU should we choose?
* `--cpus-per-task`: How many CPUs should we choose?
* `--mem`: How much memory should we ask for?

Let's briskly talk about each of these tags we need to consider:

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
which makes runs impossible to compare with one another.

```bash
#SBATCH --gpus-per-node l4:1
```

**Ask for one.** Request more only if your software explicitly documents that
it can use more than one — most cannot, and a second GPU it ignores sits idle
for the whole job while somebody else waits for it.

→ [Chapter 2: Which GPU](02-which-gpu.md) — which type to name

## `--cpus-per-task` — how many CPU cores

```bash
#SBATCH --cpus-per-task 4
```

CPU cores for the job. A GPU job still needs them: the GPU cannot fetch its own
work, so the CPU reads and prepares every batch before the GPU sees it. Too few
cores and the GPU spends most of its time waiting.

→ [Chapter 3: How many CPUs](03-how-many-cpus.md)

## `--mem` — how much system memory

```bash
#SBATCH --mem 8GB
```

Ordinary system RAM, attached to the CPU. **This is not the memory on the GPU**,
which you cannot request at all — it comes with whichever card you chose.
Confusing the two is the most common source of "I asked for more memory and it
did not help".

→ [Chapter 4: How much memory](04-how-much-memory.md)

!!! graduation-cap "Keypoints"

    - Three lines are the real decisions: `--gpus-per-node`, `--cpus-per-task`
      and `--mem`.
    - `--gpus-per-node` picks the card, and cards differ in memory and in
      double-precision speed, not just in speed.
    - A GPU job still needs CPU cores, because the CPU feeds the GPU.
    - `--mem` is system RAM. There is **no flag for GPU memory** — it comes
      with the card you pick.
