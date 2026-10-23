# B3: Long jobs: time limits, checkpoints and the queue

!!! circle-info "Beyond the basics"

    Not covered in the live workshop. Read it before you queue a GPU job that
    will run for more than a day.

!!! clipboard-list "Lesson Objectives"

    - Choose a time limit from a measurement, not a guess
    - Know why a long GPU job should checkpoint, and what to save
    - Read why a job is pending, and know what makes one start sooner

!!! clipboard-question "Questions"

    - How long should I ask for?
    - What happens when a job reaches its time limit?
    - My job has been pending for hours. Why?

## How long to ask for

[Putting it all together](putting-it-together.md) set `--time` from the test
job's step count: its rate, times the steps the real run needs, plus 20–30%.
That margin matters, because of what happens at the limit:

- **Slurm stops the job when its time runs out**, finished or not. `seff`
  reports it as `TIMEOUT`.
- Everything since the job last saved its state is lost. For a three-day job
  that saves nothing until the end, that is three GPU-days.
- No single job can run for longer than **21 days**.

Asking for far too long is not free either. A longer job is harder for the
scheduler to fit in, so it waits longer to start (more on that below).

## Checkpointing

A **checkpoint** is the job saving enough of its state to carry on from that
point later. The cluster's advice is to checkpoint any job that runs longer
than a day ([Job checkpointing](https://docs.nesi.org.nz/Batch_Computing/Job_Checkpointing/)).

**What to save** is everything needed to carry on, and nothing else:

| Kind of work | What a checkpoint holds |
|---|---|
| Training a model | The model's weights, the optimiser's state, and the step count |
| A simulation | The program's own restart files. Most simulation codes write them, and can be told to start from one |

**How often** is a trade: often enough that losing the time since the last one
would not hurt, and rarely enough that writing it does not slow the job down.
Every half hour to every few hours suits most jobs.

For PyTorch, the pattern is to save as you go, and to start from the last save
if there is one:

```python
import os
import torch

start = 0
if os.path.exists("checkpoint.pt"):
    saved = torch.load("checkpoint.pt")
    model.load_state_dict(saved["model"])
    optimiser.load_state_dict(saved["optimiser"])
    start = saved["step"] + 1

for step in range(start, total_steps):
    train_one_step(model, optimiser)
    if step % 1000 == 0:
        torch.save({"model": model.state_dict(),
                    "optimiser": optimiser.state_dict(),
                    "step": step}, "checkpoint.pt")
```

### Run it as a chain of shorter jobs

Once a job can pick up where it left off, it no longer has to be one long job.
Split it into a chain, each link starting when the last one finishes:

```bash
sbatch train.sl                                 # Submitted batch job 1234567
sbatch --dependency=afterok:1234567 train.sl    # starts when that one succeeds
```

Shorter jobs start sooner, a failure costs you one link rather than the whole
run, and a chain can run for longer than 21 days.

## Why is my job pending?

`squeue --me` gives the reason in its last column:

| Reason | Means | What to do |
|---|---|---|
| `Priority` | Other jobs are ahead of yours | Wait. A smaller, shorter request starts sooner |
| `Resources` | Your job is next, and is waiting for the cards, cores or memory it asked for to come free | Wait, or ask for a card there are more of |
| `QOSMaxGRESPerUser` | You already hold as many GPUs as one person may at a time | Wait for one of your own jobs to finish |
| `Dependency` | It is waiting for another job, as above | Nothing; that is what you asked for |

On the cluster, `squeue --me --start` shows when Slurm expects a pending job to
start.

Each user may hold **6 GPUs at once**, and **14 GPU-days' worth of running
jobs** — whichever comes first. The
[Job limits](https://docs.nesi.org.nz/Batch_Computing/Job_Limits/) page has the
full list.

### What makes a GPU job start sooner

- **The smallest card that fits.** There are more of them, and fewer people
  want them ([Which GPU: will it fit?](gpu-memory.md)).
- **An honest `--time`.** The scheduler fills gaps in the queue with jobs short
  enough to finish before the gap closes. A job that asks for a week cannot use
  a gap of a day.
- **Only what you use.** Spare cores and memory make a job harder to place, for
  no benefit.

!!! dumbbell "Optional exercise: watch a job wait"

    The training node has one L4, so two jobs that both want it cannot run at
    once. The two scripts are [`hold-gpu.sl`](https://github.com/nesi/reannz-intro-gpu-workshop/blob/main/examples/interactive/hold-gpu.sl){: target="_blank" rel="noopener" } and
    [`hello-gpu.sl`](https://github.com/nesi/reannz-intro-gpu-workshop/blob/main/examples/first-job/hello-gpu.sl){: target="_blank" rel="noopener" }:

    ```bash
    cd ~/gpu-training/interactive
    sbatch hold-gpu.sl
    cd ../first-job
    sbatch hello-gpu.sl
    squeue --me
    ```

    ??? "What you should see"

        ```
                     JOBID PARTITION     NAME     USER ST       TIME NODES NODELIST(REASON)
                      1007       gpu hold-gpu     user  R    0:00:04     1 gpunode001
                      1008       gpu hello-gp     user PD    0:00:00     1 (Resources)
        ```

        The second job is pending with `Resources`: it is next in line, and
        waiting for the L4. `scancel` the holding job, and it starts at once.

!!! graduation-cap "Keypoints"

    - Set `--time` from the **test job's step count**, plus 20–30%. At the
      limit the job is stopped, finished or not.
    - **Checkpoint any job longer than a day**: save the state, and start from
      the last save if there is one.
    - A checkpointed job can run as a **chain of shorter jobs**, with
      `--dependency=afterok`.
    - **`squeue --me`** gives the reason a job is waiting. Smaller, shorter,
      honest requests start sooner.
