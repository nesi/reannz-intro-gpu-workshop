# 4. Reading seff

!!! clipboard-list "Lesson Objectives"

    - Run `seff` on a finished job and read every line
    - Decide from the output whether a GPU was worth requesting
    - Use the CPU and GPU efficiency figures together, rather than one at a time

!!! clipboard-question "Questions"

    - How do I find out what a job actually used, after it has finished?
    - Which number tells me whether the GPU earned its place?

## The report card

`nvtop` needs you to be watching. `seff` does not — it reads the accounting
records the scheduler kept, so it works on any job that has finished, including
one that ran last month.

```bash
seff <jobid>
```

```
Job ID: 1000
State: COMPLETED
Tasks: 1
Cores: 1
Job Wall-time:          3%  00:00:31 of 00:20:00 time limit
Avg CPU Utilisation:   99%  00:00:30 of 00:00:31 core-walltime
Peak Mem Utilisation:   6%  243.67 MB of 4.00 GB
Peak GPU Utilisation:  16%
Peak GPU Memory Util:   1%  9.00 MB of 1 GB
```

Line by line:

| Line | What it compares | What you do about it |
|---|---|---|
| `Job Wall-time` | How long it ran vs `--time` | Very low: reduce `--time`, your jobs will start sooner. At 100% the job was **killed** before finishing |
| `Avg CPU Utilisation` | CPU time used vs cores × runtime | Low means you asked for more cores than you used |
| `Peak Mem Utilisation` | Most RAM held vs `--mem` | Low means reduce `--mem`. Near 100% means raise it before it gets killed |
| `Peak GPU Utilisation` | How busy the GPU was | **The number that says whether the GPU was worth asking for** |
| `Peak GPU Memory Util` | Most VRAM held vs the card's capacity | Low means a smaller GPU would have done |

!!! warning "No GPU lines means no GPU"

    If the last two lines are missing entirely, the job never had a GPU. Not
    "had one and did not use it" — never had one.

    This is the fastest way to audit a pile of old jobs and find the ones that
    were silently running on the CPU. You do not need to have been watching,
    and you do not need to rerun anything.

!!! note "Why is it called *Peak* GPU Utilisation?"

    Because it is the peak across the job's steps, and within a step the
    figure is an average over time. For an ordinary single-step job — which is
    almost every job — it is simply the average utilisation over the run.

    A true instantaneous peak would be useless: every job that touches the GPU
    at all touches 100% of it for a moment.

## What counts as a good number

There is no single threshold, but as a rough guide for `Peak GPU Utilisation`:

| Reading | Interpretation |
|---|---|
| Above 80% | The GPU is the bottleneck. A faster or larger GPU would help |
| 40–80% | Reasonable. Worth a look at whether the CPU side can be improved |
| 10–40% | The GPU is waiting most of the time. Fix that before asking for a better card |
| Under 10% | Ask whether this job needs a GPU at all |

!!! warning "Both efficiencies matter, and they pull against each other"

    A single number is never the whole story. Consider two jobs:

    ```
    Cores: 1                          Cores: 4
    Avg CPU Utilisation:   99%        Avg CPU Utilisation:   64%
    Peak GPU Utilisation:  16%        Peak GPU Utilisation:  40%
    ```

    The first looks excellent on CPU efficiency and is in fact the worse job:
    it is pinned at 99% CPU because it is desperately trying to keep up, and
    the GPU it was given sat idle 84% of the time.

    The second "wastes" CPU — but it finished in a third of the time and got
    two and a half times as much out of the GPU.

    **Read them together.** High CPU with low GPU means the GPU is starved.
    Low CPU with high GPU means you asked for cores you did not need.

## Do it

The two example jobs are the ones the numbers above came from. They run
identical work; the only difference is `--cpus-per-task`.

```bash
cd ~/gpu-training/04_reading_seff
cat starved.sl        # 1 core
cat fed.sl            # 4 cores
```

```bash
sbatch starved.sl
sbatch fed.sl
squeue --me
```

When both have finished:

```bash
seff <starved jobid>
seff <fed jobid>
```

Each job also prints its own breakdown of where the time went, from inside:

```
Where the time went
----------------------------------------------
  CPU  prepare data             23.0s   86.0%
  GPU  compute                   3.7s   14.0%
                             ----------------
       total                    26.8s  100.0%

The GPU was busy for 14% of this run.
```

Compare that 14% against `seff`'s `Peak GPU Utilisation: 16%`. The two are
measured completely differently — one from inside the program, one from the
scheduler's accounting — and they agree. That agreement is what makes both
worth trusting.

!!! dumbbell "Exercise: read four jobs"

    Run `seff` on all four jobs you have submitted so far: `hello-gpu`,
    `forgot-the-gpu`, `starved` and `fed`. For each one answer:

    1. Did it have a GPU?
    2. Was the GPU busy?
    3. What would you change about the request next time?

    ??? "Answer"

        | Job | Had a GPU? | Busy? | Change |
        |---|---|---|---|
        | `hello-gpu` | Yes | No — it only ran `nvidia-smi` | Nothing; it was a test |
        | `forgot-the-gpu` | **No GPU lines at all** | — | Add `--gpus-per-node` |
        | `starved` | Yes | 16% | More cores |
        | `fed` | Yes | 40% | Better. Try more cores again and see if it keeps climbing |

        Note that `hello-gpu` shows 0% GPU utilisation while having a perfectly
        good GPU. That is correct and not a problem — the job never asked the
        GPU to do anything. **0% utilisation is only a problem when you
        expected work to happen.**

!!! note "Other tools for the same job"

    - `sacct -j <jobid>` gives the raw accounting records `seff` summarises.
    - `#SBATCH --profile task` plus `profile_plot <jobid>` produces a graph of
      resource use over the job, which is worth it for long runs where a single
      average hides the interesting parts.

!!! graduation-cap "Keypoints"

    - `seff <jobid>` after every job, until it is a habit.
    - **Missing GPU lines mean the job had no GPU.**
    - `Peak GPU Utilisation` is the number that justifies requesting a GPU.
    - Read CPU and GPU efficiency **together**: 99% CPU with 16% GPU is a
      starved job, not a good one.
    - `Job Wall-time` at 100% means the job was killed, not that it finished.
