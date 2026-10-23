# 9. Running interactive sessions with GPUs

!!! clipboard-list "Lesson Objectives"

    - Know when an interactive session is the right tool, and when a batch job
      is
    - Hold a GPU with a job that waits, and work inside it with `svisit`
    - Use the session to debug a GPU job: check what you have, then watch it
      fail
    - Give the GPU back as soon as you are finished

!!! clipboard-question "Questions"

    - How do I try things on a GPU without queueing a job for every attempt?
    - How do I get a terminal on a node with a GPU?
    - Why does it matter how long an interactive session lasts?

Everything so far has been batch jobs: write a script, submit it, wait, read
what it did. That is the right way to run real work, and the only way to
measure it. It is a slow way to find out why something does not work. Every
attempt at a fix is another trip through the queue, and all that comes back is
the last few lines of an output file.

An **interactive session** turns that round. You hold a GPU and work on it from
a terminal: run something, watch what happens, change it and run it again,
seconds apart rather than a queue apart.

## Batch or interactive?

| | Batch job | Interactive session |
|---|---|---|
| What you get back | An output file, afterwards | A terminal on the GPU's node, now |
| Each attempt costs | A trip through the queue | Seconds |
| The GPU is working | While your program runs | Only while you have something running |
| Use it for | Real work, and measuring it | Checking, trying things, debugging |

**An interactive session is for finding out *whether* something works. A batch
job is for running it, and for measuring *how well* it works** — which is what
the test job and the tools in [Measuring a GPU job](measuring.md) are for.

!!! warning "The GPU is yours for the whole session"

    From the moment the session starts until it ends, the GPU is held in your
    name: while your program runs, and just as much while you read its output,
    edit a file or go and make a coffee. Nobody else can use it, and every
    minute of it counts against your project.

    That makes an interactive session the least efficient way there is to use
    a GPU. For debugging, which is short, that is a fair price. For anything
    else it is the opposite of [what this workshop is for](index.md) — so keep
    sessions short, and end them the moment you are done.

## A job that waits

The GPUs on Mahuika are on compute nodes, and the only way onto one is through
a job. So an interactive session starts as an ordinary batch job — one whose
only command is to wait:

```bash
#!/bin/bash -e
#SBATCH --job-name      hold-gpu
#SBATCH --account       nesi99991
#SBATCH --time          00:15:00    (1)
#SBATCH --qos           debug       (2)
#SBATCH --gpus-per-node l4:1        (3)
#SBATCH --cpus-per-task 2
#SBATCH --mem           4GB
#SBATCH --output        hold-gpu-%j.out

sleep infinity                      # (4)!
```

1. **How long you may hold the GPU.** The session ends when this runs out,
   finished or not. Ask for long enough to try what you came to try, and no
   longer — you can always submit another.
2. **Start now.** A session is only useful if you are there when it starts, and
   the [debug QoS](https://docs.nesi.org.nz/Batch_Computing/Debug_QoS/) usually
   starts it within minutes. It allows one debug job at a time, and its rules
   say not to keep an interactive session open while you are not using it —
   especially one holding a GPU.
3. **The card to debug on.** Ask for the same type your real job will use, so
   that what you find out applies to it.
4. **Wait.** `sleep` does nothing and uses no CPU. It keeps the job, and its
   GPU, alive until you cancel it or the time limit ends it.

The job itself does no work. Everything happens in terminals you open inside it
with `svisit` — the command you used in
[Measuring a GPU job](measuring.md) to watch a running job with `nvtop`:

| Step | Command | What it does |
|---|---|---|
| 1 | `sbatch hold-gpu.sl` | Asks for the GPU |
| 2 | `squeue --me` | Shows when it has started: `ST` is `R` |
| 3 | `svisit <JobID>` | Opens a terminal inside the job, with its GPU |
| 4 | *your commands* | Run, check and debug things on the GPU |
| 5 | `exit` | Leaves that terminal. **The job carries on** |
| 6 | `scancel <JobID>` | Ends the job, and gives the GPU back |

`svisit` the same job as often as you like, from as many terminals as you
like: run your program in one, and watch it with `nvtop` in another.

!!! note "Why not `srun --pty bash`?"

    The [cluster's
    documentation](https://docs.nesi.org.nz/Interactive_Computing/Slurm_Interactive_Sessions/)
    also describes a one-line interactive session:

    ```bash
    srun --gpus-per-node l4:1 --cpus-per-task 2 --mem 4GB --time 00:15:00 --pty bash
    ```

    That asks for the GPU and puts you inside the job in one step, and it
    works. The difference is what ties the job to you:

    | | `srun --pty bash` | A job that waits |
    |---|---|---|
    | While it queues | Your terminal waits with it | Your terminal is free |
    | When you `exit` | The job ends, and the GPU is freed | You leave; the job carries on |
    | If your connection drops | The job ends, with everything running in it | Nothing happens. `svisit` back in |

    A laptop going to sleep, a dropped VPN or a closed browser tab is enough to
    end an `srun` session, unless you started it inside `tmux`. A job that
    waits does not notice. The price is that it does not notice you leaving
    either: **`exit` is not `scancel`.**

## Getting a session

The files for this chapter are in `~/gpu-training/interactive`, and
[on GitHub](https://github.com/nesi/reannz-intro-gpu-workshop/tree/main/examples/interactive){: target="_blank" rel="noopener" }.

!!! dumbbell "Exercise 1: hold a GPU and step inside it"

    **Look first, from where you are now.**

    ```bash
    cd ~/gpu-training/interactive
    echo "CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES}"
    ```

    **Ask for a GPU, and wait for the job to start.**

    ```bash
    cat hold-gpu.sl
    sbatch hold-gpu.sl
    squeue --me
    ```

    **Step inside, and look again** — this time also asking the question that
    matters most, whether your software can see the card:

    ```bash
    svisit <JobID>
    echo "CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES}"
    nvidia-smi -L
    module load PyTorch/2.13.0-foss-2026-Python-3.14.4-CUDA-13.2.1
    python3 -c "import torch; print(torch.cuda.is_available())"
    ```

    Stay inside the job for the next exercise.

    ??? "What you should see"

        **Outside the job**, `CUDA_VISIBLE_DEVICES` prints nothing: you are not
        inside a job, so Slurm has given you no GPU.

        **Inside it**, `CUDA_VISIBLE_DEVICES=0`, `nvidia-smi -L` lists a single
        card, the L4 your job asked for, and PyTorch prints `True`. That is
        what being inside a job means: **you see the GPU it was given, and
        nothing else.**

        If `squeue` shows the job as `PD`, it is still waiting for an L4. A
        small debug job usually starts within a few minutes.

## Debugging in the session

Two jobs died overnight, and both left the same error at the bottom of their
output files:

```
torch.OutOfMemoryError: CUDA out of memory.
```

The same error is not always the same problem. The usual answer to running out
of GPU memory is the next card up the ladder from
[Which GPU: will it fit?](gpu-memory.md),
but that only helps if the work is too big for the card. If the job is holding
on to memory it has finished with — **a leak** — a bigger card just takes
longer to fill.

An output file tells you where a job died. A session lets you watch it happen,
as many times as you like, seconds apart.

!!! dumbbell "Exercise 2: two crashes, watched live"

    **Open a second terminal** on Mahuika, beside the first so that you can
    see both. In it, visit the same job, straight into `nvtop`:

    ```bash
    svisit <JobID> nvtop
    ```

    `nvtop` shows your job's card, the L4.

    **In the first terminal**, still inside the job, run the first crash and
    watch the GPU memory graph:

    ```bash
    python3 crash_one.py
    ```

    **Then the second:**

    ```bash
    python3 crash_two.py
    ```

    For each one, note how far it got before it died, and what GPU memory did
    on the way:

    | | `crash_one.py` | `crash_two.py` |
    |---|---|---|
    | How far it got | | |
    | What GPU memory did | | |
    | Too big for the card, or a leak? | | |

    ??? "What you should find"

        | | `crash_one.py` | `crash_two.py` |
        |---|---|---|
        | How far it got | 17 steps of work, then died on step 18 | Died loading the model, at layer 9 of 10, before doing any work |
        | What GPU memory did | Climbed with every step, until it hit the top | Filled up while the model loaded |
        | Too big for the card, or a leak? | **A leak** | **Too big** |

        **`crash_two.py` is too big for the card.** Its model has ten layers
        and the card holds eight, so it was never going to fit, and the answer is the next card up
        the ladder.

        **`crash_one.py` is a leak.** Every step does the same work, and should
        need no more memory than the one before. Instead it keeps every batch
        it has finished with, so memory climbs until there is none left. A
        bigger card would not save it — a leak fills any card in the end; a
        bigger one only takes longer. The fix is in the program, for whoever
        wrote it: you, or its developers.

        Now compare the last line each one printed:

        | | Tried to allocate | Already allocated | Free |
        |---|---|---|---|
        | `crash_one.py` | 1.1 GiB | 21.4 GiB | 620 MiB |
        | `crash_two.py` | 2.7 GiB | 21.6 GiB | 389 MiB |

        Almost identical. Both died asking for a little more, on a card that
        was already full. **The error tells you where a job died, not how it
        got there** — watching it is what told the two apart.

!!! note "A short test would have passed"

    Run the leak again, as a five-step test:

    ```bash
    python3 crash_one.py --steps 5
    ```

    It finishes without complaint, and GPU memory climbs the whole time. A leak
    passes a short test and kills the long run hours later. **Memory that
    climbs while the work stays the same is the warning** — in `nvtop` here,
    or in the GPU memory panel of `profile_plot` for a batch job
    ([Measuring a GPU job](measuring.md)).

## Giving the GPU back

When it works — or when you know why it does not — stop. Put what you learned
into a batch script, like the test script from
[Measuring a GPU job](measuring.md), and end the session.

!!! dumbbell "Exercise 3: give the GPU back"

    Press `q` in the second terminal to quit `nvtop`. In the first, leave the
    job, then end it:

    ```bash
    exit
    squeue --me
    scancel <JobID>
    squeue --me
    seff <JobID>
    ```

    ??? "What you should see"

        After `exit`, `squeue --me` still shows the job running: leaving it
        does not end it. Only `scancel` does, and the second `squeue --me` is
        empty.

        `seff` reports the job as `CANCELLED`, with GPU lines something like
        these:

        ```
        Peak GPU Utilisation:   0%
        Peak GPU Memory Util:  98%  23.60 GB of 24 GB
        ```

        The memory line is `crash_two.py` filling the card. The utilisation
        line is the whole session, and it is close to zero: **for almost all
        the time you held the GPU, it did nothing** — you were reading, typing
        and thinking. That is normal for debugging, and it is why a session
        should last minutes, not hours.

        Had you forgotten to `scancel`, the job would have held an idle L4
        until its fifteen minutes ran out, and ended as `TIMEOUT`.

!!! graduation-cap "Keypoints"

    - An interactive session is for finding out **whether** something works.
      Running it, and measuring **how well**, is what batch jobs are for.
    - **Hold a GPU with a job that waits** — a normal `#SBATCH` header and
      `sleep infinity` — then `svisit <JobID>` for a terminal inside it.
    - `svisit` the job from as many terminals as you like: run your program in
      one, and watch it with `nvtop` in another.
    - **The GPU is yours for the whole session, busy or not.** Keep `--time`
      short, and use `--qos debug` so that it starts while you are there.
    - **`exit` leaves the job; `scancel` ends it.** Until you `scancel`, the
      card sits idle in your name.
    - The same out-of-memory error can be two problems. **Too big** for the
      card: the next card up. Memory **climbing step after step**: a leak,
      which no card will fix.
