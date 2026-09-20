# Introduction to Using GPUs on High Performance Clusters (HPC)

![image](./fig/Title_GPU.svg#only-light){: width="560px" .center}
![image](./fig/Title_GPU_dark.svg#only-dark){: width="560px" .center}

This workshop is about **using** GPUs, not programming them. It is for
researchers who have software that can run on a GPU — or think it might — and
need to work out which GPU to ask for, how to ask for it, and whether they
actually got any benefit from it.

You will not write a CUDA kernel. You will not need to know what a kernel is.
What you will do is run jobs, watch them, read what the cluster tells you about
them afterwards, and use that to make better requests next time.

!!! clipboard-question "The question this workshop answers"

    **"Which GPU should I use for my work?"**

    It is the first thing people ask and the last thing that can honestly be
    answered, because the answer depends on four things you have to measure
    first: how much GPU memory your work needs, how many CPU cores it takes to
    keep the GPU busy, how much of your runtime is on the GPU at all, and
    whether your software needs double precision.

    Chapters 1 to 8 are how you find those four numbers. Chapter 9 puts them
    together.

!!! clipboard-list "Learning Objectives"

    By the end of this workshop, you will be able to:

    - Request a GPU in a Slurm script, and recognise when you have not.
    - Use `nvidia-smi` for the one thing it is good for, and stop using it for
      the things it is not.
    - Watch a running job with `nvtop` and read what the traces are telling you.
    - Read `seff` after a job and say whether the GPU was worth asking for.
    - Tell RAM and VRAM apart, and work out how much of each your work needs.
    - Choose how many CPU cores to request for a GPU job, by measuring rather
      than guessing.
    - Identify which parts of your workflow a GPU can help with, and which it
      cannot.
    - Say whether your software needs double precision, and what that rules in
      and out.
    - Choose the right GPU for a piece of work and justify the choice.

| **Lesson** | **Overview** |
|:-----------|:-------------|
| [What a GPU is, and when it helps](00-what-a-gpu-is.md) | Why some work goes faster on a GPU and most does not |
| **Getting a GPU job running** | |
| [1. Requesting a GPU](01-requesting-a-gpu.md) | The Slurm flags, and what each one actually does |
| [2. Did I get a GPU?](02-did-i-get-a-gpu.md) | Checking, and why `nvidia-smi` alone is not enough |
| **Is it doing any work?** | |
| [3. Watching a job with nvtop](03-watching-with-nvtop.md) | See utilisation and memory move while the job runs |
| [4. Reading seff](04-reading-seff.md) | The report card, and the two lines that matter most |
| **Asking for the right resources** | |
| [5. RAM and VRAM](05-ram-and-vram.md) | Two separate pools, and how much of each to ask for |
| [6. How many CPUs?](06-how-many-cpus.md) | Measuring the point where more cores stop helping |
| [7. Splitting CPU and GPU work](07-splitting-the-work.md) | Which parts of your work a GPU can help with |
| **Choosing your hardware** | |
| [8. Precision](08-precision.md) | Single and double precision, and why it decides the card |
| [9. Choosing a GPU](09-choosing-a-gpu.md) | Putting the four measurements together |
| | |
| [Summary and checklist](summarising.md) | Everything, on one page, to take away |
| [R1: Command reference](R1-command-reference.md) | Every command used, with its flags |
| [R2: The GPUs on this cluster](R2-gpu-reference.md) | The fleet, side by side |

!!! clipboard-list "Getting Started"

    This workshop assumes no experience with GPUs. You should be comfortable
    working in a Unix shell — `cd`, `ls`, editing a file — and have used
    `sbatch` to submit a job before, or be willing to learn it here.

    You do **not** need to know any CUDA, C++ or Python beyond reading a short
    script. Bring a laptop and plan to take part actively.

    Everything is done from a **terminal**. In JupyterLab, open one with
    **File → New → Terminal**, then:

    ```bash
    cd ~/gpu-training
    ls
    ```

!!! warning "About the training environment"

    The machines used for this workshop **do not have GPUs**. The session
    emulates one, so that the tools behave exactly as they do on the cluster:
    `nvidia-smi`, `nvtop`, `seff` and `sbatch` all show real utilisation, real
    memory and real job accounting.

    The arithmetic runs on the CPU. **No timing you measure here says anything
    about GPU performance**, and nothing in this workshop asks you to time
    anything. Everything you learn about *reading* these tools transfers to
    the cluster unchanged. Nothing you learn about speed does.

    The emulated card reports **1 GB of GPU memory** rather than the 24 GB a
    real one has, so that running out of memory takes a few seconds rather
    than filling a real card.

- - -

!!! copyright "Attribution Notice"

    * This workshop material draws on the [NeSI support documentation on
      Using GPUs](https://docs.nesi.org.nz/Batch_Computing/Using_GPUs/) and
      the [cluster hardware
      reference](https://docs.nesi.org.nz/Batch_Computing/Hardware/).
    * `seff` and `svisit` are documented as they behave in
      [nesi/opt-nesi-bin](https://github.com/nesi/opt-nesi-bin).
    * The training environment is
      [training-environment-jupyter-gpu-app](https://github.com/nesi/training-environment-jupyter-gpu-app).
