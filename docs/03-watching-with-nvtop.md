# 3. Watching a job with nvtop

!!! clipboard-list "Lesson Objectives"

    - Get onto the node running your job with `svisit`
    - Read the utilisation and memory traces in `nvtop`
    - Recognise the three shapes that tell you something is wrong

!!! clipboard-question "Questions"

    - How do I watch what my job is doing to the GPU *while it runs*?
    - What am I looking for?

## Getting to the job

Your job is not running where you are. It is on a compute node, and the GPU it
is using is on that node, so you have to go there.

```bash
squeue --me          # find a job whose ST is R
svisit <jobid>       # open a terminal inside it
nvtop                # watch
```

`svisit` is a wrapper around `srun --pty --overlap --jobid=...`. It puts you
inside the job's allocation, which is the only way to see the GPU that job was
given. Press `q` to leave `nvtop` and type `exit` to come back.

!!! note "If you leave out the job ID"

    `svisit` on its own finds your most recent running job. That is usually
    what you want:

    ```bash
    svisit
    ```

    Use `svisit -t` to see the command it would run, without running it.

## Try it

Submit a job that runs long enough to be worth watching. It alternates 20
seconds of GPU work with 10 seconds of doing nothing, on purpose, for eight
minutes:

```bash
cd ~/gpu-training/03_watching_with_nvtop
sbatch watch-me.sl
squeue --me
```

Wait until `ST` shows `R`, then:

```bash
svisit <jobid>
nvtop
```

## What you are looking at

```
 Device 0 [NVIDIA L4] PCIe GEN 4@16x  RX: 0 KiB/s TX: 0 KiB/s
 GPU 1980MHz MEM 6251MHz TEMP  48°C FAN N/A% POW  68 / 72 W
 GPU[||||||||||||||||||||||||||||||||||||||||96%] MEM[||||||||   64.0/1024MiB]
    ┌────────────────────────────────────────────────────────────────────┐
100%│              ▄▄▄▄▄▄▄            ▄▄▄▄▄▄▄            ▄▄▄▄▄▄▄         │
    │             █       █          █       █          █       █        │
 50%│             █       █          █       █          █       █        │
    │             █       █          █       █          █       █        │
  0%│▄▄▄▄▄▄▄▄▄▄▄▄▄█       █▄▄▄▄▄▄▄▄▄▄█       █▄▄▄▄▄▄▄▄▄▄█       █▄▄▄▄▄▄▄ │
    └────────────────────────────────────────────────────────────────────┘
    PID USER    DEV  TYPE GPU  GPU MEM  CPU  HOST MEM  Command
  12345 learner   0 Compute  96%  64MiB  99%   240MiB  python3 sawtooth.py
```

Four things, in the order worth checking:

**1. The name and memory.** `Device 0 [NVIDIA L4]` — the card you asked for.

**2. The `GPU[...]` bar and its trace.** Utilisation over time. This is what
`nvidia-smi` cannot show you: the *shape*.

**3. The `MEM[...]` bar.** GPU memory. Watch it go up once, near the start, and
then stay flat while utilisation swings up and down. **Memory shows what you
have reserved; utilisation shows what you are using.** They are unrelated, and
confusing them is one of the most common mistakes in this whole subject.

**4. The process list.** Your process should be there. If the GPU is busy and
your process is *not* listed, you are watching somebody else's work.

!!! dumbbell "Exercise: watch the shape"

    With `nvtop` open on the `watch-me` job, watch for at least a minute.

    1. How long is each busy period? How long is each idle period?
    2. Does the MEM bar move when the GPU goes idle?
    3. What does the POW reading do as utilisation rises and falls?

    ??? "Answer"

        1. 20 seconds busy, 10 seconds idle — exactly the phases the script
           prints as it runs.
        2. No. The memory is allocated once at the start and held until the
           job ends. This is how model weights behave.
        3. Power follows utilisation closely, with a lag. It is the most
           honest single indicator that a GPU is genuinely working: a card
           drawing 68 W of its 72 W limit is doing something.

## The three shapes worth recognising

Once you can read the trace, most GPU problems are visible in it within thirty
seconds.

!!! check-to-slot "Healthy: a solid block near the top"

    ```
    100%│████████████████████████████████████████
      0%│
    ```

    The GPU is being kept fed. If your job looks like this and is still too
    slow, you need a *faster* GPU — which is the one case where upgrading
    hardware is the right answer.

!!! square-xmark "Starved: a sawtooth, or a low flat line"

    ```
    100%│  ▄▄    ▄▄    ▄▄    ▄▄    ▄▄    ▄▄
      0%│▄▄  ▄▄▄▄  ▄▄▄▄  ▄▄▄▄  ▄▄▄▄  ▄▄▄▄  ▄▄▄▄
    ```

    The GPU is waiting for something — usually the CPU preparing the next
    batch, or a slow filesystem. A faster GPU will not help at all; it will
    just wait faster.

    **This is the most common pattern in real jobs**, and chapters 6 and 7 are
    about what to do with it.

!!! square-xmark "Idle: flat at zero, but memory is allocated"

    ```
    100%│
      0%│▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄     MEM[|||||||  18.9/24.0GB]
    ```

    Something has the GPU reserved and is not using it. Common causes: the job
    has finished its GPU phase and is now writing output; the software fell
    back to the CPU but still initialised CUDA; or a crashed process left its
    memory allocated.

    Memory in use with no utilisation is never a good sign.

!!! note "Watching without nvtop"

    If you want a rough trace in a log file rather than an interactive display,
    you can sample from inside the job script itself:

    ```bash
    nvidia-smi --query-gpu=utilization.gpu,memory.used \
               --format=csv --loop=5 > gpu-trace.csv &
    ```

    That writes a reading every 5 seconds for the life of the job. It is much
    less pleasant to read than `nvtop`, but it works when nobody is watching —
    for example in an overnight run.

!!! warning "Do not time anything in this environment"

    The training environment has no GPU. The utilisation, memory, power and
    temperature you see are all consistent and behave correctly, but the
    arithmetic runs on a CPU.

    Reading the traces is the skill, and it transfers exactly. Comparing how
    long two things took does not transfer at all.

!!! graduation-cap "Keypoints"

    - `squeue --me` → `svisit <jobid>` → `nvtop` is the sequence. Learn it.
    - `nvtop` shows utilisation **over time**, which is what a single
      `nvidia-smi` cannot.
    - **Memory is what you reserved. Utilisation is what you are using.** A
      full memory bar at 0% utilisation means nothing is happening.
    - A solid high trace means you need a faster GPU. A sawtooth means you need
      to fix what is feeding it.
    - Check your own process is in the process list.
