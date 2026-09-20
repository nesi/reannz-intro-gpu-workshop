# 5. RAM and VRAM

!!! clipboard-list "Lesson Objectives"

    - State the difference between system RAM and GPU memory
    - Work out, on paper, how much GPU memory your work needs
    - Read a CUDA out-of-memory error and choose the right fix
    - Decide how much `--mem` to request

!!! clipboard-question "Questions"

    - My job says "out of memory" — do I ask for more `--mem`?
    - How do I know which GPU is big enough?

## Two pools

Both are called memory. Both are measured in gigabytes. They are completely
separate and you get them in completely different ways.

| | **RAM** | **VRAM** |
|---|---|---|
| Where | Attached to the CPU | On the GPU board itself |
| How you get it | `#SBATCH --mem 8GB` | Comes with the GPU you chose |
| Can you ask for a specific amount? | Yes | **No** |
| Running out | Slurm kills your job | Your program raises an out-of-memory error |
| Shown by | `seff`'s `Peak Mem Utilisation` | `nvidia-smi`, `nvtop`, `seff`'s `Peak GPU Memory Util` |

!!! warning "The consequence that matters"

    * If your program dies with **"CUDA out of memory"**, increasing `--mem`
      will not help. You need a GPU with more VRAM, or you need to use less.
    * If Slurm kills your job for **exceeding its memory limit**, a bigger GPU
      will not help. You need more `--mem`.

    Getting these the wrong way round wastes a remarkable amount of time,
    because in both cases the fix you reach for *looks* like the right one.

## See it happen

```bash
cd ~/gpu-training/05_ram_and_vram
python3 two_pools.py
```

```
                                      RAM (MB)   VRAM (MB)
----------------------------------------------------------
at the start                               218           1
after 256 MB in RAM                        478           1
   ^ RAM went up. VRAM did not move: the GPU cannot see this data.

after moving it to the GPU                 478         257
   ^ VRAM went up. The data now exists in the GPU's own memory.

after freeing the RAM copy                 478         257
   ^ VRAM is unchanged. Freeing RAM does nothing for VRAM, and the
     reverse is also true. They are not connected.
```

Two things to take from this. First, allocating 256 MB in RAM moved the RAM
counter and nothing else. Second — and this surprises people — moving data to
the GPU **adds** to VRAM without removing anything from RAM. A transfer is a
copy, so for a moment the data exists twice.

## How much VRAM do you need?

You can work this out before you queue anything. Every number you hold on the
GPU costs bytes:

| Type | Also called | Bytes each |
|---|---|---|
| `float64` | double precision | 8 |
| `float32` | single precision | 4 |
| `float16` / `bfloat16` | half precision | 2 |

Multiply by how many numbers you hold at once.

**For neural networks**, the rule of thumb is about **4× the size of the
model**, because you hold the weights, their gradients, and two optimiser
states for each weight. Then add the activations, which scale with batch size.

```bash
python3 how_much_vram.py
```

```
  parameters   fp32 weights   fp32 training   fp16 weights
  ----------------------------------------------------------
          1M           0.00G           0.01G          0.00G
         10M           0.04G           0.15G          0.02G
        100M           0.37G           1.49G          0.19G
          1B           3.73G          14.90G          1.86G
          7B          26.08G         104.31G         13.04G
         70B         260.77G        1043.08G        130.39G
```

Read the row for your model and pick the smallest GPU it fits in. A 7B model
needs about 26 GB just for weights and optimiser state in fp32 — too big for an
L4's 24 GB, comfortable on an A100's 80 GB.

**For simulations**, the size is usually a straightforward function of the grid
or system size, and the documentation often states it directly.

**If you genuinely do not know**, guess high, run a short job with
`--qos debug`, and read `Peak GPU Memory Util` from `seff`. Then request
properly next time. That measurement takes fifteen minutes and settles the
question permanently.

## Running out

The second half of the script fills the card until it refuses:

```
  allocated    960 MB  (0.94 GB)

  Out of memory. This is the error, in full:

    CUDA out of memory. Tried to allocate 64.00 MiB (GPU 0; 1000.00 MiB total
    capacity; 960.00 MiB already allocated; 40.00 MiB free).
```

Learn to read it:

| Phrase | Means |
|---|---|
| `Tried to allocate` | The size of the allocation that failed — often small |
| `total capacity` | What the card has |
| `already allocated` | What **your process** was holding |
| `free` | What was left |

!!! note "The failed allocation is usually small"

    People see "Tried to allocate 64 MiB" and conclude something strange has
    happened, because 64 MiB is nothing. But the card was already 96% full;
    64 MiB was simply the straw that broke it.

    The number that matters is `already allocated`, not `tried to allocate`.

### What to do about it, in order

1. **Reduce the batch size.** This is the whole fix most of the time. Halving
   the batch roughly halves the activation memory and usually costs very little
   otherwise. Try this first, always.
2. **Use a lower precision**, if your work tolerates it. fp32 → fp16 halves
   memory. Chapter 8 is about when that is safe.
3. **Check for a memory leak.** If usage climbs steadily across a long run
   rather than settling, you are holding on to something you meant to discard.
4. **Ask for a GPU with more VRAM.** Real, but it is the last resort: bigger
   cards are scarcer and you will wait longer for one.

!!! warning "Do not ask for two GPUs to get more memory"

    Two 24 GB cards are not a 48 GB card. Unless your software explicitly
    supports splitting a model across devices — and most does not — a second
    GPU gives you a second, separate 24 GB that your job cannot reach.

## How much `--mem` should you request?

Ordinary RAM, and the answer is: measure it.

1. Start with something generous, like `--mem 8GB`.
2. Run a short job.
3. Read `Peak Mem Utilisation` from `seff`.
4. Request about 20–30% above the peak in future.

!!! note "Do not over-request either"

    Asking for 64 GB when you need 4 GB makes your job much harder to schedule,
    so it waits longer, and it stops that memory being used by anyone else
    while you hold it. Over-requesting is not free and it is not cautious — it
    is just slower.

!!! dumbbell "Exercise: both pools, in a job"

    ```bash
    sbatch vram.sl
    ```

    This job requests `--mem 4GB` and one L4. When it has finished:

    1. Read the output file.
    2. Run `seff` on it and compare `Peak Mem Utilisation` with
       `Peak GPU Memory Util`.
    3. Was this job's `--mem` request well sized? Was the GPU well sized?

    ??? "Answer"

        `Peak Mem Utilisation` will be low — a few hundred MB of the 4 GB
        requested — so `--mem 1GB` would have been plenty.

        `Peak GPU Memory Util` will be near 100%, because the second script
        deliberately fills the card. In a real job that would be a warning:
        you are one small increase in problem size away from failing, and you
        should either reduce the batch size or move to a larger card.

!!! graduation-cap "Keypoints"

    - **RAM and VRAM are separate pools.** `--mem` gets you the first. Your
      choice of GPU gets you the second.
    - "CUDA out of memory" is never fixed by `--mem`.
    - Estimate VRAM as bytes-per-number × numbers held; for training, about 4×
      the model size, plus activations.
    - Read `already allocated` in an OOM message, not `tried to allocate`.
    - Fix OOM by reducing batch size first. Ask for a bigger card last.
    - Size `--mem` from `seff`'s `Peak Mem Utilisation`, plus a margin.
