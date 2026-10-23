# Introduction to Using GPUs on High Performance Clusters (HPC)

![image](./fig/Title_GPU.svg#only-light){: width="560px" .center}
![image](./fig/Title_GPU_dark.svg#only-dark){: width="560px" .center}

The goal of this workshop is to show you how to run your software on GPUs as
efficiently as possible, on a high performance computing system like Mahuika.

**What does efficiency mean in this context?** It specifically means how we can
keep the GPU running at its maximum for your computational job or simulation.

Concretely, an efficient GPU job is one where:

- The GPU is **busy** for most of the time you hold it.
- You asked for a card your work **fits in**, and not a larger one.
- You asked for roughly the **CPU cores and memory you actually use**.

**Why is this important?** GPU time is in limited supply, due to its demand for
research applications like AI and simulations. For this reason GPU time is
expensive and precious, and minimising the amount of time you need a GPU to
complete your computational job is very important.

**Mahuika is also a shared resource.** We all want to use the GPUs for our
research. Having efficient jobs makes you a good user of the platform, and
leaves time for other researchers to do their research as well.

## Who should be attending this workshop

You should be attending this workshop if you are using or are interested in using
GPUs on Mahuika or another High Performance Computing (HPC) system.

Specifically, this workshop will cover what you should consider and what tests 
you should run in order to optimise the efficiency of your GPU jobs.

## Flow of this workshop

The workshop is in five stages.

**Stage 1: Getting started with GPUs** — what a GPU is good for, and a first
job that provably uses one:

| **Chapter** | **Overview** |
|:------------|:-------------|
| [1. Introduction](introduction.md) | What a GPU is good at, and the ceiling on what it can do |
| [2. Your first GPU job](first-gpu-job.md) | The lines that matter in a submit script, and a job to run |
| [3. Is it really using the GPU?](using-the-gpu.md) | The checks that catch a job quietly running on the CPU |

**Stage 2: Asking for the right resources** — the three decisions in your
submit script:

| **Chapter** | **Overview** |
|:------------|:-------------|
| [4. Which GPU: precision](precision.md) | The cards, and why double precision rules some of them out |
| [5. Which GPU: will it fit?](gpu-memory.md) | GPU memory, out-of-memory errors, and the smallest card that fits |
| [6. How many CPUs do I need?](how-many-cpus.md) | Feeding the GPU, and where to start |
| [7. How much CPU memory should I request?](cpu-memory.md) | What a GPU job uses RAM for, and how to size it |

**Stage 3: Measuring your GPU jobs** — finding out what your request actually did:

| **Chapter** | **Overview** |
|:------------|:-------------|
| [8. Measuring a GPU job](measuring.md) | A test submit script, `seff`, `profile_plot` and `nvtop` |

**Stage 4: Running interactive jobs** — trying things on a GPU as you go:

| **Chapter** | **Overview** |
|:------------|:-------------|
| [9. Running interactive sessions with GPUs](interactive-sessions.md) | Holding a GPU with a job that waits, and debugging inside it |

**Stage 5: Putting it all together** — turning the measurements into a request
you keep:

| **Chapter** | **Overview** |
|:------------|:-------------|
| [10. Putting it all together](putting-it-together.md) | The whole loop on one job: watch it, size the card, tune cores and memory |
| [Summary and checklist](summarising.md) | Everything, on one page, to take away |

**Beyond the basics** — for after the workshop, when you set up your own work:

| **Page** | **Overview** |
|:------------|:-------------|
| [B1: Getting your software running on a GPU](software.md) | Modules, Python environments, containers, and builds too old for the card |
| [B2: Where the time goes](where-the-time-goes.md) | Measuring the CPU and GPU parts of a job, and reading data quickly |
| [B3: Long jobs](long-jobs.md) | Time limits, checkpoints, and why a job is pending |
| [B4: More than one GPU, and less than one](more-than-one-gpu.md) | When a second GPU helps, and what to do with small jobs |

**Reference:** [commands](R1-command-reference.md) and [the GPUs on this
cluster](R2-gpu-reference.md).

!!! clipboard-list "Getting started"

    You should be comfortable in a Unix shell — `cd`, `ls`, editing a file —
    and have submitted a Slurm job before, or be willing to pick it up here.
    If you have not, the cluster's
    [Submitting your first job](https://docs.nesi.org.nz/Tutorials/Introduction_To_HPC/Submitting_Your_First_Job/)
    tutorial is the place to start. No GPU experience is assumed.

    Everything is done from a **terminal** on Mahuika, in OnDemand or over
    `ssh`. The exercise files live in `~/gpu-training`. If you do not have
    them yet, copy them from the workshop's repository:

    ```bash
    git clone https://github.com/nesi/reannz-intro-gpu-workshop.git
    cp -r reannz-intro-gpu-workshop/examples ~/gpu-training
    cd ~/gpu-training
    ls
    ```

    You can also read them [on GitHub](https://github.com/nesi/reannz-intro-gpu-workshop/tree/main/examples){: target="_blank" rel="noopener" }.

    The exercises use PyTorch from the cluster's modules. The job scripts load
    it themselves. To run Python in a terminal of your own, load it there
    first:

    ```bash
    module load PyTorch/2.13.0-foss-2026-Python-3.14.4-CUDA-13.2.1
    ```

- - -

!!! copyright "Attribution Notice"

    * Draws on the NeSI support documentation for [Using
      GPUs](https://docs.nesi.org.nz/Batch_Computing/Using_GPUs/) and
      [Hardware](https://docs.nesi.org.nz/Batch_Computing/Hardware/).
    * `seff` and `svisit` are documented as they behave in
      [nesi/opt-nesi-bin](https://github.com/nesi/opt-nesi-bin).
