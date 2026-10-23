#!/usr/bin/env python3
"""A job that died with "CUDA out of memory" - the second of two.

crash_one.py died with the same error. Run each of them inside your
interactive session, with nvtop open in a second terminal, and watch what GPU
memory does on the way to the error. They are not the same problem, and what
would fix one of them would do nothing for the other.

    python3 crash_two.py

Like most real jobs, it reports its progress and not its memory. Watching the
memory is what nvtop is for.
"""

import argparse
import sys
import time

import torch

parser = argparse.ArgumentParser(
    description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
)
parser.add_argument("--steps", type=int, default=40, help="how many batches to work through")
args = parser.parse_args()

if not torch.cuda.is_available():
    raise SystemExit(
        "No GPU visible to this process. Are you inside your job?\n"
        "Run 'svisit <JOBID>' first, then try again."
    )

# Every size is a fraction of the card, so the job behaves the same on the
# training environment's 200 MB cards as it would on a real 24 GB L4.
card = torch.cuda.get_device_properties(0).total_memory
layers = 10
width = int((card * 0.12 / 4) ** 0.5)      # each layer about an eighth of the card
rows = int(card * 0.05 / 4 / width)        # each batch a twentieth of it

try:
    model = []
    for layer in range(1, layers + 1):
        print(f"Loading the model: layer {layer} of {layers}")
        model.append(torch.randn(width, width, device="cuda"))
        time.sleep(1)                       # slow enough to watch

    for step in range(1, args.steps + 1):
        batch = torch.randn(rows, width, device="cuda")
        for weights in model:
            batch = batch @ weights
        print(f"step {step:>3} of {args.steps}: done")
        time.sleep(1)
except torch.cuda.OutOfMemoryError as exc:
    # What a crashed job leaves at the bottom of its output file.
    sys.exit(f"\ntorch.OutOfMemoryError: {exc}")

print(f"\nFinished all {args.steps} steps.")
