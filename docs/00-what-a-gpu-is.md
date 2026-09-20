# What a GPU is, and when it helps

!!! clipboard-list "Lesson Objectives"

    - Describe, in one sentence, the kind of work a GPU is good at
    - Recognise the kinds of research work that do and do not benefit
    - Understand that "has GPU support" is a property of your software, not of
      your problem

!!! clipboard-question "Questions"

    - Why is a GPU faster than a CPU for some things and slower for others?
    - How do I find out whether my software can use one?

## The one-sentence version

A CPU has a small number of powerful cores that can each do something
different. A GPU has thousands of weak cores that all have to do **the same
thing at the same time, to different data**.

That is the whole trade-off. If your work is "apply this identical operation to
ten million numbers", a GPU will do it in one pass while a CPU grinds through
it. If your work is "do this, then decide what to do next based on the answer",
the GPU's thousands of cores have nothing useful to do and you would have been
better off on the CPU.

| | CPU | GPU |
|---|---|---|
| Cores | tens | thousands |
| Each core | fast, independent, good at branching | slow, must march in step |
| Good at | decisions, sequences, one thing at a time | the same arithmetic over huge arrays |
| Bad at | doing a million identical things at once | anything that branches or waits |

!!! note "A useful mental image"

    A CPU is a handful of professors. A GPU is a stadium full of first-year
    students who all have to be given the same instruction at once.

    If the job is "mark 50,000 identical multiple-choice papers", the stadium
    wins easily. If the job is "read this thesis and decide whether it passes",
    the stadium is useless no matter how many people are in it.

## What this means for research work

**Work that usually benefits**

- Training and running neural networks
- Molecular dynamics (GROMACS, AMBER, NAMD, LAMMPS)
- Large dense linear algebra
- Image and volume processing, where the same filter hits every pixel
- Monte Carlo simulation with many independent samples
- Genomics basecalling and alignment tools written for GPUs

**Work that usually does not**

- Anything dominated by reading and writing files
- Small problems. Moving data to the GPU costs time; if the calculation is
  short, you spend longer on the transfer than you save
- Code with lots of branching, or where each step depends on the last
- Software that has no GPU support — which is most software

!!! warning "The most important point on this page"

    **A GPU does not speed up your work. GPU-aware software speeds up your
    work.**

    There is no setting that makes an ordinary program use a GPU. If your
    software was not written to use one, requesting a GPU does nothing at all
    except make your job wait longer in the queue and take a card away from
    someone who needed it.

    Before requesting a GPU for the first time, find the page in your
    software's documentation that says it supports GPUs, and find out what you
    have to do to switch it on. It is usually a flag, a config setting, or a
    different executable name.

## How to find out about your own software

1. **Search its documentation for "GPU" or "CUDA".** Packages that support
   GPUs say so prominently, because it is a selling point.
2. **Check whether it needs to be switched on.** Many packages have separate
   GPU and CPU builds, or need `-gpu` / `--device cuda` / `use_gpu: true`.
   Installing the GPU build is not the same as using it.
3. **Check the cluster's application pages.** Widely used packages often have
   a support page with the exact settings — for example
   [TensorFlow](https://docs.nesi.org.nz/Software/Available_Applications/TensorFlow/),
   [AlphaFold](https://docs.nesi.org.nz/Software/Available_Applications/AlphaFold/),
   [ABAQUS](https://docs.nesi.org.nz/Software/Available_Applications/ABAQUS/)
   and
   [ont-guppy-gpu](https://docs.nesi.org.nz/Software/Available_Applications/ont-guppy-gpu/).
4. **Ask the support desk.** "Does X benefit from a GPU, and how do I turn it
   on?" is a question they answer often.

!!! dumbbell "Exercise: before you go any further"

    Write down, for the software you actually use:

    1. Its name and version.
    2. Whether its documentation says it supports GPUs.
    3. What you have to change to switch that on.

    If the answer to 2 is "no", the rest of this workshop is still worth
    knowing — you will need it the first time a package you use gains GPU
    support, and it will tell you how to check whether the claim is true.

## What the rest of this workshop does

Assuming your software does support GPUs, everything that follows is about
getting a good one, confirming you got it, and finding out whether it helped.

!!! graduation-cap "Keypoints"

    - A GPU does the **same operation to very many pieces of data at once**.
      That is the only thing it is better at.
    - Work that branches, waits on files, or is simply small will not go faster
      on a GPU — and may go slower.
    - **Software has to be written to use a GPU.** Requesting one does not make
      an ordinary program use it.
    - Check your software's documentation before you request a GPU, not after.
