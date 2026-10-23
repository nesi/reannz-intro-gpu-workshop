# B1: Getting your software running on a GPU

!!! circle-info "Beyond the basics"

    Not covered in the live workshop. Read it before you set up your own GPU
    software on the cluster — it is where most first GPU jobs go wrong, long
    before the choice of card matters.

!!! clipboard-list "Lesson Objectives"

    - Know the three ways GPU software arrives on the cluster, and what each
      needs from you
    - Check that a build can use a GPU at all, and the GPU you asked for
    - Test new software in an interactive session rather than a queued job

!!! clipboard-question "Questions"

    - Do I need to load a CUDA module?
    - My software works on one card and not on another. Why?

## Three ways to get GPU software

| | How you get it | What you need to do about CUDA |
|---|---|---|
| **A module** | `module spider` and `module load` | Nothing. The module loads the CUDA it was built with |
| **A Python environment** | `pip install` or conda | Usually nothing. PyTorch and TensorFlow bring their own CUDA, so what you need is a GPU build, not a CUDA module |
| **A container** | `apptainer pull`, for example from NVIDIA's NGC registry | Run it with `--nv`, or the container cannot see the GPU |

Start with a module if there is one, and check the cluster's
[application pages](https://docs.nesi.org.nz/Software/Available_Applications/)
first: widely used GPU packages often have a page with the exact settings.

You only need to load a CUDA module yourself when you are compiling GPU code,
or when your software's instructions tell you to.

### Modules

```bash
module spider <name>                # which versions exist
module load <name>/<version>        # loads its CUDA along with it
```

### Python environments

Install a GPU build, not the default one. For PyTorch, the install command on
[pytorch.org](https://pytorch.org/get-started/locally/) names the CUDA version
in its index URL, for example:

```bash
pip install torch --index-url https://download.pytorch.org/whl/cu128
```

Then check what you got, as in [Is it really using the GPU?](using-the-gpu.md):

```bash
python -c "import torch; print(torch.__version__, torch.version.cuda)"
#   2.14.0+cu128  12.8   -> a CUDA build
#   2.14.0+cpu    None   -> a CPU-only build; it will never use a GPU
```

Environments are large. Your home directory holds 20 GB, so put big
environments in your project directory instead
([Filesystems and quotas](https://docs.nesi.org.nz/Storage/Filesystems_and_Quotas/)).

### Containers

```bash
module load Apptainer
apptainer pull pytorch.sif docker://nvcr.io/nvidia/pytorch:<tag>
apptainer exec --nv pytorch.sif python my_script.py
```

**Without `--nv` the container cannot see the GPU**, and most software inside
it quietly runs on the CPU — the same failure as forgetting `--gpus-per-node`.
The cluster's [NVIDIA GPU containers](https://docs.nesi.org.nz/Software/Containers/NVIDIA_GPU_Containers/)
page has a worked example.

## Is the build new enough for the card?

Each generation of GPU has a *compute capability*, and a build only runs on
the generations it was compiled for:

| GPU | Compute capability |
|---|---|
| A100 | 8.0 |
| L4 | 8.9 |
| H100 | 9.0 |
| RTX PRO 6000 | 12.0 |

The RTX PRO 6000 is the newest card, so it is the one older builds fail on.
The error looks like one of these:

```
CUDA error: no kernel image is available for execution on the device
NVIDIA RTX PRO 6000 ... with CUDA capability sm_120 is not compatible with the current PyTorch installation.
```

The fix is a newer build — for PyTorch, one built for CUDA 12.8 or later. **The
same software working on an A100 and failing on the RTX PRO 6000 is almost
always this.**

The node matters too. `nvidia-smi` shows, top right, the newest CUDA version
its driver supports. A build made for a newer major version of CUDA than that
fails with `CUDA driver version is insufficient for CUDA runtime version`.
Within one major version a newer build still runs: the cluster's PyTorch
module, built for CUDA 13.2, runs on a driver that shows 13.0.

## Test it in an interactive session

You can install software on the login node, but you cannot test it there:
the GPUs are on the compute nodes. Test it in
[an interactive session](interactive-sessions.md) on the card you intend to
use:

1. Hold a GPU with a job that waits, and `svisit` it.
2. Load your module, activate your environment, or point at your container.
3. Make the checks from [Is it really using the GPU?](using-the-gpu.md).
4. Run your program on the smallest input that does something real.
5. `exit`, and `scancel` the job.

Ten minutes there saves a day of queueing jobs that fail at the first line.

!!! note "If you write your own GPU code"

    Writing GPU code is beyond this workshop. If you want to see what it looks
    like, [`cuda_kernel.py`](https://github.com/nesi/reannz-intro-gpu-workshop/blob/main/examples/software/cuda_kernel.py){: target="_blank" rel="noopener" }
    has two small CUDA kernels written in Python with Numba. To compile CUDA
    code of your own with `nvcc`, load a CUDA module first.

!!! graduation-cap "Keypoints"

    - **Modules load their own CUDA.** So do PyTorch and TensorFlow from pip
      or conda. Load a CUDA module yourself only to compile code.
    - Check you have a **GPU build**: `+cu128`, not `+cpu`.
    - A build must be **new enough for the card**. Failing on the RTX PRO 6000
      and working on an A100 means the build is too old.
    - Containers need **`--nv`** to see the GPU.
    - **Test in an interactive session**, not in a queued job, and not on the
      login node.
