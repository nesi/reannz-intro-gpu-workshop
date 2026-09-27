# 2. Which GPU should I use?

!!! clipboard-list "Lesson Objectives"

    - Know which GPUs Mahuika has, and how to ask for one
    - Work out whether your job will fit in a card's memory
    - Decide whether your work needs double precision, and what that rules out

!!! clipboard-question "Questions"

    - What GPUs can I ask for?
    - Which one should I ask for, and why not simply the biggest?

## The GPUs available on Mahuika

We have a number of GPUs available on Mahuika for scientific research. These
GPUs, and how you ask for each of them, are below:

| GPU | Per node | Total on Mahuika | Request |
|---|---|---|---|
| **NVIDIA L4** | 4 | 16 | `l4:1` |
| **NVIDIA A100 40 GB** | 3 | 9 | `a100_40:1` |
| **NVIDIA A100 80 GB** | 4 | 16 | `a100:1` |
| **NVIDIA H100** | 2 | 8 | `h100:1` |
| **NVIDIA RTX PRO 6000** | 2 | 8 | `pro_6000:1` |

---

## How to choose which GPU to use

There are two questions you need to ask yourself when determining what GPU you should use for your job: 

1. **Will my job fit in the card's memory?** If it does not, the job cannot run
   there at all.
2. **Does my software use single or double precision?** Get this wrong and the
   job runs perfectly correctly, just tens of times slower than it should.

### GPU Memory (VRAM)

The GPU Memory, also know as VRAM, is the amount of data that can be place on a GPU. 
This memory is typically used to store the variables in your machine learning or 
AI model. Each card has different amounts of VRAM it can hold: 

| GPU | Memory |
|---|---|
| **NVIDIA L4** | 24 GB |
| **NVIDIA A100 40 GB** | 40 GB |
| **NVIDIA A100 80 GB** | 80 GB |
| **NVIDIA H100** | 94 GB |
| **NVIDIA RTX PRO 6000** | 96 GB |

Unlike CPU memory (Called RAM) which you do request, for GPUs you get all the VRAM. Therefore, it is 
important that you choose the GPU that will fit your model or data appropriately. 

* You want to avoid asking for a GPU that requires far more VRAM than you need. 
* For example, if you only need 18 GBs of VRAM, choosing an L4 GPU would be the most appropriate. 
Asking for any other card would be an inappropriate use of resources. 

!!! note "Two GPUs is not more memory"

    Two 24 GB L4s are not a 48 GB card. Unless your software explicitly
    supports splitting a job across devices, the second GPU is
    a separate 24 GB your job cannot reach.
    Most softwares do not support splitting a job across devices

How do you choose which sized card you should use depends on what you are trying to do.
It is often very hard to estimate this in theory, but in practice it is possible to find
this out through short test runs. 

We will see at the end of this chapter how to decide which sized card is appropriate for your job. 

### Precision

**What is precision?**

Precision is the number of significant figures that can be stored on a GPU. 

**Why is precision important?**

1. For some calculations, having too few significant figures can introduce errors 
after many iterations of calculations. However it only affects some types of calculation types. 
2. It is also important because **different GPUs run different precision types at different speeds**.

There are two precision types that we will focus on: 

* `float32` (fp32)
* `float64`  (fp64). 

Here is some information about these two types of precision:

| Format | Also called | Significant digits | Bytes |
|---|---|---|---|
| `float32` | single precision, fp32 | ~7 | 4 |
| `float64` | double precision, fp64 | ~16 | 8 |

**Which precision type does my software use?**

In practise, it ultimately depends on what precision type your software was written for. 

* fp32 is generally used for machine learning/AI processes, as well as for
  molecular dynamics.
* fp64 is generally used for softwares where a high level of precision is
  needed, such as many chemistry and engineering softwares where small errors
  can build.
* Always consult your software's instruction manual to find out which precision type
  your software uses

As a rough guide:

| Usually needs fp64 | Usually fine in fp32 |
|---|---|
| Quantum chemistry (VASP, Gaussian, CP2K) | Machine learning, training and inference |
| Computational fluid dynamics | Molecular dynamics (LAMMPS, GROMACS) |
| Climate and ocean models | Image and signal processing |
| Iterative solvers, eigenvalue problems | Most Monte Carlo work |

**Why is it important to understand the precision type my software uses?**

It is important because different GPUs perform calculations with different precision types at different speeds. 

* Every GPU can do both types of calculations. What differs enormously is how fast...

Shown below are the calculation speeds (TFLOPS) of each card type at REANNZ for fp32 and fp64 precision.

| GPU | fp32 | fp64 |
|---|---|---|
| **NVIDIA L4** | 30.3 TFLOPS | 0.5 TFLOPS |
| **NVIDIA A100** (40 GB and 80 GB) | 19.5 TFLOPS | 9.7 TFLOPS |
| **NVIDIA H100** | 60 TFLOPS | 30 TFLOPS |
| **NVIDIA RTX PRO 6000** | 120 TFLOPS | 1.9 TFLOPS |

The number of TFLOPS each card performs across each float type is an 
unintuitive number on its own, but the comparison of TFLOPS between float type
and card is useful:

1. **The performance of fp32 software is RTX PRO 6000 > H100 > L4 > A100**

    This means if you are wanting to perform machine learning/AI
    workloads that generally use fp32, this is the order of GPUs you would want to
    consider if you are thinking about performance.

    Note that while the L4s are more performative than the A100s, you may need more
    GPU memory than the 24 GB available on the L4s, so this may be a constraint.

2. **The fp64 of the L4 and RTX PRO 6000 are very low compared to the A100 and H100**

    Roughly sixty times lower, in both cases. From this we can see that **you should
    never use the L4 or the RTX PRO 6000 if your software uses fp64** — if your work
    needs double precision, your choice is the A100 or the H100, whatever else is
    true.

!!! warning "Do not perform double-precision jobs on the L4 or RTX Pro 6000 Cards"

    An eight-hour double-precision job on an A100 would take roughly two weeks
    on an L4. You will not see an error message for this, so watch out. 

**Some final pointers**

* If your software can use fp32, use it over fp64. fp32 calculations are generally much faster than fp64. 
* If you know that your software performs calculations where small errors compound over millions of steps, you will need fp64.


## Summary: Choosing your card

GPU memory (VRAM) and precision type needed are the main points you need to 
consider when choosing a GPU for youe job. The figure below shows a graphic that 
is designed to help you test which GPU is right for you. 

![Choosing a GPU](./fig/choosing-a-gpu.png){: .center}

The general approach is the following:

1. Determine which precision type you need. This determine the types of GPUs you should use,
as well as the order you should try them in.

2. Perform 15 minute test jobs on each GPU in the order given to determine which is appropriate for 
you to use: 

    1. **Did the job run out of GPU memory?** Move to the next GPU up the ladder.
       Nothing else you can do will make it fit.
    2. **Is the GPU sitting at 0% utilisation?** Stop climbing — your program is
       not using the GPU at all, and a bigger one will not change that.
    3. **Record your GPU utilisation, GPU memory and step count.** Do this before
       deciding anything, while the numbers are in front of you.
    4. **Are you happy with how long the calculation took?** If yes, **this is your
       card** — stop here. If not, move up one rung and run the 15 minutes again.

!!! note "Why record the numbers before you decide"

    Step 4 is a judgement, and it is much easier to make with the previous
    rung's figures written down. "Is this fast enough?" is hard to answer in
    the abstract; "is this enough faster than the L4 to be worth the queue?" is
    not.

    [Chapter 6](06-tools-for-measuring.md) covers reading those numbers off a finished
    job with `seff`.

!!! graduation-cap "Keypoints"

    - Five things to ask for, differing in **memory** and in
      **double-precision speed**, not simply in how fast they are.
    - The A100 comes in **40 GB and 80 GB**. They are the same chip at the same
      speed — name the smaller one if your job fits in it.
    - Name the type, and ask for **one** unless your software can use more.
    - **There is no flag for GPU memory** — you get all of whatever card you
      asked for, and two GPUs do not give you more.
    - Estimate memory at roughly 4× the model size for training, or measure a
      short run.
    - **fp64 work belongs on an A100 or H100.** The L4 and RTX PRO 6000 are
      about sixty times slower at it, with no warning.
    - Then take the **smallest card that fits** — shorter queue, fairer share,
      same result.
