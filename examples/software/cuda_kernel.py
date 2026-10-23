#!/usr/bin/env python3
"""Two real CUDA kernels, written in Python with Numba.

Run it in a GPU job, with Numba installed, and the kernels run on the card:
one thread per element for a vector add, then a reduction that shares memory
between the threads of a block.

Numba also ships a CUDA simulator, switched on with NUMBA_ENABLE_CUDASIM=1, that
runs the same kernels in the Python interpreter. It is slow, and completely
faithful to the programming model - ``threadIdx``, ``blockIdx``, shared memory,
``syncthreads`` and race conditions all behave as they do on hardware.
"""

from __future__ import annotations

import numpy as np
from numba import config, cuda


@cuda.jit
def vector_add(a, b, out):
    """One thread per element, the canonical first CUDA kernel."""
    i = cuda.grid(1)
    if i < out.size:  # guard: the grid is usually larger than the data
        out[i] = a[i] + b[i]


@cuda.jit
def row_sums_shared(matrix, out):
    """Sum each row with a shared-memory reduction.

    Deliberately written the way a workshop would teach it, so the
    ``syncthreads`` calls are load-bearing. Remove either one and the answers
    go wrong - which is the point of running it.
    """
    row = cuda.blockIdx.x
    tid = cuda.threadIdx.x
    block = cuda.blockDim.x

    partial = cuda.shared.array(shape=128, dtype=np.float32)

    total = np.float32(0.0)
    for col in range(tid, matrix.shape[1], block):
        total += matrix[row, col]
    partial[tid] = total
    cuda.syncthreads()

    stride = block // 2
    while stride > 0:
        if tid < stride:
            partial[tid] += partial[tid + stride]
        cuda.syncthreads()
        stride //= 2

    if tid == 0:
        out[row] = partial[0]


def main() -> int:
    print(f"CUDA available to numba: {cuda.is_available()}")
    if config.ENABLE_CUDASIM:
        print("(running under Numba's CUDA simulator)")
    print()

    # -- vector add ---------------------------------------------------
    n = 1024
    a = np.arange(n, dtype=np.float32)
    b = np.arange(n, dtype=np.float32) * 2

    d_a = cuda.to_device(a)
    d_b = cuda.to_device(b)
    d_out = cuda.device_array_like(a)

    threads_per_block = 128
    blocks = (n + threads_per_block - 1) // threads_per_block
    vector_add[blocks, threads_per_block](d_a, d_b, d_out)

    out = d_out.copy_to_host()
    assert np.allclose(out, a + b), "vector_add disagreed with numpy"
    print(f"vector_add: {blocks} blocks x {threads_per_block} threads -> correct")

    # -- shared-memory reduction --------------------------------------
    rows, cols = 16, 500
    matrix = np.random.default_rng(0).random((rows, cols), dtype=np.float32)
    d_matrix = cuda.to_device(matrix)
    d_sums = cuda.device_array(rows, dtype=np.float32)

    row_sums_shared[rows, threads_per_block](d_matrix, d_sums)
    sums = d_sums.copy_to_host()

    expected = matrix.sum(axis=1)
    assert np.allclose(sums, expected, rtol=1e-4), "reduction disagreed with numpy"
    print(f"row_sums_shared: {rows} blocks, shared-memory reduction -> correct")

    print("\nTry breaking it: delete one of the syncthreads() calls in")
    print("row_sums_shared and run again. A GPU and the simulator give the")
    print("same wrong answers, for the same reason.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
