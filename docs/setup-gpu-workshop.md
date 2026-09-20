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
      k8s_container: ghcr.io/nesi/training-environment-jupyter-gpu-app:v0.3.0
      repo: https://github.com/nesi/training-environment-jupyter-gpu-app.git
      version: 'v0.3.0'
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
| CPUs | 4 | Do not go below this — chapter 6 needs at least 4 to show the curve |
| Memory | 8 GB | |
| GPU model | `l4` | Also `a100`, `h100`, `rtxpro6000` |
| GPU VRAM | `1GiB` | Keep this. It makes chapter 5 take seconds instead of filling real RAM |
| GPU count | 1 | |

!!! warning "Keep the VRAM at 1 GB"

    Every exercise is sized to fit inside 1 GB, and chapter 5's out-of-memory
    demonstration depends on the card being small. Raising it to the card's
    real size would mean a learner needs to allocate 23 GB of host RAM to
    trigger an OOM, which is not affordable per session.

## Checking a deployment

In a session terminal:

```bash
nvidia-smi                       # an L4, 1024MiB
python3 -c "import torch; print(torch.cuda.is_available())"   # True
cd ~/gpu-training && ls          # nine numbered chapters
sbatch 01_requesting_a_gpu/hello-gpu.sl
seff <jobid>                     # must include the two GPU lines
```

If `nvidia-smi` reports 23034MiB rather than 1024MiB, the session is running an
older image than the branch expects.

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
./run-local.sh --device rtxpro6000 --vram ""   # a different card, full size
./run-local.sh --shell                         # a terminal instead of JupyterLab
```

## Timing

Roughly three hours with exercises, or two if chapters 7 and 8 are presented
rather than worked through.

| Chapter | Time | Notes |
|---|---|---|
| 0. What a GPU is | 15 min | Discussion. No terminal needed |
| 1. Requesting a GPU | 25 min | Everyone submits both scripts |
| 2. Did I get a GPU? | 20 min | The commenting-out exercise is the important one |
| 3. Watching with nvtop | 25 min | `watch-me.sl` runs 8 minutes; start it before you explain the display |
| 4. Reading seff | 25 min | `starved.sl` and `fed.sl` take about a minute each |
| 5. RAM and VRAM | 30 min | The OOM demonstration always generates questions |
| 6. How many CPUs | 25 min | `scan-cpus.sh` submits 3 jobs; ~2 minutes total |
| 7. Splitting the work | 20 min | Mostly discussion of learners' own workflows |
| 8. Precision | 25 min | The RTX PRO 6000 comparison is the memorable part |
| 9. Choosing a GPU | 25 min | The three-researcher exercise works well in pairs |

!!! note "Things worth saying out loud"

    - **At the start:** there is no GPU here, and no timing in this environment
      means anything. Say it once clearly and it will not come up again.
    - **Chapter 3:** start `watch-me.sl` before you explain `nvtop`, so there
      is something to look at when you get there.
    - **Chapter 5:** the most common question is "so how do I ask for more
      VRAM?" The answer — you cannot, you choose a card — is the point of the
      chapter.
    - **Chapter 8:** the RTX PRO 6000 being both the best fp32 card and nearly
      the worst fp64 card is the thing people remember. Spend time on it.

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

Chapter 8's precision figures are published specifications shown in a table,
not measurements — the environment cannot demonstrate the speed difference, so
the chapter demonstrates the *accuracy* difference, which is real, and gives
the speed ratios as documentation.
