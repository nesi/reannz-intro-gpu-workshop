# 10. Putting it all together

!!! clipboard-list "Lesson Objectives"

    - Watch a running job and judge from the live display whether the GPU is busy
    - Use `seff` across a set of finished jobs to find the smallest card your
      work fits in
    - Use `seff` and `profile_plot` to settle the core count and the memory
      request
    - Write the answers back into a production submit script

!!! clipboard-question "Questions"

    - I have the tools. How do I actually use them on a real job?
    - How do I know when I am finished tuning?

Everything so far has been one piece at a time. This chapter runs the whole
loop, on one job, from first guess to a script you would keep.

This is the diagram from [Which GPU: will it fit?](gpu-memory.md) again — it is the plan
for this entire chapter:

![Choosing a GPU](./fig/choosing-a-gpu.png){: .center}

We will work through it in three passes:

| Pass | Question | Tool |
|---|---|---|
| **1** | Is the job using the GPU at all, and what does it look like? | `nvtop`, live |
| **2** | Which card does it fit in? | `seff`, across several finished jobs |
| **3** | How many cores and how much memory does it need? | `seff` and `profile_plot` |

---

## Pass 1: watch a job while it runs

Before measuring anything carefully, look at the job with your own eyes. It
takes two minutes and it catches the failures that would make every later
measurement meaningless.

The files for this chapter are in `~/gpu-training/putting-it-together`, and
[on GitHub](https://github.com/nesi/reannz-intro-gpu-workshop/tree/main/examples/putting-it-together){: target="_blank" rel="noopener" }.

!!! dumbbell "Exercise 1: watch a job live"

    **Submit the job.**

    ```bash
    cd ~/gpu-training/putting-it-together
    cat watch-me.sl
    sbatch watch-me.sl
    ```

    **Find it, and jump onto its node.**

    ```bash
    squeue --me
    svisit <JobID>
    ```

    **Watch it.**

    ```bash
    nvtop
    ```

    Leave it running for a minute and watch the two graphs. Then press `q` to
    quit, and `exit` to come back to the login node.

    ??? "What you should see"

        A **sawtooth**. GPU utilisation climbs, drops back, climbs again —
        over and over, never settling high.

        That shape is the [starved GPU](how-many-cpus.md) from
        How many CPUs, seen live. Each rise is the GPU working on a
        batch; each fall is the GPU waiting while the CPU prepares the next
        one.

        GPU memory, meanwhile, will be flat. It was allocated at start-up and
        does not change.

**What you are checking for at this stage** is not a number, it is a category:

| What the display shows | What it means | What to do |
|---|---|---|
| Flat at zero, your process absent | The job is not using the GPU | Stop. Nothing below will help until that is fixed |
| Sawtooth | Starved between batches | Continue, and fix it in pass 3 |
| High and flat | Already well fed | Continue to pass 2 |
| Memory climbing without limit | A leak | Fix the code before tuning anything |

Only once the GPU is genuinely being used is there any point measuring how
*well* it is being used.

---

## Pass 2: which card does it fit in?

Now the memory ladder from the flow diagram. The same job has been run on each
card in turn, so you do not have to wait for five queues. The A100 jobs asked
for `a100:1` with `--constraint a100_40gb` or `a100_80gb`.

!!! dumbbell "Exercise 2: find the smallest card that fits"

    **Read what `seff` said about each job**, and fill in the table below.

    === "L4"

        ```
        Job ID: 2001001
        State: FAILED
        Tasks: 1
        Cores: 4
        Job Wall-time:          5%  00:00:48 of 00:15:00 time limit
        Avg CPU Utilisation:   55%  00:01:45 of 00:03:12 core-walltime
        Peak Mem Utilisation:  19%  6.20 GB of 32.00 GB
        Peak GPU Utilisation:  31%
        Peak GPU Memory Util:  95%  21.86 GB of 23 GB
        ```

    === "A100 40 GB"

        ```
        Job ID: 2001002
        State: COMPLETED
        Tasks: 1
        Cores: 4
        Job Wall-time:         67%  00:10:00 of 00:15:00 time limit
        Avg CPU Utilisation:   64%  00:25:36 of 00:40:00 core-walltime
        Peak Mem Utilisation:  19%  6.20 GB of 32.00 GB
        Peak GPU Utilisation:  35%
        Peak GPU Memory Util:  75%  30.10 GB of 40 GB
        ```

    === "A100 80 GB"

        ```
        Job ID: 2001003
        State: COMPLETED
        Tasks: 1
        Cores: 4
        Job Wall-time:         67%  00:10:00 of 00:15:00 time limit
        Avg CPU Utilisation:   64%  00:25:36 of 00:40:00 core-walltime
        Peak Mem Utilisation:  19%  6.20 GB of 32.00 GB
        Peak GPU Utilisation:  35%
        Peak GPU Memory Util:  38%  30.10 GB of 80 GB
        ```

    === "H100"

        ```
        Job ID: 2001004
        State: COMPLETED
        Tasks: 1
        Cores: 4
        Job Wall-time:         67%  00:10:00 of 00:15:00 time limit
        Avg CPU Utilisation:   64%  00:25:36 of 00:40:00 core-walltime
        Peak Mem Utilisation:  19%  6.20 GB of 32.00 GB
        Peak GPU Utilisation:  35%
        Peak GPU Memory Util:  32%  30.10 GB of 94 GB
        ```

    === "RTX PRO 6000"

        ```
        Job ID: 2001005
        State: COMPLETED
        Tasks: 1
        Cores: 4
        Job Wall-time:         67%  00:10:00 of 00:15:00 time limit
        Avg CPU Utilisation:   64%  00:25:36 of 00:40:00 core-walltime
        Peak Mem Utilisation:  19%  6.20 GB of 32.00 GB
        Peak GPU Utilisation:  35%
        Peak GPU Memory Util:  31%  30.10 GB of 96 GB
        ```

    | Card | State | GPU memory used | Fits? |
    |---|---|---|---|
    | L4 (24 GB) | | | |
    | A100 (40 GB) | | | |
    | A100 (80 GB) | | | |
    | H100 (94 GB) | | | |
    | RTX PRO 6000 (96 GB) | | | |

    ??? "What you should find"

        The L4 job **failed**. The others all completed, and all report the
        same peak GPU memory:

        | Card | State | GPU memory used | Fits? |
        |---|---|---|---|
        | L4 (24 GB) | `FAILED` | 21.9 GB of 23 GB — 95% | **No** |
        | A100 (40 GB) | `COMPLETED` | 30.1 GB of 40 GB — 75% | **Yes** |
        | A100 (80 GB) | `COMPLETED` | 30.1 GB of 80 GB — 38% | Yes |
        | H100 (94 GB) | `COMPLETED` | 30.1 GB of 94 GB — 32% | Yes |
        | RTX PRO 6000 (96 GB) | `COMPLETED` | 30.1 GB of 96 GB — 31% | Yes |

        The job needs about **30 GB**, so the L4's 24 GB was never going to be
        enough — and its output file will say so:

        ```
        torch.OutOfMemoryError: CUDA out of memory. Tried to allocate 512.00 MiB.
        GPU 0 has a total capacity of 21.97 GiB of which 118.00 MiB is free.
        Including non-PyTorch memory, this process has 21.86 GiB memory in use.
        Of the allocated memory 21.24 GiB is allocated by PyTorch, and
        310.00 MiB is reserved by PyTorch but unallocated. ...
        ```

        **The answer is the 40 GB A100**: `--gpus-per-node a100:1` with
        `--constraint a100_40gb`. It is the smallest card the job fits in,
        so it is the one you will wait least for. Every card above it runs the
        job at the same speed while holding memory somebody else needed.

!!! warning "75% is the right kind of full"

    A job filling 75% of its card has headroom for a slightly larger input
    without falling over, and is not wasting most of a scarce resource.

    **Below about 25%, look at the card underneath.** Above about 90%, look at
    the card above — you are one bigger input away from the L4's fate.

---

## Pass 3: how many cores, and how much memory?

The card is settled. Now the two requests that do not change which card you
need, but do change how well it is used.

### Cores

!!! dumbbell "Exercise 3a: settle the core count"

    The same job, on the 40 GB A100, submitted at five core counts. From each
    report, record two numbers: **Avg CPU Utilisation** and **Peak GPU
    Utilisation**.

    === "1 core"

        ```
        Job ID: 2002001
        State: COMPLETED
        Tasks: 1
        Cores: 1
        Job Wall-time:         97%  00:14:35 of 00:15:00 time limit
        Avg CPU Utilisation:  100%  00:14:35 of 00:14:35 core-walltime
        Peak Mem Utilisation:  10%  3.05 GB of 32.00 GB
        Peak GPU Utilisation:  24%
        Peak GPU Memory Util:  75%  30.10 GB of 40 GB
        ```

    === "2 cores"

        ```
        Job ID: 2002002
        State: COMPLETED
        Tasks: 1
        Cores: 2
        Job Wall-time:         75%  00:11:17 of 00:15:00 time limit
        Avg CPU Utilisation:   81%  00:18:17 of 00:22:34 core-walltime
        Peak Mem Utilisation:  13%  4.10 GB of 32.00 GB
        Peak GPU Utilisation:  31%
        Peak GPU Memory Util:  75%  30.10 GB of 40 GB
        ```

    === "4 cores"

        ```
        Job ID: 2002003
        State: COMPLETED
        Tasks: 1
        Cores: 4
        Job Wall-time:         67%  00:10:00 of 00:15:00 time limit
        Avg CPU Utilisation:   64%  00:25:36 of 00:40:00 core-walltime
        Peak Mem Utilisation:  19%  6.20 GB of 32.00 GB
        Peak GPU Utilisation:  35%
        Peak GPU Memory Util:  75%  30.10 GB of 40 GB
        ```

    === "8 cores"

        ```
        Job ID: 2002004
        State: COMPLETED
        Tasks: 1
        Cores: 8
        Job Wall-time:         65%  00:09:43 of 00:15:00 time limit
        Avg CPU Utilisation:   38%  00:29:33 of 01:17:46 core-walltime
        Peak Mem Utilisation:  32%  10.40 GB of 32.00 GB
        Peak GPU Utilisation:  36%
        Peak GPU Memory Util:  75%  30.10 GB of 40 GB
        ```

    === "16 cores"

        ```
        Job ID: 2002005
        State: COMPLETED
        Tasks: 1
        Cores: 16
        Job Wall-time:         65%  00:09:43 of 00:15:00 time limit
        Avg CPU Utilisation:   20%  00:31:06 of 02:35:33 core-walltime
        Peak Mem Utilisation:  59%  18.80 GB of 32.00 GB
        Peak GPU Utilisation:  36%
        Peak GPU Memory Util:  75%  30.10 GB of 40 GB
        ```

    ??? "What you should find"

        | Cores | CPU efficiency | GPU utilisation |
        |---|---|---|
        | 1 | 100% | 24% |
        | 2 | 81% | 31% |
        | 4 | 64% | **35%** |
        | 8 | 38% | 36% |
        | 16 | 20% | 36% |

        The same curve as [How many CPUs](how-many-cpus.md): GPU utilisation
        climbs steeply, then flattens at 4. Going from 4 cores to 16 buys one
        percentage point of GPU for four times the CPU request.

        **The answer is 4.**

        Note that the one-core job has the *best* CPU efficiency of the five
        and is the worst job of the five. CPU efficiency is a diagnostic, not
        a target.

!!! note "Use `profile_plot` when the average looks wrong"

    `seff` gives you 35% for the four-core job. If that figure is lower than
    you expected, plot it:

    ```bash
    profile_plot <JobID>
    ```

    A **steady** 35% and a job **alternating** between 100% and 0% both average
    35%, and they have completely different causes. Only the plot distinguishes
    them — see [Measuring a GPU job](measuring.md).

### Memory

!!! dumbbell "Exercise 3b: settle the memory request"

    Take the four-core job's report from exercise 3a, and look at the `Peak
    Mem Utilisation` line rather than the GPU ones:

    ```
    Peak Mem Utilisation:  19%  6.20 GB of 32.00 GB
    ```

    1. What was the peak CPU memory this job actually used?
    2. What was requested?
    3. What should the request be, allowing 20–30% headroom?

    ??? "Answer"

        The job peaked at **6.2 GB** and asked for **32 GB** — so 26 GB sat
        reserved and untouched for the whole run, making the job harder to
        schedule for no benefit.

        6.2 GB plus 30% is about 8 GB. **Ask for `--mem 8GB`.**

        Be careful not to size this from the one-core run. Memory scales with
        the core count ([How much CPU memory](cpu-memory.md)) — measure it at
        the core count you have actually chosen.

---

## Writing the answers back

Three passes, three answers, and one more to work out: how long to ask for.

### How long to ask for

The flow diagram had you record a step count in the 15-minute test, and this
is what it is for. If the test got through 1,250 steps in 15 minutes and the
real run needs 30,000, the run will take about 24 times as long: six hours.
Add 20–30% for the variation a single test will not show you, and ask for
eight.

Put it all in a script you would keep:

```bash
#!/bin/bash -e
#SBATCH --job-name      my-real-job
#SBATCH --account       nesi99991
#SBATCH --time          08:00:00      # (1)
#SBATCH --gpus-per-node a100:1        # (2)
#SBATCH --constraint    a100_40gb
#SBATCH --cpus-per-task 4             # (3)
#SBATCH --mem           8GB           # (4)
#SBATCH --output        my-job-%j.out

# your program here
```

1. **The step count.** The test's rate, times the steps you need, plus a
   margin. Past a day, read [B3: Long jobs](long-jobs.md) and checkpoint.
2. **Pass 2.** The smallest card the job fits in: the 40 GB A100, which
   takes a constraint ([Which GPU: precision](precision.md)).
3. **Pass 3a.** Where GPU utilisation stopped climbing.
4. **Pass 3b.** Measured peak, plus headroom.

!!! warning "Take the testing lines out"

    `--qos debug`, `--profile task` and `--acctg-freq=1` all belong to the
    15-minute test job and none of them belong here.

    Leaving `--qos debug` in a production script will get the job killed at the
    debug walltime limit. Leaving the profiling on writes a sample every second
    for the entire run.

    And `--time` comes from the step count, not from the 15 minutes the test
    needed.

!!! graduation-cap "Keypoints"

    - **Look before you measure.** A minute with `nvtop` tells you whether the
      job is worth measuring at all.
    - **Card first, then cores, then memory.** The card decides what is
      possible; the other two decide how well it goes.
    - The smallest card that fits is the right card. **75% full is healthy;
      under 25% means try the card below.**
    - Choose the core count where **GPU utilisation stops climbing**, not where
      CPU efficiency looks best.
    - Size memory from a run at the core count you have actually settled on.
    - Set `--time` from the test's **step count**, plus 20–30%.
    - **Strip the testing flags** before the script becomes a real job.
