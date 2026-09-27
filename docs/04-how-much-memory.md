# 4. How much memory should I request?

!!! clipboard-list "Lesson Objectives"

    - Know what a GPU job actually uses CPU memory for
    - Work out how much your job needs
    - Recognise a job that was killed for going over what it asked for

!!! clipboard-question "Questions"

    - How much memory should I ask for?
    - My job died without printing an error. What happened?

## What a GPU job needs CPU memory for

It is easy to assume that once the work is on the GPU, the CPU side barely
matters. It still needs room for:

- **Data read from disk**, before it has been prepared.
- **Batches waiting to be handed over.** Recall from
  [chapter 3](03-how-many-cpus.md) that several cores prepare batches at once —
  every batch sitting ready is sitting in CPU memory.
- **The copy made during a transfer.** Moving data to the GPU does not free the
  CPU memory it came from; for a moment it exists in both places.
- **Whatever your program keeps CPU-side** — results being accumulated, logs,
  arrays you have not released.

## How much does my job need?

This is very dependent on your program, what you are wanting to do, etc. The 
best way is to measure the peak amount of memory you needed

1. **Start with a large amount of RAM.** For example 64 GBs of RAM
2. **Run a short 15 minute job.**
3. **Read the peak usage afterwards** (we will see how to do this later). 
4. **Ask for 20–30% above that peak** from then on.

The margin matters. Peak usage varies a little between runs — a slightly larger
input file, a different batch arriving first — so sizing exactly to a single
measured peak leaves you being killed occasionally, for no reason you can see.

!!! note "Do not over-request"

    Asking for 256 GB when you need 4 makes your job much harder to schedule, so
    it waits longer, and holds memory nobody else can use while you have it.

    Over-requesting is not caution — it is just slower.

## What happens when you run out

Going over the memory you asked for does not produce a normal error. **Slurm
kills the job**, so your program never gets the chance to complain — which is
why this one is confusing the first time you meet it.

```
slurmstepd: error: Detected 1 oom_kill event in StepId=1234567.batch.
Some of the step tasks have been OOM Killed.
```

Sometimes that is all you get. The signs to look for:

| What you see | What it means |
|---|---|
| The job stops abruptly, part-way through | Killed rather than crashed |
| No error from your own program | It was not given the chance to raise one |
| `oom_kill event` in the output file | Slurm is telling you directly |
| Exit code `137` | The job was killed (128 + signal 9) |
| `seff` reports memory efficiency near or above 100% | You used everything you asked for |

**Ask for more, then measure again** and settle on a value with some headroom.
If your request is already large, look instead for something you are holding on
to CPU-side that you meant to release, or reduce your core count so that fewer
batches are in flight at once.
!!! graduation-cap "Keypoints"

    - A GPU job still needs real **CPU memory**: for data read from disk, for
      batches waiting to be handed over, and for the copy made during each
      transfer.
    - **CPU memory and cores are linked.** More cores means more batches in
      flight, which means more memory.
    - **There is no formula — measure a short run**, then add 20–30%.
    - Over-requesting delays your own job as well as everyone else's.
    - Running out gets your job **killed**, usually with no error from your
      program. Look for `oom_kill` or exit code `137`.
