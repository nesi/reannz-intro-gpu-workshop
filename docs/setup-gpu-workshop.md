# Setup (for trainers)

How to stand up the environment this workshop runs in, and what to tell
learners about it.

## The environment

The workshop runs on the [REANNZ training
environment](https://github.com/nesi/training-environment), using the
[GPU JupyterLab
app](https://github.com/nesi/training-environment-jupyter-gpu-app).

**The training infrastructure has no GPUs.** The app emulates one, well enough
that `nvidia-smi`, `nvtop`, `seff`, `sbatch` and PyTorch's CUDA API all behave
as they do on the cluster. Utilisation, device memory, job accounting and
out-of-memory errors are real; the arithmetic runs on the CPU.

## Deploying

1. Deploy the training environment from the `gpu` branch, following the
   [deployment
   tutorial](https://nesi.github.io/training-environment/tutorials/deployment-on-nesi/).
2. The `gpu` branch is already configured with the GPU app enabled and
   pre-pulled. Check that both pins in `vars/ondemand-config.yml` name the same
   release:

    ```yaml
    gpu:
      k8s_container: ghcr.io/nesi/training-environment-jupyter-gpu-app:v0.5.3
      repo: https://github.com/nesi/training-environment-jupyter-gpu-app.git
      version: 'v0.5.3'
      enabled: true
      pre_pull: true
    ```

    `version` decides which `submit.yml.erb` a session uses, and therefore
    which image actually runs. `k8s_container` only tells the pod pre-puller
    what to cache. **They must match.**

3. Sizing: one trainer and one training user per session, 4 CPUs and 8 GB per
   session by default.

### Session options

| Option | Default | Notes |
|---|---|---|
| CPUs | 4 | Do not go below this: with fewer, the emulated GPU utilisation reads high for every job |
| Memory | 8 GB | |
| NVIDIA L4 — GPU memory | `200 MiB` | |
| NVIDIA A100 40 GB — GPU memory | `200 MiB` | |
| NVIDIA A100 80 GB — GPU memory | `200 MiB` | |
| NVIDIA H100 NVL — GPU memory | `200 MiB` | |
| NVIDIA RTX PRO 6000 — GPU memory | `200 MiB` | |

There is one control per card, and the session's node presents every card you
leave switched on. That is what makes `--gpus-per-node a100:1` and
`--gpus-per-node l4:1` different requests, so choosing a GPU is something a
learner can practise rather than only read. **Not on this node** leaves a card
out, and asking for it is then refused, as on the cluster.

!!! warning "Keep the GPU memory at 200 MB"

    Every exercise is sized to fit inside it, and the out-of-memory
    demonstrations depend on the cards being small. Raising one to its real
    size would mean a learner needs to allocate 23 GB of host RAM to trigger an
    OOM, which is not affordable per session.

    Emulated GPU memory is accounted rather than reserved, so five cards cost
    nothing until something is put on them — but a card that is filled does
    cost that much of the session's 8 GB.

## Checking a deployment

In a session terminal:

```bash
nvidia-smi -L                    # five cards: an L4, two A100s, an H100, an RTX PRO 6000
sinfo -l                         # gpu:a100:2, and the a100_40gb and a100_80gb features
python3 -c "import torch; print(torch.cuda.is_available())"   # True
cd ~/gpu-training && ls          # first-job, gpu-memory, measuring, interactive, ...
cd measuring && sbatch test-job.sl
seff <jobid>                     # must include the two GPU lines
profile_plot <jobid>             # writes <jobid>_profile.png
seff 2001001                     # a recorded job: FAILED, 98% of 24 GB
```

If `nvidia-smi -L` shows a single card, or reports 23034MiB rather than
200MiB, the session is running an older image than the branch expects. If
`ls` shows `06_tools_for_measuring` and `07_putting_it_together` instead of
topic-named folders, or `sinfo -l` lists `gpu:a100_40:1`, the image predates
this version of the workshop.

## Trying it without deploying

The app repository has a local runner. Docker is the only requirement:

```bash
git clone https://github.com/nesi/training-environment-jupyter-gpu-app.git
cd training-environment-jupyter-gpu-app
./run-local.sh
```

It starts the same image the cluster runs and prints a JupyterLab URL. Useful
for rehearsing, and for checking an exercise before a session. It does not
reproduce the Open OnDemand wrapper — no login, no scheduler outside the
container.

```bash
./run-local.sh --fleet 'l4,a100:full'   # an L4 and a full-size A100
./run-local.sh --shell                   # a terminal instead of JupyterLab
```

## Timing

| Chapter | Time | Notes |
|---|---|---|
| **Stage 1 — Getting started with GPUs** | | |
| 1. Introduction | 10 min | Brisk. The point that matters: the software has to support a GPU |
| 2. Your first GPU job | 15 min | `hello-gpu.sl` finishes in seconds. Most of the audience will know the Slurm lines |
| 3. Is it really using the GPU? | 20 min | The edit-and-resubmit loop is the exercise; keep it moving |
| **Stage 2 — Asking for the right resources** | | |
| 4. Which GPU: precision | 20 min | Skip the two optional exercises if time is short |
| 5. Which GPU: will it fit? | 25 min | `vram.sl` takes seconds. The flow diagram is the heart of it |
| 6. How many CPUs | 25 min | The three figures do the work here. The hypothesis table repays going slowly; the optional scan runs in twenty seconds |
| 7. How much CPU memory | 15 min | CPU memory, not VRAM. Expect the confusion and name it early |
| **Stage 3 — Measuring your GPU jobs** | | |
| 8. Measuring a GPU job | 35 min | `test-job.sl` runs three minutes; submit it before you explain `seff` |
| **Stage 4 — Running interactive jobs** | | |
| 9. Running interactive sessions with GPUs | 25 min | Two terminals side by side. Explain the page before anyone submits `hold-gpu.sl` |
| **Stage 5 — Putting it all together** | | |
| 10. Putting it all together | 35 min | Three passes over one job. The recorded jobs mean no waiting |
| Summary and checklist | 5 min | |
| **Beyond the basics** | — | Not taught live. Point at B1–B4 at the end, for when learners set up their own work |

About three hours fifty minutes, which leaves a short break in a four-hour
session. If you are running late, the optional exercises in chapters 4 and 6, and the
second crash in chapter 9, are the ones to drop. The material assumes most of
the audience has run a Slurm job before; chapter 2 moves quickly and only the
GPU lines are likely to be new.

!!! note "Things worth saying out loud"

    - **At the start:** there is no GPU here, and no timing in this environment
      means anything. Say it once clearly and it will not come up again.
    - **Chapter 3:** a job that forgot its GPU usually *completes*. The
      `forgot-the-gpu.sl` job ends as `FAILED` only because `nvidia-smi` is its
      last command — say so, or someone will conclude that Slurm catches the
      mistake.
    - **Chapters 4 and 5:** the most common question is "so how do I ask for
      more VRAM?" The answer — you cannot, you choose a card — is the point.
      The RTX PRO 6000 being both the best fp32 card and nearly the worst fp64
      card is the thing people remember; spend time on it.
    - **Chapter 8:** submit `test-job.sl` before you explain the tools, so
      there is a finished job to read when you get there.
    - **Chapter 9:** `hold-gpu.sl` has fifteen minutes, and they start when
      the job does, not when the learner gets to it — which is the chapter's
      point, made the hard way if you talk for too long after submitting.
      `exit` does not end the job: before moving on, have everyone run
      `squeue --me` and `scancel` anything still holding the L4.
    - **Chapter 10:** the ten jobs it compares were run in advance. Say so —
      otherwise someone will wonder why their `squeue` is empty.

## Keeping the material in step

The exercises in [`examples/`](https://github.com/nesi/reannz-intro-gpu-workshop/tree/main/examples){: target="_blank" rel="noopener" }
are a copy of `docker/workshop/` in the app repository, which is what actually
ships in the session image. If you change one, change the other, or the page a
learner reads will not match the file in front of them.

The folders are named by topic rather than by chapter number, so that
reordering the chapters does not mean renaming them — and releasing a new
image to match.

## Known limits

The emulator is honest about what it cannot do:

| Taught properly | Not possible here |
|---|---|
| Requesting a GPU by type and `--constraint`, and confirming it | Anything about speed |
| Reading `nvidia-smi`, `nvtop`, `seff` | Profiling, occupancy, kernel performance |
| Memory budgeting and OOM recovery | Real fp64 vs fp32 throughput |
| Diagnosing a starved GPU | Multi-GPU scaling, NCCL |
| Structuring a GPU batch job | Custom CUDA extensions, Triton, `torch.compile` |
| Holding a GPU with a job that waits, and `svisit` | `srun --pty`, `salloc` and `squeue --start` |

The interactive sessions chapter differs from the cluster in three small ways.
A terminal outside any job can see every card, since the session is a single
node (the chapter says so). A shell opened with `svisit` is not ended when its
job is, so a learner who runs `scancel` from inside one stays in it, still able
to use the card. And `seff` counts only the job's own script against its CPU
and memory lines, not what a learner ran through `svisit`, so those read near
zero; the GPU lines, which the chapter is about, are measured from the card and
include everything.

If a learner asks: `tensor.device` reports `cpu` here, because the emulator
keeps tensors in host memory. Nothing in the workshop relies on it.

The precision chapter's speed figures are published specifications shown in a
table, not measurements — the environment cannot demonstrate the speed
difference. The *accuracy* difference is real, and is what the chapter's
optional `accuracy.py` exercise shows.
