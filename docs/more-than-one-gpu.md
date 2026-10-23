# B4: More than one GPU, and less than one

!!! circle-info "Beyond the basics"

    Not covered in the live workshop.

!!! clipboard-list "Lesson Objectives"

    - Know when a second GPU can help, and how to find out whether it does
    - Know which nodes suit work that passes data between GPUs
    - Know what to do with work too small for a whole GPU

!!! clipboard-question "Questions"

    - Will two GPUs make my job twice as fast?
    - My job uses only a fraction of the card. What should I do?

## More than one GPU

A second GPU helps only if your software splits the work between them. The
common ways it does:

- **Data parallel training.** Each GPU holds a copy of the model and trains on
  different batches, and the GPUs combine what they learned after every step.
  In PyTorch this is `DistributedDataParallel`, started with `torchrun`.
- **Simulation codes that divide the system**, as several molecular dynamics
  codes can.
- **Splitting a model too big for one card** across several. Only software
  written to do this can.

If your software does none of these, the second GPU sits idle for the whole
job — and two cards are still not one bigger card
([Which GPU: will it fit?](gpu-memory.md)).

### Find out whether it helps

Measure, as with everything else: run the same test job on one GPU and on two,
and compare the **throughput** — steps per second, or whatever your program
counts. For example:

| GPUs | Steps per second | Speed-up | Efficiency |
|---|---|---|---|
| 1 | 100 | 1.0× | 100% |
| 2 | 185 | 1.85× | 93% |
| 4 | 300 | 3.0× | 75% |

Efficiency is the speed-up divided by the number of GPUs. Here two GPUs are
well worth it; four are already wasting a quarter of what they hold. A useful
rule: **each GPU you add should earn its place**, and once efficiency falls
much below 75%, the extra GPUs are mostly waiting while somebody else waits
for them.

### How to ask, and where

```bash
#SBATCH --gpus-per-node a100:2
#SBATCH --constraint    a100_80gb
#SBATCH --cpus-per-task 8              # cores for each GPU, times two
```

Two things decide where multi-GPU work should run:

- **How many GPUs a node has.** All the GPUs of one job are on one node
  unless you go further than this page does: up to four L4s or 80 GB A100s,
  three 40 GB A100s, or two H100s or RTX PRO 6000s.
- **How the GPUs talk to each other.** The four GPUs on each 80 GB A100 node
  are linked by NVLink. Every other card, the H100s included, talks over PCIe,
  which is much slower for GPU-to-GPU traffic. Work that exchanges data
  between GPUs every step
  belongs on the 80 GB A100s
  ([Hardware](https://docs.nesi.org.nz/Batch_Computing/Hardware/)).

The per-user limit applies to the total: six GPUs at once
([B3](long-jobs.md#why-is-my-job-pending)).

## Less than one GPU

The opposite problem is more common. If `seff` shows a job using a small
fraction of its card — GPU memory well under 25%, and utilisation low — the
card is too big for it. In order of what to try:

1. **The smallest card.** An L4 is often enough
   ([Which GPU: will it fit?](gpu-memory.md)).
2. **More work in each job.** If several independent pieces of work fit in
   the GPU's memory together, run them on the same GPU at the same time, in
   the background of one job:

    ```bash
    python3 run.py --input part-1 &
    python3 run.py --input part-2 &
    python3 run.py --input part-3 &
    wait
    ```

    Each one is background work the GPU needs, so each needs cores of its own
    ([How many CPUs](how-many-cpus.md)).

3. **Many separate jobs**, if the pieces really are independent: a job array
   (`#SBATCH --array=1-100`) runs one job per piece. Each still holds a whole
   GPU, so make each piece worth one — or combine this with 2.

Some clusters can also split an A100 into several smaller GPUs, called MIG
slices. If your jobs are too small for any card, ask the support team whether
that is available for your work.

!!! graduation-cap "Keypoints"

    - A second GPU helps **only if your software splits the work**. Most does
      not.
    - **Measure throughput on one GPU and on two.** Each GPU you add should
      earn its place.
    - Work that passes data between GPUs every step belongs on the **80 GB
      A100s**, the only GPUs on the cluster linked by NVLink.
    - A job using a fraction of a card should use **a smaller card**, or **do
      more on the one it has**.
