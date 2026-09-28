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
      k8s_container: ghcr.io/nesi/training-environment-jupyter-gpu-app:v0.5.1
      repo: https://github.com/nesi/training-environment-jupyter-gpu-app.git
      version: 'v0.5.1'
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
| CPUs | 4 | Do not go below this — chapter 3 needs at least 4 to show the curve |
| Memory | 8 GB | |
| NVIDIA L4 — GPU memory | `200 MiB` | |
| NVIDIA A100 40 GB — GPU memory | `200 MiB` | |
| NVIDIA A100 80 GB — GPU memory | `200 MiB` | |
| NVIDIA H100 NVL — GPU memory | `200 MiB` | |
| NVIDIA RTX PRO 6000 — GPU memory | `200 MiB` | |

There is one control per card, and the session's node presents every card you
leave switched on. That is what makes `--gpus-per-node a100:1` and
`--gpus-per-node l4:1` different requests, so the chapter on choosing a GPU is
something a learner can practise rather than only read. **Not on this node**
leaves a card out, and asking for it is then refused, as on the cluster.

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
nvidia-smi -L                    # five cards: l4, a100_40, a100, h100, pro_6000
sinfo -l                         # the same list, spelled as --gpus-per-node wants
python3 -c "import torch; print(torch.cuda.is_available())"   # True
cd ~/gpu-training && ls          # 06, 07 and supplementary
sbatch 06_tools_for_measuring/test-job.sl
seff <jobid>                     # must include the two GPU lines
profile_plot <jobid>             # writes <jobid>_profile.png
seff 2001001                     # a recorded job: FAILED, 98% of 24 GB
```

If `nvidia-smi -L` shows a single card, or reports 23034MiB rather than
200MiB, the session is running an older image than the branch expects.

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
| **Stage 1 — Writing your submit script** | | Read rather than run: there is no job yet |
| 1. The submit script | 20 min | The annotated skeleton. Most of the audience will know some of this |
| 2. Which GPU | 40 min | The longest chapter. The flow diagram and the memory ladder are the heart of it |
| 3. How many CPUs | 25 min | The two figures do the work here. The hypothesis table repays going slowly |
| 4. How much memory | 20 min | CPU memory, not VRAM. Expect the confusion and name it early |
| **Stage 2 — Measuring your GPU jobs** | | |
| 5. Measuring your GPU jobs | 15 min | Short. Sets up the four questions the tools answer |
| 6. The tools for measuring | 40 min | `test-job.sl` runs 3 minutes; submit it before you explain `seff` |
| **Stage 3 — Putting it all together** | | |
| 7. Putting it all together | 40 min | Three passes over one job. The recorded jobs mean no waiting |
| S1 / S2 | — | Supplementary. Point at them rather than working through |

Roughly three and a half hours. The material assumes most of the audience has
run a Slurm job before; chapter 1 moves quickly and only the GPU lines are
likely to be new.

!!! note "Things worth saying out loud"

    - **At the start:** there is no GPU here, and no timing in this environment
      means anything. Say it once clearly and it will not come up again.
    - **Chapter 2:** the most common question is "so how do I ask for more
      VRAM?" The answer — you cannot, you choose a card — is the point of the
      chapter. The RTX PRO 6000 being both the best fp32 card and nearly the
      worst fp64 card is the thing people remember; spend time on it.
    - **Chapter 6:** submit `test-job.sl` before you explain the tools, so
      there is a finished job to read when you get there.
    - **Chapter 7:** the ten jobs it compares were run in advance. Say so —
      otherwise someone will wonder why their `squeue` is empty.

## Keeping the material in step

The exercises in [`examples/`](https://github.com/nesi/reannz-intro-gpu-workshop/tree/main/examples)
are a copy of `docker/workshop/` in the app repository, which is what actually
ships in the session image. If you change one, change the other, or the page a
learner reads will not match the file in front of them.

## Known limits

The emulator is honest about what it cannot do:

| Taught properly | Not possible here |
|---|---|
| Requesting a GPU and confirming it | Anything about speed |
| Reading `nvidia-smi`, `nvtop`, `seff` | Profiling, occupancy, kernel performance |
| Memory budgeting and OOM recovery | Real fp64 vs fp32 throughput |
| Diagnosing a starved GPU | Multi-GPU scaling, NCCL |
| Structuring a GPU batch job | Custom CUDA extensions, Triton, `torch.compile` |

Chapter 2's precision figures are published specifications shown in a table,
not measurements — the environment cannot demonstrate the speed difference, so
the chapter gives the speed ratios as documentation and leaves the *accuracy*
difference, which is real, to the supplementary material.
