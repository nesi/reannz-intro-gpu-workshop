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
GPUs on Mahuika or another High Performance Computing (HPC) system

Specifically, this workshop will cover what you should consider and what tests 
you should run in order to optimise the efficiency of your GPU jobs.

## Flow of this workshop

The workshop is in three stages.

**Stage 1: Writing your submit script** — asking for the right things:

| **Chapter** | **Overview** |
|:------------|:-------------|
| [1. The submit script](01-the-submit-script.md) | The lines that matter, and which are real decisions |
| [2. Which GPU](02-which-gpu.md) | Precision, GPU memory, and the smallest card that fits |
| [3. How many CPUs](03-how-many-cpus.md) | Feeding the GPU, and where to start |
| [4. How much memory](04-how-much-memory.md) | What a GPU job uses CPU memory for, and how to size it |

**Stage 2: Measuring your GPU jobs** — finding out what your request actually did:

| **Chapter** | **Overview** |
|:------------|:-------------|
| [5. Measuring your GPU jobs](05-measuring-your-jobs.md) | Which questions to ask, and which tool answers each |
| [6. The tools for measuring](06-tools-for-measuring.md) | A test submit script, `seff`, `profile_plot` and `nvtop` |

**Stage 3: Putting it all together** — turning the measurements into a request
you keep:

| **Chapter** | **Overview** |
|:------------|:-------------|
| [7. Putting it all together](07-putting-it-together.md) | The whole loop on one job: watch it, size the card, tune cores and memory |
| [Summary and checklist](summarising.md) | Everything, on one page, to take away |

**Supplementary:** [what a GPU is](S1-what-a-gpu-is.md) for anyone meeting them
for the first time, and [splitting CPU and GPU
work](S2-splitting-the-work.md) for when your utilisation is lower than you
would like. **Reference:** [commands](R1-command-reference.md) and [the GPUs on
this cluster](R2-gpu-reference.md).

!!! clipboard-list "Getting started"

    You should be comfortable in a Unix shell — `cd`, `ls`, editing a file —
    and have used `sbatch` before, or be willing to pick it up here. No GPU
    experience is assumed.

    Everything is done from a **terminal**. In JupyterLab, open one with
    **File → New → Terminal**, then:

    ```bash
    cd ~/gpu-training
    ls
    ```

!!! warning "About the training environment"

    The machines used for this workshop **have no GPUs**. The session emulates
    one, so the tools behave exactly as they do on the cluster: `nvidia-smi`,
    `nvtop`, `seff` and `sbatch` all show real utilisation, real memory and
    real job accounting.

    The arithmetic runs on the CPU. **No timing you measure here says anything
    about GPU performance**, and nothing in this workshop asks you to time
    anything. Everything you learn about *reading* these tools transfers
    unchanged. Nothing you learn about speed does.

    The emulated card reports **1 GB of GPU memory** rather than the 24 GB a
    real one has, so running out of memory takes seconds rather than filling a
    real card.

- - -

!!! copyright "Attribution Notice"

    * Draws on the NeSI support documentation for [Using
      GPUs](https://docs.nesi.org.nz/Batch_Computing/Using_GPUs/) and
      [Hardware](https://docs.nesi.org.nz/Batch_Computing/Hardware/).
    * `seff` and `svisit` are documented as they behave in
      [nesi/opt-nesi-bin](https://github.com/nesi/opt-nesi-bin).
    * The training environment is
      [training-environment-jupyter-gpu-app](https://github.com/nesi/training-environment-jupyter-gpu-app).
