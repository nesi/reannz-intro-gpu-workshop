#!/usr/bin/env python3
"""A job that died with "CUDA out of memory" - the first of two.

crash_two.py died with the same error. Run each of them inside your
interactive session, with nvtop open in a second terminal, and watch what GPU
memory does on the way to the error. They are not the same problem, and what
would fix one of them would do nothing for the other.

    python3 crash_one.py
    python3 crash_one.py --steps 5      # the same job, as a short test

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

# Every size is a fraction of the card, so the job behaves the same way on
# any GPU.
card = torch.cuda.get_device_properties(0).total_memory
width = int((card * 0.10 / 4) ** 0.5)      # a model a tenth of the card
rows = int(card * 0.05 / 4 / width)        # each batch a twentieth of it

try:
    print("Loading the model...")
    weights = torch.randn(width, width, device="cuda")
    time.sleep(2)

    finished = []
    for step in range(1, args.steps + 1):
        batch = torch.randn(rows, width, device="cuda")
        result = batch @ weights
        finished.append(batch)              # kept, for a summary at the end
        print(f"step {step:>3} of {args.steps}: done")
        time.sleep(1)                       # slow enough to watch
except torch.cuda.OutOfMemoryError as exc:
    # What a crashed job leaves at the bottom of its output file.
    sys.exit(f"\ntorch.OutOfMemoryError: {exc}")

print(f"\nFinished all {args.steps} steps.")
