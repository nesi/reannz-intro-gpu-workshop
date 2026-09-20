# R2: The GPUs on this cluster

Figures are the manufacturers' published specifications, and the node layout is
from the cluster's [hardware
documentation](https://docs.nesi.org.nz/Batch_Computing/Hardware/). Nothing on
this page is measured in the training environment, which has no GPU.

## Side by side

| | **L4** | **A100** | **H100 NVL** | **RTX PRO 6000** |
|---|---|---|---|---|
| Slurm name | `l4` | `a100` | `h100` | `pro_6000` |
| VRAM | 24 GB | 80 GB | 94 GB | 96 GB |
| Per node | 4 | 4 | 2 | 2 |
| Architecture | Ada Lovelace | Ampere | Hopper | Blackwell |
| Compute capability | 8.9 | 8.0 | 9.0 | 12.0 |
| **fp32** | 30.3 TFLOPS | 19.5 TFLOPS | 60 TFLOPS | **120 TFLOPS** |
| **fp64** | 0.5 TFLOPS | **9.7 TFLOPS** | **30 TFLOPS** | 1.9 TFLOPS |
| **fp64 : fp32** | 1:62 | **1:2** | **1:2** | 1:63 |
| Memory bandwidth | 300 GB/s | 2.0 TB/s | 3.9 TB/s | 1.6 TB/s |
| Power | 72 W | 400 W | 400 W | 600 W |

## Host nodes

| GPU | Node CPU | Cores | RAM | GPUs | Cores per GPU |
|---|---|---|---|---|---|
| A100 | AMD Milan 7713P | 64 | 512 GB | 4 | ~16 |
| RTX PRO 6000 | 2× AMD Genoa 9634 | 168 | 768 GB | 2 | ~84 |
| H100 NVL | 2× AMD Genoa 9634 | 168 | 768 GB | 2 | ~84 |
| L4 | 2× AMD Genoa 9634 | 168 | 768 GB | 4 | ~42 |

"Cores per GPU" is a fair share, not a limit — but it is a sensible ceiling to
have in mind when deciding `--cpus-per-task`.

## How to request each

```bash
#SBATCH --gpus-per-node l4:1
#SBATCH --gpus-per-node a100:1
#SBATCH --gpus-per-node h100:1
#SBATCH --gpus-per-node pro_6000:1
```

Ask for more than one only if your software says it can use more than one.

## Choosing between them

!!! warning "Double precision first"

    The **L4 and RTX PRO 6000 should be avoided for double-precision (fp64)
    work.** At about 1:60 they are roughly thirty times slower than an A100 at
    fp64, and nothing warns you — the job simply takes weeks instead of hours.

    If your software needs fp64, your choice is **A100 or H100**, whatever else
    is true.

Otherwise, by what you need:

| Situation | Card |
|---|---|
| fp32 or fp16, fits in 24 GB | **L4** — shortest queue, plenty for most work |
| fp64, up to 80 GB | **A100** |
| fp64, the largest models | **H100 NVL** |
| fp32/fp16 and very large, or wants the most raw fp32 | **RTX PRO 6000** |
| Not sure yet | **L4** — measure with `seff`, move up if it does not fit |

**Take the smallest card your work fits in.** Small cards are more plentiful
and less contended, so your job starts sooner, and you leave the large ones for
work that needs them.

## Reading the numbers

**TFLOPS** is trillions of floating-point operations per second. It is a
theoretical peak that no real program reaches, so treat it as a way to compare
cards rather than a prediction. The *ratios* between cards are meaningful; the
absolute values are not.

**fp64 : fp32** is the ratio of double- to single-precision throughput, and it
is the most decision-relevant number on this page. A 1:2 card does double
precision at half its single-precision rate, which is as good as it gets. A
1:64 card does it about sixty times slower — these are cards whose lineage is
graphics and machine learning, where fp64 is almost never wanted.

**Memory bandwidth** is how fast the GPU can move data in and out of its own
memory. Many real workloads are limited by this rather than by arithmetic, so a
card with more bandwidth can outperform one with a better TFLOPS number.

**Compute capability** is NVIDIA's version number for the hardware's features.
Some software requires a minimum; it rarely affects which card you should
choose.

!!! note "Why the RTX PRO 6000 is the interesting one"

    It has the highest fp32 figure in the fleet by a wide margin — four times
    an A100 — and one of the lowest fp64 figures.

    For machine learning it is outstanding. For a quantum chemistry or CFD code
    it is one of the worst choices available. The same card, for the same
    money, depending entirely on what you run on it. That is the clearest
    illustration there is of why [chapter 8](08-precision.md) matters.
