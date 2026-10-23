#!/usr/bin/env python3
"""Decide which GPU to ask for, from four things you can find out.

By this point in the workshop you have measured everything this needs:

  1. Does your software need double precision?     (Which GPU: precision)
  2. How much VRAM does your work need?            (Which GPU: will it fit?)
  3. How many CPU cores keep the GPU fed?          (How many CPUs)
  4. What fraction of your runtime is on the GPU?  (B2: Where the time goes)

This walks through them and prints a Slurm request. It is not an oracle - it
encodes the same reasoning the earlier chapters explained, so that you have
something to take away and apply to your own work.

    python3 pick_a_gpu.py                       # ask me the questions
    python3 pick_a_gpu.py --fp64 --vram 40      # or answer them up front
"""

import argparse
import sys

from dataclasses import dataclass


@dataclass(frozen=True)
class Card:
    name: str
    vram_gb: int
    max_per_node: int
    fp32_tflops: float
    fp64_tflops: float
    gres_name: str          # how --gpus-per-node spells it
    feature: str = ""       # the --constraint that picks it, if it shares a name

    @property
    def fp64_ratio(self) -> float:
        return self.fp64_tflops / self.fp32_tflops


# The GPUs on Mahuika, from the manufacturers' published figures.
CARDS = [
    Card("NVIDIA L4", 24, 4, 30.3, 0.489, "l4"),
    Card("NVIDIA A100-PCIE-40GB", 40, 3, 19.5, 9.7, "a100", "a100_40gb"),
    Card("NVIDIA A100-SXM4-80GB", 80, 4, 19.5, 9.7, "a100", "a100_80gb"),
    Card("NVIDIA H100 NVL", 94, 2, 60.0, 30.0, "h100"),
    Card("NVIDIA RTX PRO 6000 Blackwell Server Edition", 96, 2, 120.0, 1.9, "pro_6000"),
]

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--fp64", action="store_true", help="software needs double precision")
parser.add_argument("--vram", type=float, help="GB of VRAM your work needs")
parser.add_argument("--cpus", type=int, help="CPU cores that kept the GPU fed")
parser.add_argument("--gpu-share", type=float, help="%% of runtime spent on the GPU")
args = parser.parse_args()

interactive = args.vram is None and sys.stdin.isatty()


def ask(question, default):
    if not interactive:
        return default
    reply = input(f"{question} [{default}] ").strip()
    return reply or default


print()
print("Choosing a GPU")
print("=" * 70)

# --- 1. precision ----------------------------------------------------------
needs_fp64 = args.fp64
if interactive and not args.fp64:
    needs_fp64 = ask(
        "\n1. Does your software need double precision (fp64)?\n"
        "   Quantum chemistry, CFD and linear solvers usually do. Machine\n"
        "   learning and molecular dynamics usually do not. (y/n)",
        "n",
    ).lower().startswith("y")

# --- 2. VRAM ---------------------------------------------------------------
vram = args.vram
if vram is None:
    vram = float(
        ask(
            "\n2. How much VRAM does your work need, in GB?\n"
            "   'Which GPU: will it fit?' shows how. If you do not know,\n"
            "   guess high and measure with seff afterwards.",
            "8",
        )
    )

# --- 3. CPUs ---------------------------------------------------------------
cpus = args.cpus
if cpus is None:
    cpus = int(
        ask(
            "\n3. How many CPU cores kept the GPU busy?\n"
            "   'How many CPUs' measures this. 2 is a reasonable starting guess.",
            "2",
        )
    )

# --- 4. GPU share ----------------------------------------------------------
share = args.gpu_share
if share is None:
    share = float(
        ask(
            "\n4. What percentage of your runtime is actually on the GPU?\n"
            "   seff reports this - see 'Measuring a GPU job'. 60 is a\n"
            "   reasonable guess.",
            "60",
        )
    )

# --------------------------------------------------------------- reasoning

print()
print("=" * 70)
print()

candidates = list(CARDS)

if needs_fp64:
    candidates = [d for d in candidates if d.fp64_ratio > 0.1]
    print("Double precision required, so the 1:64 cards are out:")
    print("  at fp64 the L4 is about 20x slower than an A100, and the RTX PRO")
    print("  6000 about 5x, so an overnight run becomes a week on an L4.")
    print()

fits = [d for d in candidates if d.vram_gb >= vram]
if not fits:
    biggest = max(candidates, key=lambda d: d.vram_gb)
    print(f"Nothing in the fleet has {vram:.0f} GB of VRAM.")
    print(f"The largest available is the {biggest.name} at {biggest.vram_gb} GB.")
    print()
    print("Your options, in the order worth trying:")
    print("  * Reduce the batch size. This is usually the whole fix.")
    print("  * Use a lower precision, if the work tolerates it.")
    print("  * Split the model across more than one GPU, if your software")
    print("    supports it - most does not.")
    sys.exit(1)

# The smallest card that fits is the right default: it is the one you will
# wait least for, and an idle 80 GB card helps nobody else either.
choice = min(fits, key=lambda d: (d.vram_gb, d.fp32_tflops))

print(f"Ask for: {choice.name}")
print()
print(f"  VRAM          {choice.vram_gb} GB, and you need about {vram:.0f} GB")
print(f"  fp64          {choice.fp64_tflops:.1f} TFLOPS "
      f"(1:{round(1 / choice.fp64_ratio)} of its fp32 rate)")
print(f"  Per node      {choice.max_per_node}")
print()
print("Why this one and not a bigger one:")
print("  The smallest card your work fits in is almost always the right")
print("  choice. It is the one with the shortest queue, and a job that uses")
print("  20% of an A100 has taken a card someone else needed all of.")

if len(fits) > 1:
    others = ", ".join(d.name for d in fits if d is not choice)
    print()
    print(f"  Also big enough, if this one is busy: {others}")

print()
print("Your Slurm request")
print("-" * 70)
print("#!/bin/bash -e")
print("#SBATCH --job-name      my-gpu-job")
print("#SBATCH --account       nesi99991")
print("#SBATCH --time          01:00:00")
print(f"#SBATCH --cpus-per-task {cpus}")
print("#SBATCH --mem           8GB          # RAM, not VRAM - measure it with seff")
print(f"#SBATCH --gpus-per-node {choice.gres_name}:1")
if choice.feature:
    # Both A100s are "a100" to Slurm; the constraint is what picks the size.
    print(f"#SBATCH --constraint    {choice.feature}")

print()
if share < 40:
    print(f"One warning: only {share:.0f}% of your runtime is on the GPU.")
    print("The GPU will sit idle for most of your allocation, and a faster")
    print("card cannot fix that. Before you queue this, read B2 again")
    print("and see whether the CPU side can be sped up or overlapped instead.")
else:
    print(f"With {share:.0f}% of your runtime on the GPU, this is a reasonable")
    print("thing to be asking for a GPU to do.")

print()
print("Whatever you choose, run it once with '--qos debug' for 15 minutes")
print("first, then check it with seff before you queue the long version.")
print()
