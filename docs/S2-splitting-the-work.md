# S2: Splitting CPU and GPU work

!!! circle-info "Supplementary"

    This sits outside the main sequence. It is the natural next step once you
    can read `seff` and find your GPU utilisation lower than you would like:
    it is about working out which parts of your work a GPU can help with at
    all, and what that puts a ceiling on.

    The scripts are in `~/gpu-training/supplementary/`.

!!! clipboard-list "Lesson Objectives"

    - Break a workflow into stages and identify which belong on a GPU
    - Measure what fraction of your runtime a GPU could affect
    - Recognise when a faster GPU cannot help you, no matter how fast

!!! clipboard-question "Questions"

    - Which parts of my work should run on the GPU?
    - My GPU utilisation is low. Should I get a better GPU?

## The ceiling

Suppose 30% of your job's runtime is GPU work and 70% is reading files,
preparing data and writing results. You swap the GPU for one twice as fast.

```
before:  [======== 70% CPU ========][=== 30% GPU ===]     100%
after:   [======== 70% CPU ========][ 15% ]                85%
```

You saved 15% of the runtime. Now swap it for one that is *infinitely* fast:

```
best:    [======== 70% CPU ========]                       70%
```

You saved 30%, and that is the most any GPU can ever do for this job.

**The work that is not on the GPU sets a hard ceiling on what a better GPU can
do for you.** This is Amdahl's law, and the only thing you need from it is the
habit: find out what the fraction is before you go looking for a better card.

## Which stages belong on a GPU

| Belongs on the GPU | Stays on the CPU |
|---|---|
| The same arithmetic over large arrays | Reading and writing files |
| Matrix multiplication, convolution, FFT | Decompressing, parsing, text handling |
| Element-wise operations on big tensors | Decisions and branching |
| Many independent simulations at once | Anything that must happen in order |
| Neural network forward and backward passes | Talking to a database or the network |

The pattern: **large, regular, identical, independent** work belongs on the
GPU. Everything else does not.

## Measure your own stages

```bash
cd ~/gpu-training/supplementary
python3 profile_phases.py
```

The script runs a workload in four stages and reports where the time went:

```
Where the time went
----------------------------------------------
  CPU  1. read input              3.0s   28.5%
  CPU  2. prepare                 0.2s    1.9%
  GPU  3. compute                 4.3s   40.8%
  CPU  4. write output            1.5s   14.2%
                             ----------------
       total                     10.5s  100.0%

The GPU was busy for 41% of this run.
A GPU 2x faster would cut 4.3s to 2.1s, saving 20% of the total runtime.
```

Now run the badly balanced version:

```bash
python3 profile_phases.py --heavy-io
```

```
Where the time went
----------------------------------------------
  CPU  1. read input              6.0s   44.5%
  CPU  2. prepare                 0.2s    1.3%
  GPU  3. compute                 4.3s   31.9%
  CPU  4. write output            3.0s   22.3%
                             ----------------
       total                     13.5s  100.0%

The GPU was busy for 32% of this run.
Most of this job is not on the GPU. Speeding up the part that is cannot
help much - look at the CPU phases first.
```

Same computation. Two thirds of the runtime is now reading and writing, and no
GPU on earth will do anything about it.

## Timing your own code

You do not need any special tools. Put timers around the stages:

```python
import time

t0 = time.time()
data = load_and_prepare(path)
t1 = time.time()
result = model(data)            # the GPU part
t2 = time.time()
save(result, out)
t3 = time.time()

print(f"load    {t1-t0:6.1f}s")
print(f"compute {t2-t1:6.1f}s")
print(f"save    {t3-t2:6.1f}s")
```

Ten lines, once, and you will know more about your job than most people know
about theirs. For non-Python software, the same thing:

```bash
/usr/bin/time -v ./preprocess.sh
/usr/bin/time -v ./simulate.sh
```

!!! warning "Not in this environment"

    The training environment has no GPU, so wall-clock times measured here are
    meaningless as a guide to GPU performance. Do the timing exercise on the
    real cluster with your own code.

    What the exercise here teaches is the **method** and what to do with the
    answer — and those do transfer.

## What to do with the answer

**If the GPU stage dominates (say over 70%)**

The GPU is the bottleneck. This is the one case where a faster or larger GPU is
the right answer. Go to chapters 5 and 6 and choose one properly.

**If reading and writing dominate**

You are limited by storage. Things that help, roughly in order of payoff:

- Read fewer, larger files instead of many small ones. Filesystems hate
  thousands of small reads.
- Stage your data onto fast local storage at the start of the job, rather than
  reading it repeatedly over the network.
- Overlap reading with computing, so the next batch loads while the current one
  is being processed. Most machine-learning frameworks do this for you if you
  switch it on — in PyTorch it is `DataLoader(..., num_workers=N)`.
- Keep intermediate results in memory instead of writing them to disk and
  reading them back.

**If CPU preparation dominates**

- Parallelise it across more cores — chapter 2.
- Do the preparation once and cache the result, if it is the same every run.
  People re-decode the same dataset every epoch for months.
- Consider moving that stage onto the GPU too, if it is arithmetic rather than
  parsing.

!!! dumbbell "Exercise: your own workflow"

    On paper, break your own work into stages and answer, for each:

    | Stage | What it does | CPU or GPU? | Roughly what fraction of runtime? |
    |---|---|---|---|

    Then:

    1. What fraction of your runtime could a GPU possibly affect?
    2. If a GPU twice as fast were free tomorrow, how much would your job speed
       up?
    3. Is there a stage where a day of your time would save more than a better
       GPU would?

    For most real workflows the honest answer to 3 is yes, and it is usually
    the loading stage.

!!! note "Overlapping is often the biggest win available"

    The diagram at the top of this page assumes CPU and GPU take turns. They do
    not have to. If batch N+1 is prepared while batch N is computing, the
    waiting disappears:

    ```
    taking turns:  [prep 1][gpu 1][prep 2][gpu 2][prep 3][gpu 3]
    overlapped:    [prep 1][prep 2][prep 3]
                          [gpu 1][gpu 2][gpu 3]
    ```

    This is what `num_workers` in a PyTorch `DataLoader`, or `prefetch` in a
    TensorFlow dataset, actually does — and it costs one argument.

!!! graduation-cap "Keypoints"

    - The work **not** on the GPU is a hard ceiling on what a better GPU can do.
    - GPUs help with large, regular, identical, independent arithmetic. Nothing
      else.
    - **Time your stages before you ask for better hardware.** Ten lines.
    - If storage dominates, fix the storage. If preparation dominates, add
      cores or cache the result.
    - Overlapping preparation with computation is often the cheapest large win
      available.
