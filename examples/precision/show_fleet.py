#!/usr/bin/env python3
"""The GPUs available on the cluster, side by side, with the numbers that matter.

These are the manufacturers' published figures, not measurements, printed
together so the trade-offs are visible in one place.

The column to look at first is fp64:fp32. It is the ratio of double-precision
to single-precision throughput, and it splits this fleet cleanly in two.
"""

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

rows = CARDS

print()
print("GPUs on this cluster")
print("=" * 96)
print(
    f"{'Card':<30}{'VRAM':>7}{'Per node':>10}{'fp32':>9}{'fp64':>9}"
    f"{'fp64:fp32':>11}{'Slurm':>20}"
)
print("-" * 96)
for dev in rows:
    ratio = dev.fp64_ratio
    ratio_text = f"1:{round(1 / ratio)}" if ratio else "-"
    print(
        f"{(dev.name if len(dev.name) <= 29 else dev.name[:26] + chr(8230)):<30}"
        f"{dev.vram_gb:>6}G"
        f"{dev.max_per_node:>10}"
        f"{dev.fp32_tflops:>8.0f}T"
        f"{dev.fp64_tflops:>8.1f}T"
        f"{ratio_text:>11}"
        f"{dev.gres_name + ':1' + (f', {dev.feature}' if dev.feature else ''):>20}"
    )
print("-" * 96)
print("fp32 / fp64 are TFLOPS: trillions of floating point operations per second.")

print()
print("Reading this table")
print("-" * 96)
print("  A100 and H100 are 1:2 cards. They do double precision at half their")
print("  single precision rate, which is as good as it gets. If your software")
print("  needs fp64, these are your only sensible options.")
print()
print("  L4 and RTX PRO 6000 are around 1:60. The RTX PRO 6000 has the highest")
print("  fp32 number here by a wide margin and one of the worst fp64 numbers.")
print("  It is a superb card for machine learning and a poor one for a")
print("  quantum chemistry code - the same card, for the same money.")
print()
print("  The L4 is the small, low-power card. It is the right answer more often")
print("  than people expect: if your work fits in 24 GB and does not need")
print("  fp64, an L4 you can have now beats an A100 you have to queue for.")

print()
print("How to request each of them")
print("-" * 96)
for dev in rows:
    print(f"  #SBATCH --gpus-per-node {dev.gres_name}:1")
    if dev.feature:
        print(f"  #SBATCH --constraint    {dev.feature}      # the {dev.vram_gb} GB A100")
print()
print("  Both A100s are 'a100' to Slurm, and the constraint picks the size.")
print("  Without one, a100:1 can land on either.")
print()
print("  Ask for more than one only if your software says it can use more than")
print("  one. Most cannot, and a second idle GPU helps nobody.")
print()
