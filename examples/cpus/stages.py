"""Time the stages of a job, and say where the time went.

Wrap each stage of your program, then ask for the report:

    from stages import cpu_phase, gpu_phase, report

    for batch in batches:
        with cpu_phase("load and prepare"):
            data = prepare(batch)
        with gpu_phase("compute"):
            step(data)

    report()

Most people asking "why is my GPU only 30% utilised?" have never worked out
which parts of their program run on the GPU at all. This is how you find out,
and the answer is usually that the GPU is waiting: a job spending four seconds
reading and preparing data for every one second of computation leaves *any*
GPU idle 80% of the time, and a faster one changes nothing.
"""

from __future__ import annotations

import time
from contextlib import contextmanager

__all__ = ["cpu_phase", "gpu_phase", "report", "listeners"]

_seconds: dict[str, float] = {}
_kind: dict[str, str] = {}

# Anything that wants to know when a stage starts and ends: each is called with
# (kind, util) as a stage starts and (kind, 0) as it ends.
listeners: list = []


@contextmanager
def _phase(name: str, kind: str, util: float):
    for listener in listeners:
        listener(kind, util)
    start = time.monotonic()
    try:
        yield
    finally:
        _seconds[name] = _seconds.get(name, 0.0) + time.monotonic() - start
        _kind.setdefault(name, kind)
        for listener in listeners:
            listener(kind, 0)


def cpu_phase(name: str = "cpu"):
    """A stage of work done on the CPU, while the GPU waits."""
    return _phase(name, "CPU", 0)


def gpu_phase(name: str = "gpu", util: float = 95):
    """A stage of work done on the GPU. ``util`` is how busy it keeps the card."""
    return _phase(name, "GPU", util)


def report(speedup: float = 2.0) -> None:
    """Print where the time went, and what a faster GPU could do about it."""
    total = sum(_seconds.values())
    if total <= 0:
        print("No stages were recorded.")
        return

    print()
    print("Where the time went")
    print("-" * 46)
    for name, secs in _seconds.items():
        print(f"  {_kind[name]:<4} {name:<22}{secs:>7.1f}s{secs / total * 100:>7.1f}%")
    print(f"  {'':<4} {'':<22}{'-' * 8:>8}{'-' * 8:>8}")
    print(f"  {'':<4} {'total':<22}{total:>7.1f}s{100.0:>7.1f}%")

    gpu_time = sum(s for n, s in _seconds.items() if _kind[n] == "GPU")
    share = gpu_time / total * 100
    print()
    print(f"The GPU was busy for {share:.0f}% of this run.")

    # Amdahl, in the only form that matters to someone choosing a GPU: the
    # ceiling on what a faster card can do for you is set by the work that is
    # not on it.
    if gpu_time > 0:
        saved = gpu_time - gpu_time / speedup
        print(
            f"A GPU {speedup:g}x faster would cut {gpu_time:.1f}s to "
            f"{gpu_time / speedup:.1f}s, saving {saved / total * 100:.0f}% "
            f"of the total runtime."
        )
        if share < 50:
            print(
                "Most of this job is not on the GPU. Speeding up the part that "
                "is cannot help much - look at the CPU phases first."
            )
    print()
