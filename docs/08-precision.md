# 8. Precision

!!! clipboard-list "Lesson Objectives"

    - Explain what single and double precision mean
    - Find out which one your software needs
    - Explain why that decides which GPU you should ask for

!!! clipboard-question "Questions"

    - What is fp32 and fp64, and why does everyone go on about them?
    - Why is one GPU thirty times slower than another at the same calculation?

## Precision is how many digits you keep

A computer stores a number in a fixed number of bits, so most real numbers are
stored slightly wrong. How wrong depends on the format:

| Format | Also called | Bits | Significant digits | Bytes |
|---|---|---|---|---|
| `float64` | double precision, fp64 | 64 | ~16 | 8 |
| `float32` | single precision, fp32 | 32 | ~7 | 4 |
| `float16` | half precision, fp16 | 16 | ~3 | 2 |
| `bfloat16` | brain float | 16 | ~3 (wider range) | 2 |

Fewer digits means less memory, less data to move, and faster arithmetic. It
also means less accuracy, and for some kinds of calculation that is fatal.

## Why it decides the GPU

Every GPU can do all of these. What differs — enormously — is how *fast*.

GPUs are built out of hardware that does single-precision arithmetic. Double
precision is either properly supported in hardware or largely bolted on, and
manufacturers choose which depending on the market a card is for.

| GPU | fp32 | fp64 | Ratio |
|---|---|---|---|
| NVIDIA A100 | 19.5 TFLOPS | 9.7 TFLOPS | **1:2** |
| NVIDIA H100 NVL | 60 TFLOPS | 30 TFLOPS | **1:2** |
| NVIDIA L4 | 30.3 TFLOPS | 0.5 TFLOPS | **1:62** |
| NVIDIA RTX PRO 6000 | 120 TFLOPS | 1.9 TFLOPS | **1:63** |

```bash
cd ~/gpu-training/08_precision
python3 show_fleet.py
```

Look at the RTX PRO 6000 row. It has by far the highest single-precision number
in the fleet — four times an A100 — and nearly the worst double-precision
number. It is a superb card for machine learning and a poor one for a quantum
chemistry code. **Same card, same cost.**

!!! warning "A factor of 60 is not a detail"

    An eight-hour fp64 job on an A100 would take roughly two weeks on an L4.

    This is the single biggest way to pick the wrong GPU, and it is invisible:
    the job runs, produces correct answers, and is just inexplicably slow.
    There is no error message for "you put a double-precision workload on a
    consumer-lineage card".

!!! note "The cluster documentation puts it plainly"

    > The L4 and RTX PRO 6000 should be avoided for double precision floating
    > point (fp64) work.

    — [Using GPUs](https://docs.nesi.org.nz/Batch_Computing/Using_GPUs/)

## Why some work needs fp64

Run:

```bash
python3 accuracy.py
```

It demonstrates three things, with arithmetic you can check.

**Errors accumulate.** Add up a million numbers in fp32 and in fp64 and the
totals differ. Each individual addition is only slightly wrong, there are a
million of them, and the errors do not cancel out.

```
   float64 total: 50015925.646368
   float32 total: 50015924.000000
   difference:    1.646368
```

**Subtracting nearly equal numbers destroys precision.**

```
   (1.0000001 - 1.0)
   float64: 1.0000000005e-07
   float32: 1.1920928955e-07
   correct: 1.0000000000e-07
```

fp32 does not have enough digits to tell those two numbers apart properly.
Iterative solvers do this millions of times.

**Some problems amplify any error at all.**

```
   worst error, float64: 1.14e-04
   worst error, float32: 6.35e+02
```

The correct answer is all ones. In fp32 it is wrong by more than the answer
itself. No amount of extra compute fixes this — only more precision does.

## Which does your software need?

This is a property of your software and your problem. You do not get to choose
it freely.

**Usually needs fp64**

- Molecular dynamics over long trajectories
- Quantum chemistry (VASP, Gaussian, CP2K, Quantum ESPRESSO)
- Computational fluid dynamics
- Climate and ocean models
- Iterative linear solvers, eigenvalue problems
- Anything where small errors compound over millions of steps

**Usually fine in fp32**

- Machine learning, training and inference
- Image and signal processing
- Most Monte Carlo work
- Visualisation and rendering

**Often fine in fp16 or bfloat16**

- Neural network training with mixed precision, and inference. This is what the
  newest cards are optimised for, and where their headline numbers come from.

### How to find out, without guessing

1. **Read the documentation.** Software that needs fp64 says so, often
   insistently.
2. **Look for a precision setting.** Many packages ship both single and double
   builds — GROMACS has `gmx` and `gmx_d`, and the difference is exactly this.
3. **Check for a mixed-precision option.** Many machine-learning frameworks can
   use fp16 for most work and fp32 where it matters, which roughly halves
   memory and is usually safe. In PyTorch that is `torch.autocast`.
4. **If you are using machine-learning libraries**, you are already in fp32 or
   fp16 unless you went out of your way not to be.
5. **Ask the support desk.** They will have seen your package before.

!!! dumbbell "Exercise: classify your own work"

    1. Run `python3 show_fleet.py` and find the two cards you should avoid for
       double precision.
    2. For your own software: does it need fp64? Where did you find that out?
    3. Given your answer, which GPUs are you choosing between?

    ??? "If you are not sure"

        Two things you can do:

        - Run the same short job in both precisions, if your software supports
          both, and compare the results. If they agree to the precision you
          care about, you can use the faster one.
        - Run a short job on an L4 and the same one on an A100, and compare
          the runtime. If the L4 is dramatically slower for no obvious reason,
          you are doing fp64 work.

!!! note "Mixed precision is worth knowing about"

    If your work is fp32 today and you are short of memory or time, mixed
    precision keeps the sensitive parts in fp32 and does the rest in fp16. For
    neural networks this is standard practice, roughly halves memory use, and
    usually needs one or two lines of code.

    It is not appropriate for fp64 scientific codes — those need *more*
    precision, not less.

!!! graduation-cap "Keypoints"

    - Precision is how many digits you keep: fp64 ~16, fp32 ~7, fp16 ~3.
    - **A100 and H100 do fp64 at 1:2. L4 and RTX PRO 6000 at about 1:60.**
    - Choosing the wrong one makes your job up to sixty times slower, with no
      error message.
    - Whether you need fp64 is a property of your software. Look it up.
    - Simulation of physical systems usually needs fp64. Machine learning
      almost never does.
