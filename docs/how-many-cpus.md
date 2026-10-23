# 6. How many CPUs do I need?

!!! clipboard-list "Lesson Objectives"

    - Explain why a GPU job needs CPU cores at all
    - Pick a starting number, and know what measuring it will look like
    - Recognise that high CPU efficiency is not the goal
    - Tell CPU work that feeds the GPU from CPU work that only keeps the cores
      busy

!!! clipboard-question "Questions"

    - I asked for a GPU. Why does the number of CPUs matter?
    - How do I pick a number?
    - My job does other CPU work in the background. Does that count?

## Why a GPU job needs CPUs

A GPU has to be given a batch of work by the CPU to perform. 
Every batch it processes has to be read from
disk, decoded, filtered, reshaped and handed over, all on the CPU. So a GPU job
is really two jobs taking turns:

![How the CPU feeds the GPU](./fig/cpu-feeds-gpu.svg#only-light){: width="700px" .center}
![How the CPU feeds the GPU](./fig/cpu-feeds-gpu_dark.svg#only-dark){: width="700px" .center}

This is **one CPU core feeding one GPU**. This is the worst arrangement available. 
Some points to take away from this arrangement: 

- **The CPU never stops.** It prepares batch 2 while the GPU is working on
  batch 1, then batch 3, and so on. Its track is solid the whole way across.
- **The GPU cannot start until a batch exists.** The dotted arrows are the
  handovers. Batch 1 is not ready until the CPU has finished making it, which
  is why the GPU's first stretch is spent waiting rather than computing.
- **Computing is quicker than preparing here.** So the GPU finishes each batch
  before the next one is ready, and has nothing to do in between. Those are the
  hatched gaps, and they are the whole problem.

There are two important points to take from this:

- **If preparing a batch takes longer than computing on it, the GPU spends more 
  of the job waiting than working.** Note that the GPU is the expensive half of the machine.
- **More cores let the preparation happen in parallel, which shortens each blue 
  block and closes the gaps.**

**Conclusion: A GPU job with too few CPUs paid for a GPU and then starved it.** It is
probably the most common inefficiency in GPU work anywhere.

## What it looks like when the GPU is fed

Here is the same job again — same preparation cost, same computation cost — with
**four CPU cores** instead of one:

![The same job with four CPU cores](./fig/cpu-feeds-gpu-fed.svg#only-light){: width="700px" .center}
![The same job with four CPU cores](./fig/cpu-feeds-gpu-fed_dark.svg#only-dark){: width="700px" .center}

Nothing about the GPU changed. What changed is that the four cores prepare four
*different* batches at the same time, so batches now arrive faster than the GPU
can get through them.

The GPU still waits for the very first batch — nothing can prevent that, since
batch 1 does not exist until somebody makes it. But from that point on its track
is **solid**, with no hatched gaps anywhere. Batches 2, 3 and 4 were finished by
the other three cores long before the GPU needed them, and were sitting waiting.

**This is what you are aiming for. Keep the GPU busy!**

!!! circle-info "Both figures are a simplification"

    They show work flowing one way — the CPU prepares, the GPU computes — and
    stop there. Two things are deliberately left out.

    **Results coming back.** Whatever the GPU produces has to return to the CPU
    at some point. In a training run that is almost nothing, because the model
    stays on the card and only a single number comes back each step. In a
    simulation it is periodic: forces, energies or a trajectory frame every so
    many steps.

    **Post-processing.** Writing that frame out, checking convergence, updating
    a log — all of it runs on the CPU, and **competes for the same cores as the
    preparation**. A core busy writing the last result is not preparing the next
    piece of work.

    This does not change the lesson: the CPU side
    has more to do than the pictures admit, so the cost of asking for too few
    cores is higher, not lower. But it does mean the blue blocks stand for
    *everything the CPU does for the GPU*, not only reading input.

## Work in the background

In the four-core picture, the cores do their work **in the background**: while
the GPU computes one batch, they are already preparing the next ones. That is
what keeps it fed, but only if your software prepares batches that way. In
PyTorch, for example, it is the `num_workers` setting of a `DataLoader`, and
the default, `num_workers=0`, prepares every batch in your main program, one at
a time, however many cores you asked for.

Not everything running in the background feeds the GPU, though. The
post-processing in the note above is one example; a job can be busy with
plenty of CPU work that the GPU never waits for. Whether it matters to the GPU
depends on what it is:

| Running in the background | Does the GPU need it? |
|---|---|
| Preparing the next batches | **Yes.** This is what feeds it |
| Part of every step done on the CPU, such as some of the forces in a molecular dynamics code | **Yes.** The GPU waits for it at the end of each step |
| Writing results, checkpoints and logs | **No**, though it takes cores from the work that does |
| Another program started in the same job | **No**, unless it makes something the GPU will use |

Here is the four-core job again, with two of its cores taken by a CPU job
running in the background:

![Four busy CPU cores, two of them on a background job](./fig/cpu-feeds-gpu-background.svg#only-light){: width="700px" .center}
![Four busy CPU cores, two of them on a background job](./fig/cpu-feeds-gpu-background_dark.svg#only-dark){: width="700px" .center}

All four cores are busy all of the time, so `seff` would report a CPU
efficiency close to 100%. Yet the GPU is back to waiting, because only two of
the four cores are making batches. **Busy cores are not the same as a fed
GPU.**

Background work the GPU does not need still needs cores of its own:

- **If it has to happen in this job** — writing the results, say — ask for its
  cores on top of the ones feeding the GPU.
- **If it does not** — an analysis of earlier output, another program started
  alongside — run it as a separate CPU-only job. The cores on a GPU node are
  there to feed its GPUs.

## How many CPUs do I need for my job?

The number of CPU you need depends entirely on how much work your code does per
batch before the GPU sees it, and that varies by orders of magnitude between
applications. However, you can test how many CPUs you need by looking at the 
CPU and GPU efficiency as you change the number of CPU you use:

In this example, we hypothesis running the same job, but submitted with different
numbers of cores:

| Cores | CPU efficiency | GPU utilisation |
|---|---|---|
| 1 | 100% | 24% |
| 2 | 81% | 31% |
| 4 | 64% | **35%** |
| 8 | 38% | 36% |
| 16 | 20% | 36% |

Two things happen at once:

- **GPU utilisation climbs, then flattens.** 24 → 31 → 35 → 36 → 36. The gain
  from 1 to 2 is large, 2 to 4 is smaller, and **beyond 4 there is nothing left
  to gain**. That flattening is the point you are looking for.
- **CPU efficiency falls the whole way.** At one core the CPU is pinned at 100%
  trying to keep up. By four it is idle a third of the time, and by sixteen it
  is idle four-fifths of the time.

The last two rows are the important ones. Going from 4 cores to 16 is four times
the CPU request for **one percentage point** of extra GPU use — cores that do
nothing except make your job harder to schedule and eat into your fair share.

**Ask for the smallest core count that gets GPU utilisation onto the flat part
of the curve** — here, 4.

Background work the GPU does not need shifts the whole curve to the right. If
a background job took two cores, GPU utilisation would only stop climbing at
about six, and CPU efficiency would look healthier in every row without the GPU
being any busier. **The GPU column is the one to trust.**

!!! dumbbell "Optional exercise: measure the curve yourself"

    Measure a small version of the table above: the same job at one, two and
    four cores. The scripts are also [on GitHub](https://github.com/nesi/reannz-intro-gpu-workshop/tree/main/examples/cpus){: target="_blank" rel="noopener" }.

    ```bash
    cd ~/gpu-training/cpus
    ./scan-cpus.sh
    squeue --me                # wait until all three have finished
    ./compare.sh
    ```

    The three jobs take about a minute between them.

    ??? "What you should see"

        Something like:

        | Cores | CPU efficiency | GPU utilisation |
        |---|---|---|
        | 1 | 99% | 25% |
        | 2 | 84% | 39% |
        | 4 | 67% | 48% |

        The same shape as the start of the table above: GPU utilisation
        climbs with every core added, while CPU efficiency falls. At four
        cores it is still climbing, if more slowly, so for this job you would
        keep going — 8, 16 — until it stops.

!!! graduation-cap "Keypoints"

    - A GPU needs CPU cores to feed it. Too few, and it sits idle.
    - **Start at `--cpus-per-task 2`**, then measure.
    - Choose the smallest count where GPU utilisation stops climbing.
    - Falling CPU efficiency is the expected cost of a busier GPU, not a
      problem in itself.
    - Background CPU work only helps if the GPU needs it. **Busy cores are not
      a fed GPU**: give other work cores of its own, or a job of its own.
    - If more cores change nothing, the bottleneck is storage or the software —
      check that it prepares batches in the background.
