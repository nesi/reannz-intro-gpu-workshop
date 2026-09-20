# 6. How many CPUs does a GPU job need?

!!! clipboard-list "Lesson Objectives"

    - Explain why a GPU job needs CPU cores at all
    - Measure the number of cores your own job needs, rather than guessing
    - Recognise the point where adding cores stops helping

!!! clipboard-question "Questions"

    - I asked for a GPU. Why does the number of CPUs matter?
    - How do I pick a number?

## Why a GPU job needs CPUs

A GPU cannot fetch its own work. Every batch of data it processes has to be
read from disk, decoded, filtered, reshaped and handed over — and all of that
happens on the CPU.

So a GPU job is really two jobs taking turns:

```
CPU:  [ prepare batch 1 ][ prepare batch 2 ][ prepare batch 3 ]
GPU:                     [ compute 1 ]      [ compute 2 ]      [ compute 3 ]
                          ^^^^^^^^^^^
                          the GPU waits here, doing nothing
```

If preparing a batch takes longer than computing on it, the GPU spends most of
its life idle. Adding CPU cores lets the preparation happen in parallel, which
shortens the wait.

**This is why a GPU job with too few CPUs is a job that paid for a GPU and then
starved it.** It is probably the most common inefficiency in GPU work on any
cluster.

## There is no formula

The right number depends entirely on how much work your code does per batch
before the GPU sees it, which varies by orders of magnitude between
applications. The only reliable method is to measure your own job.

!!! note "A starting point, before you have measured anything"

    ```bash
    #SBATCH --cpus-per-task 2
    ```

    Two is rarely badly wrong. One is often badly wrong. This is also what the
    [cluster documentation](https://docs.nesi.org.nz/Batch_Computing/Using_GPUs/)
    suggests as a default.

    Then measure, and adjust.

## Measuring it

Submit the same job at several core counts and compare:

```bash
cd ~/gpu-training/06_how_many_cpus
./scan-cpus.sh
```

```
submitted 1000 with 1 CPU(s)
submitted 1001 with 2 CPU(s)
submitted 1002 with 4 CPU(s)
```

Wait for them with `squeue --me`, then:

```bash
./compare.sh
```

```
Job ID: 1000
Cores: 1
Avg CPU Utilisation:  100%  00:00:27 of 00:00:27 core-walltime
Peak GPU Utilisation:  24%

Job ID: 1001
Cores: 2
Avg CPU Utilisation:   81%  00:00:29 of 00:00:36 core-walltime
Peak GPU Utilisation:  31%

Job ID: 1002
Cores: 4
Avg CPU Utilisation:   64%  00:00:37 of 00:00:58 core-walltime
Peak GPU Utilisation:  35%
```

## Reading the result

Put it in a table and the shape is obvious:

| Cores | CPU efficiency | GPU utilisation |
|---|---|---|
| 1 | 100% | 24% |
| 2 | 81% | 31% |
| 4 | 64% | **35%** |

Two things are happening at once:

- **GPU utilisation climbs and then flattens.** 24 → 31 → 35. The gain from 1
  to 2 cores is large; from 2 to 4 it is much smaller. That flattening is the
  point you are looking for.
- **CPU efficiency falls the whole way.** At one core the CPU is pinned at
  100%, desperately trying to keep up. By four cores it is idle a third of the
  time.

**The right answer is the smallest core count that gets GPU utilisation onto
the flat part of the curve.** Here that is somewhere around 2–4. Beyond it you
are paying for cores that make the GPU no busier, while making your job harder
to schedule.

!!! warning "100% CPU efficiency is not a goal"

    The one-core job has the best CPU efficiency of the three and is the worst
    job of the three. It took more than twice as long and got a third less out
    of the GPU.

    When you have a GPU, the GPU is the expensive resource. CPU efficiency is a
    secondary consideration — useful for spotting that you asked for far more
    cores than you can use, not something to maximise.

!!! dumbbell "Exercise: find the flat part"

    1. Run `./scan-cpus.sh` and `./compare.sh` as above.
    2. Plot or sketch GPU utilisation against core count.
    3. Which core count would you request for this job, and why?
    4. The training session only has 4 cores. If you were on the cluster, where
       a GPU node has 64 or 168, how would you extend this experiment — and how
       would you know when to stop?

    ??? "Answer"

        3. 2 or 4. The step from 1 to 2 buys 7 percentage points of GPU
           utilisation; 2 to 4 buys another 4. Given the CPU efficiency cost,
           2 is defensible and 4 is defensible; 1 is not.

        4. Keep doubling — 8, 16 — and stop when GPU utilisation stops rising
           by a meaningful amount. If it flattens at 8, request 8. If it is
           still climbing at 16, the job is genuinely CPU-heavy and chapter 7
           is the more useful chapter for it.

## Other things that starve a GPU

More cores are not always the answer. If utilisation stays low no matter how
many you add, the bottleneck is elsewhere:

| Symptom | Likely cause | Fix |
|---|---|---|
| Adding cores changes nothing, CPU efficiency low | Reading files is the bottleneck | Read in larger chunks; use faster storage; stage data to local disk first |
| Utilisation low, memory nearly full | Batch size too small for the card | Increase the batch size |
| Utilisation spiky with long flat gaps | The job is waiting on something external | Look at what happens between the spikes |
| Software uses one core no matter what | It does not parallelise data loading | Check for a "workers" or "threads" setting |

!!! note "Where the cores come from"

    A GPU node is shared. On this cluster, an A100 node has 64 cores and 4
    GPUs, so a fair share is about 16 cores per GPU; a node with 4 L4s has 168
    cores, so about 42.

    You are not limited to that, but it is a reasonable ceiling to have in
    mind: asking for 32 cores alongside one L4 is unlikely to be justified, and
    will keep you waiting.

!!! graduation-cap "Keypoints"

    - A GPU needs CPU cores to feed it. Too few, and it sits idle.
    - **Start at `--cpus-per-task 2`**, then measure.
    - Submit the same job at several core counts and compare
      `Peak GPU Utilisation`.
    - Choose the smallest count where GPU utilisation stops climbing.
    - Falling CPU efficiency is the expected cost of a busier GPU, not a
      problem in itself.
    - If more cores change nothing, the bottleneck is storage or the software —
      not core count.
