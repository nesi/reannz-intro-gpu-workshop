# 4. Which GPU: precision

!!! clipboard-list "Lesson Objectives"

    - Know which GPUs Mahuika has, and how to ask for each one
    - Decide whether your work needs double precision, and what that rules out
    - Know when lower precision is worth using for machine learning

!!! clipboard-question "Questions"

    - What GPUs can I ask for?
    - My job runs on all of them. Does it matter which one I choose?

## The GPUs available on Mahuika

We have a number of GPUs available on Mahuika for scientific research. These
GPUs, and how you ask for each of them, are below:

| GPU | Per node | Total on Mahuika | Request |
|---|---|---|---|
| **NVIDIA L4** | 4 | 16 | `l4:1` |
| **NVIDIA A100 40 GB** | 3 | 6 | `a100:1` + `--constraint=a100_40gb` |
| **NVIDIA A100 80 GB** | 4 | 16 | `a100:1` + `--constraint=a100_80gb` |
| **NVIDIA H100** | 2 | 8 | `h100:1` |
| **NVIDIA RTX PRO 6000** | 2 | 8 | `pro_6000:1` |

!!! note "Asking for a particular A100"

    Both A100s have the same Slurm name, `a100`, so `--gpus-per-node a100:1`
    on its own can land on either of them. Choose which with `--constraint`
    ([Using GPUs](https://docs.nesi.org.nz/Batch_Computing/Using_GPUs/#request-gpu-resources-using-slurm)):

    ```bash
    #SBATCH --gpus-per-node a100:1
    #SBATCH --constraint    a100_40gb     # the 40 GB A100
    ```

    ```bash
    #SBATCH --gpus-per-node a100:1
    #SBATCH --constraint    a100_80gb     # the 80 GB A100
    ```

    Leaving the constraint out is the same mistake as leaving out the type in
    [your first GPU job](first-gpu-job.md): you get whichever is free, and
    runs you cannot compare — or 40 GB of memory when your job needed 80.

!!! dumbbell "Optional exercise: ask for each A100"

    Ask for each A100 in turn, and watch the constraint choose between them.
    `--wrap` runs a single command as a job, with no script:

    ```bash
    cd ~/gpu-training/precision
    query="nvidia-smi --query-gpu=name,memory.total --format=csv,noheader"
    sbatch --gpus-per-node a100:1 --constraint a100_40gb --wrap "$query"
    sbatch --gpus-per-node a100:1 --constraint a100_80gb --wrap "$query"
    ```

    Each job writes one line to its `slurm-<JobID>.out`.

    ??? "What you should see"

        ```
        NVIDIA A100-PCIE-40GB, 40960 MiB
        NVIDIA A100-SXM4-80GB, 81920 MiB
        ```

        Both jobs asked for `a100:1`. The constraint is what decided that one
        got the 40 GB card and the other the 80 GB.

## Two questions decide the card

1. **Does your software use single or double precision?** Get this wrong and
   the job runs perfectly correctly, just many times slower than it should.
   That is this chapter.
2. **Will your job fit in the card's memory?** If it does not, the job cannot
   run there at all. That is [the next chapter](gpu-memory.md).

Precision comes first, because it rules cards in or out. Memory then picks
between what is left.

## Precision

**What is precision?**

Precision is how many significant figures a number is stored with.

**Why is precision important?**

1. For some calculations, having too few significant figures introduces
   errors that build up over many iterations. It only affects some kinds of
   calculation.
2. **Different GPUs run different precisions at very different speeds.**

There are two precision types to focus on:

| Format | Also called | Significant digits | Bytes |
|---|---|---|---|
| `float32` | single precision, fp32 | ~7 | 4 |
| `float64` | double precision, fp64 | ~16 | 8 |

**Which precision type does my software use?**

It depends on what your software was written for.

* fp32 is generally used for machine learning and AI, as well as for
  molecular dynamics.
* fp64 is generally used where a high level of precision is needed, such as
  many chemistry and engineering codes where small errors can build up.
* Always check your software's documentation to find out which it uses.

As a rough guide:

| Usually needs fp64 | Usually fine in fp32 |
|---|---|
| Quantum chemistry (VASP, Gaussian, CP2K) | Machine learning, training and inference |
| Computational fluid dynamics | Molecular dynamics (LAMMPS, GROMACS) |
| Climate and ocean models | Image and signal processing |
| Iterative solvers, eigenvalue problems | Most Monte Carlo work |

**Why does it matter which card?**

Every GPU can do both kinds of calculation. What differs enormously is how
fast. These are the calculation speeds (TFLOPS) of each card at REANNZ:

| GPU | fp32 | fp64 |
|---|---|---|
| **NVIDIA L4** | 30.3 TFLOPS | 0.5 TFLOPS |
| **NVIDIA A100** (40 GB and 80 GB) | 19.5 TFLOPS | 9.7 TFLOPS |
| **NVIDIA H100** | 60 TFLOPS | 30 TFLOPS |
| **NVIDIA RTX PRO 6000** | 120 TFLOPS | 1.9 TFLOPS |

A TFLOPS figure means little on its own, but the comparisons between cards and
between precisions do:

1. **For fp32 work, the order is RTX PRO 6000 > H100 > L4 > A100.**

    If you run machine learning or other fp32 work, this is the order of cards
    to consider for speed. The L4 beats the A100 here, though its 24 GB of
    memory may be too small for your job — that is
    [the next chapter](gpu-memory.md).

2. **At fp64, the L4 and RTX PRO 6000 fall far behind.**

    Each does fp64 at about a sixtieth of its own fp32 speed. Against an
    A100, the L4 is about twenty times slower at fp64 and the RTX PRO 6000
    about five times, and the H100 is three times faster again. **If your
    work needs double precision, your choice is the A100 or the H100, whatever
    else is true.**

!!! warning "Do not run double-precision jobs on the L4 or RTX PRO 6000"

    An eight-hour double-precision job on an A100 would take about a week on
    an L4. You will not see an error message for this, so watch out.

**Some final pointers**

* If your software can use fp32, use it over fp64. fp32 calculations are
  generally much faster than fp64.
* If your software performs calculations where small errors compound over
  millions of steps, you will need fp64.

!!! note "Lower precision for machine learning"

    fp32 and fp64 are not the only choices. Machine learning frameworks can
    also compute in **bf16** or **fp16**, two bytes per number, and all four
    of Mahuika's GPU models have *tensor cores* that run these many times
    faster than ordinary fp32 arithmetic. They also support **TF32**, which
    runs fp32 matrix maths on the tensor cores.

    In PyTorch, mixed precision is a block around your forward pass, and TF32
    is one line:

    ```python
    torch.set_float32_matmul_precision("high")     # TF32 for fp32 matrix maths

    with torch.autocast(device_type="cuda", dtype=torch.bfloat16):
        loss = model(batch)
    ```

    Two bytes per number also means half the GPU memory, which can be the
    difference between fitting a card and not. Most training is fine in bf16,
    but check that your results are — and none of this is any use to software
    that needs fp64.

!!! dumbbell "Optional exercise: watch fp32 go wrong"

    If you have time:

    ```bash
    cd ~/gpu-training/precision
    module load PyTorch/2.13.0-foss-2026-Python-3.14.4-CUDA-13.2.1
    python3 accuracy.py
    python3 show_fleet.py
    ```

    [`accuracy.py`](https://github.com/nesi/reannz-intro-gpu-workshop/blob/main/examples/precision/accuracy.py){: target="_blank" rel="noopener" } shows fp32 losing accuracy in three ways you
    can check by hand, and [`show_fleet.py`](https://github.com/nesi/reannz-intro-gpu-workshop/blob/main/examples/precision/show_fleet.py){: target="_blank" rel="noopener" } prints the published speeds of
    every card side by side.

!!! graduation-cap "Keypoints"

    - Five things to ask for, differing in **memory** and in
      **double-precision speed**, not simply in how fast they are.
    - The A100 comes in **40 GB and 80 GB**. They are the same chip at the same
      speed, and share the Slurm name `a100` — choose with
      `--constraint=a100_40gb` or `--constraint=a100_80gb`.
    - Name the type, and ask for **one** unless your software can use more.
    - **fp64 work belongs on an A100 or H100.** At fp64 the L4 is about twenty
      times slower than an A100, and the RTX PRO 6000 about five, with no
      warning.
    - For machine learning, **bf16 and TF32** run on the tensor cores, faster
      than fp32 and in half the memory.
