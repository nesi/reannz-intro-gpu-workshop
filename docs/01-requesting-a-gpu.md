# 1. Requesting a GPU

!!! clipboard-list "Lesson Objectives"

    - Write a Slurm script that requests a GPU
    - Explain what each of the four resource flags asks for
    - Recognise what a job looks like when you forgot to ask for a GPU

!!! clipboard-question "Questions"

    - How do I ask Slurm for a GPU?
    - What happens if I forget?

## The flag

```bash
#SBATCH --gpus-per-node=<type>:<how many>
```

For example:

```bash
#SBATCH --gpus-per-node=l4:1
```

That is one L4. The type is not optional in practice: if you leave it out you
get whatever is free, which makes your results impossible to compare between
runs.

The types available on this cluster:

| GPU | VRAM | Max per node | Slurm request |
|---|---|---|---|
| NVIDIA L4 | 24 GB | 4 | `--gpus-per-node=l4:1` |
| NVIDIA A100 | 80 GB | 4 | `--gpus-per-node=a100:1` |
| NVIDIA H100 NVL | 94 GB | 2 | `--gpus-per-node=h100:1` |
| NVIDIA RTX PRO 6000 | 96 GB | 2 | `--gpus-per-node=pro_6000:1` |

Chapter 9 is about choosing between them. For now, use `l4:1`.

!!! note "Ask for one"

    Request more than one GPU only if your software explicitly says it can use
    more than one. Most cannot. A second GPU that your software ignores sits
    idle for the whole job, and it was a GPU somebody else needed.

## A complete job script

Open a terminal (**File → New → Terminal** in JupyterLab) and look at the
first example:

```bash
cd ~/gpu-training/01_requesting_a_gpu
cat hello-gpu.sl
```

```bash title="hello-gpu.sl"
#!/bin/bash -e
#SBATCH --job-name      hello-gpu
#SBATCH --account       nesi99991
#SBATCH --time          00:05:00
#SBATCH --cpus-per-task 2
#SBATCH --mem           2GB
#SBATCH --gpus-per-node l4:1
#SBATCH --output        hello-gpu-%j.out

echo "Job ${SLURM_JOB_ID} is running on ${SLURMD_NODENAME}"
echo "Slurm gave this job GPU number: '${CUDA_VISIBLE_DEVICES}'"
echo

nvidia-smi
```

There are four resource requests here and it is worth being clear about what
each one is:

| Flag | Asks for | Common mistake |
|---|---|---|
| `--cpus-per-task 2` | CPU cores | Asking for 1, and starving the GPU (chapter 6) |
| `--mem 2GB` | Ordinary system RAM | Confusing this with GPU memory (chapter 5) |
| `--gpus-per-node l4:1` | The GPU itself | Leaving it out entirely |
| `--time 00:05:00` | Wall-clock limit | Asking for far more than you need |

!!! warning "`--mem` is not GPU memory"

    `--mem` is ordinary RAM attached to the CPU. It has nothing to do with the
    GPU's own memory, which you cannot request directly — you get whatever the
    card you asked for happens to have. This catches almost everybody once.
    Chapter 5 is entirely about this distinction.

## Submit it

```bash
sbatch hello-gpu.sl
```

```
Submitted batch job 1000
```

Check on it:

```bash
squeue --me
```

```
             JOBID PARTITION     NAME     USER ST       TIME NODES NODELIST(REASON)
              1000       gpu hello-gp  learner  R       0:02     1 gpunode001
```

`ST` is the state. `PD` is pending (waiting for resources), `R` is running.
When the job disappears from `squeue`, it has finished.

Then read the output:

```bash
cat hello-gpu-1000.out
```

```
Job 1000 is running on gpunode001
Slurm gave this job GPU number: '0'

+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 550.54.15              Driver Version: 550.54.15      CUDA Version: 12.4     |
|-----------------------------------------+------------------------+----------------------+
| GPU  Name                 Persistence-M | Bus-Id          Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |           Memory-Usage | GPU-Util  Compute M. |
|                                         |                        |               MIG M. |
|=========================================+========================+======================|
|   0  NVIDIA L4                      On  |   00000000:00:04.0 Off |                    0 |
| N/A   38C    P8             12W /  72W  |       1MiB /   1024MiB |      0%      Default |
+-----------------------------------------+------------------------+----------------------+
```

You asked for a GPU and you got one.

!!! note "Why does it say 1024MiB and not 24GB?"

    Because this is the training environment, where the card is emulated and
    deliberately given 1 GB so that running out of memory is quick to
    demonstrate. On the cluster an L4 reports 23034MiB. Everything else on
    this page is identical.

## `CUDA_VISIBLE_DEVICES`

The line that printed `'0'` is the one to remember.

When Slurm gives your job a GPU, it sets an environment variable called
`CUDA_VISIBLE_DEVICES` listing the GPUs you are allowed to use. Every GPU
library on the machine reads it. You do not set it yourself and you should not
change it — but you should know how to read it, because it is the fastest way
to tell whether a job has a GPU.

| `CUDA_VISIBLE_DEVICES` | Means |
|---|---|
| `0` | You have one GPU, numbered 0 |
| `0,1` | You have two |
| *empty* | **You asked for no GPUs, so you have none** |
| not set at all | You are not inside a Slurm job |

## What forgetting looks like

```bash
cat forgot-the-gpu.sl
```

This is the same script with `--gpus-per-node` deleted. Submit it:

```bash
sbatch forgot-the-gpu.sl
```

It does not fail. It does not warn you. It starts *sooner* than the GPU job
did, because any node will take a job that needs no GPU. And the output says:

```
Job 1001 is running on gpunode001
Slurm gave this job GPU number: ''

No devices were found
```

An empty `CUDA_VISIBLE_DEVICES`, and an `nvidia-smi` that finds nothing.

!!! warning "Why this matters more than it looks"

    In this example the script only ran `nvidia-smi`, so the problem is
    obvious. Real software is not so helpful. **Most GPU-aware programs do not
    stop when they cannot find a GPU — they quietly carry on using the CPU.**

    Your job runs. It produces correct results. It takes thirty times longer
    than it should, and nothing in the output tells you why. People lose weeks
    to this.

    Chapter 2 is about making sure it never happens to you.

!!! dumbbell "Exercise: make the mistake on purpose"

    1. Submit both scripts:
       ```bash
       sbatch hello-gpu.sl
       sbatch forgot-the-gpu.sl
       ```
    2. When both have finished, compare the two output files side by side.
    3. Now run `seff` on each of them:
       ```bash
       seff <jobid of hello-gpu>
       seff <jobid of forgot-the-gpu>
       ```

    **What is different about the two `seff` outputs?** You have not met `seff`
    properly yet — that is chapter 4 — but one difference should jump out.

    ??? "Answer"

        The job that had a GPU has two extra lines:

        ```
        Peak GPU Utilisation:   0%
        Peak GPU Memory Util:   0%  1.00 MB of 1 GB
        ```

        The job that did not have one has no GPU lines at all.

        That absence is how you tell, weeks later and without rerunning
        anything, which of your jobs were really using the GPU you thought you
        had asked for. It is the single most useful thing on this page.

!!! note "A tip worth adopting now: `--qos debug`"

    Before you queue a long job, run a short version of it:

    ```bash
    #SBATCH --qos debug
    #SBATCH --time 00:15:00
    ```

    The debug QOS has a 15 minute limit and jumps the queue, so you find out
    that you forgot `--gpus-per-node` in two minutes rather than the following
    morning.

!!! graduation-cap "Keypoints"

    - Request a GPU with `#SBATCH --gpus-per-node=<type>:<count>`, and always
      name the type.
    - `--mem` is system RAM, not GPU memory. They are unrelated.
    - `CUDA_VISIBLE_DEVICES` tells you which GPUs your job may use. **Empty
      means none.**
    - Forgetting `--gpus-per-node` does not produce an error. It produces a
      slow job, and a `seff` report with no GPU lines in it.
    - Test with `--qos debug` before committing to a long run.
