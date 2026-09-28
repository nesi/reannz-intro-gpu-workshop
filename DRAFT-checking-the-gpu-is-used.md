# 7. Checking your job is using the GPU

!!! clipboard-list "Lesson Objectives"

    - Confirm Slurm gave your job a GPU
    - Confirm your software is using it, not just that it exists
    - Spot a job that has quietly fallen back to the CPU, and stop it happening

!!! clipboard-question "Questions"

    - How do I know my job actually got a GPU?
    - How do I know my program is using it and not the CPU?

## Three things can be true

Asking for a GPU and using a GPU are separate, and they fail separately:

| Slurm gave you a GPU? | Your software found it? | What you see | Where the fix is |
|---|---|---|---|
| No | — | `CUDA_VISIBLE_DEVICES` empty | One line of your Slurm script |
| Yes | No | **Nothing. The job just runs slowly** | Your software install |
| Yes | Yes | What you wanted | — |

The middle row is the dangerous one. **Most GPU-aware software does not stop
when it cannot find a GPU — it quietly carries on using the CPU.** Your job
runs, produces correct results, takes thirty times longer, and nothing in the
output says why.

This chapter is two checks, in the order they answer those questions.

## Check 1: did Slurm give you a GPU?

When Slurm allocates a GPU it sets `CUDA_VISIBLE_DEVICES`, listing the devices
you may use. Every GPU library on the node reads it. You never set it yourself,
but reading it is the fastest check there is:

```bash
echo "CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES}"
```

| Value | Means |
|---|---|
| `0` | One GPU, numbered 0 |
| `0,1` | Two |
| *empty* | **No GPUs were requested, so you have none** |
| not set | You are not inside a Slurm job |

If this is empty, stop here — the problem is your Slurm script, and nothing
downstream will fix it.

## Check 2: is your software using it?

This is the one that matters, and the one people skip.

| Software | How to ask |
|---|---|
| PyTorch | `python -c "import torch; print(torch.cuda.is_available())"` |
| TensorFlow | `python -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"` |
| GROMACS | `gmx mdrun` prints the GPUs it detected in the log header |
| Most others | The top of the program's own log. GPU-aware software almost always announces the device it picked |

!!! note "Is it even a GPU-capable build?"

    Software that *cannot* use a GPU is the most common reason a job that has
    one runs without it. For PyTorch, two values tell you:

    ```bash
    python -c "import torch; print(torch.__version__, torch.version.cuda)"
    ```

    | Output | Means |
    |---|---|
    | `2.14.0+cu124  12.4` | A CUDA build. It can use a GPU |
    | `2.14.0+cpu  None` | A CPU-only build. It never will, whatever Slurm gives it |

    A CPU-only build with a perfectly good GPU allocated is a software problem.
    No amount of fixing your Slurm script will help.

### Both at once

```bash
cd ~/gpu-training/07_checking_the_gpu
cat check_gpu.py        # worth reading; it is short
sbatch check-gpu.sl
```

```
1. What Slurm gave this job
---------------------------
  CUDA_VISIBLE_DEVICES = 0
  This job may use 1 GPU(s).
  CPUs allocated: 2
  RAM allocated:  2048 MB

2. What the driver reports (nvidia-smi)
---------------------------------------
  NVIDIA L4, 200 MiB

3. What your software reports (PyTorch)
---------------------------------------
  torch version:         2.14.0+cu124
  built against CUDA:    12.4
  torch.cuda.is_available(): True
  device count:          1
  device name:           NVIDIA L4
  compute capability:    8.9
  device memory (VRAM):  200 MB
  test calculation:      1000 (expected 1000)

  This job has a GPU and your software is using it.
```

The last line only appears after a real calculation has run on the device.
Checking a flag is weaker than doing the thing.

---

## Not running on the CPU by accident

Everything so far is a check you have to remember to run. The failure mode is
that you forget, and find out weeks later.

### The signs

| Sign | Where you would see it |
|---|---|
| `CUDA_VISIBLE_DEVICES` empty | Your job's output |
| `torch.cuda.is_available()` is `False` | Your own check |
| Your process missing from the GPU's process list | [`nvtop`](06-tools-for-measuring.md) |
| GPU at 0% while the CPU is pinned at 100% | `nvtop`, `seff` |
| `seff` shows **no GPU lines at all** | [Chapter 6](06-tools-for-measuring.md) |
| "falling back to CPU", "no CUDA device found" | Your software's own log — grep for it |
| The job simply takes far longer than you expected | You, eventually |

!!! note "Grep your logs"

    Software that falls back usually says so somewhere, quietly, once, near the
    start:

    ```bash
    grep -iE "cuda|gpu|fall.?back|device" my-job-1234.out | head -20
    ```

    Worth doing once for any new package. You only need to find the line it
    prints on success to know what to look for on failure.

### Make the job fail instead

The reliable fix is not to check harder. It is to make a job that has no GPU
**stop**, rather than spend two days quietly on the CPU:

```bash title="at the top of your job script"
python3 -c "import torch, sys; sys.exit(0 if torch.cuda.is_available() else 1)" \
    || { echo "ERROR: no GPU visible - refusing to run on the CPU" >&2; exit 1; }
```

Two lines. A job that was going to waste a day of your allocation now fails in
four seconds and tells you why.

The same idea without Python, for software that is not PyTorch:

```bash
[ -n "${CUDA_VISIBLE_DEVICES}" ] || { echo "ERROR: no GPU allocated" >&2; exit 1; }
```

!!! note "And record what you saw"

    Even when it works, leave the evidence in the output file:

    ```bash
    echo "CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES}"
    python3 -c "import torch; print(torch.cuda.get_device_name(0))"
    ```

    When you come back to a result in six months and wonder whether that run
    used the GPU, this is the difference between knowing and guessing.

!!! warning "In this training environment"

    One check does **not** work here: `tensor.device` reports `cpu`, because
    the emulator keeps tensors in host memory and does the arithmetic on the
    CPU. On real hardware it would report `cuda:0`.

    Use `torch.cuda.memory_allocated()` instead — that is accounted correctly
    — or watch the job with [`nvtop`](06-tools-for-measuring.md), which will
    show your process holding memory.

!!! dumbbell "Exercise: cause it, then catch it"

    1. Run `sbatch check-gpu.sl` and confirm all three sections agree.
    2. Edit `check-gpu.sl` and comment out the GPU line with a second `#`:
       ```bash
       ##SBATCH --gpus-per-node l4:1
       ```
    3. Submit it again and compare the two outputs.
    4. Now add the fail-fast guard above to the script, and submit once more.

    ??? "What you should see at step 3"

        ```
        1. What Slurm gave this job
        ---------------------------
          CUDA_VISIBLE_DEVICES is set but EMPTY.
          This job asked for no GPUs, so it has none. Add to your script:
              #SBATCH --gpus-per-node l4:1

        2. What the driver reports (nvidia-smi)
        ---------------------------------------
          nvidia-smi found no GPU for this job.

        3. What your software reports (PyTorch)
        ---------------------------------------
          torch version:         2.14.0+cu124
          built against CUDA:    12.4
          torch.cuda.is_available(): False

          PyTorch found no GPU because this job was not given one.
          This is a Slurm problem, not a software problem. Add:
              #SBATCH --gpus-per-node l4:1
        ```

        Note what section 3 does **not** say. PyTorch is still a CUDA build —
        `+cu124` — it simply has no device. Nothing is wrong with the software.

        Had the version said `+cpu` and `built against CUDA: None` while
        section 1 showed a GPU, the diagnosis would be the opposite, and the
        fix would have nothing to do with Slurm.

    ??? "What you should see at step 4"

        ```
        ERROR: no GPU visible - refusing to run on the CPU
        ```

        The job stops in seconds instead of running to completion on the CPU.
        This is the version you want in your real job scripts.

    **Undo your edit** before moving on.

!!! graduation-cap "Keypoints"

    - `CUDA_VISIBLE_DEVICES` empty means Slurm gave you nothing. Fix the script.
    - **Never judge how busy a GPU is from a single instantaneous reading.**
      Watch it over time with `nvtop`, or read `seff` afterwards — both are in
      [chapter 6](06-tools-for-measuring.md).
    - Ask your *software*, not just the driver. A job can have a perfect GPU
      sitting idle beside it.
    - `+cpu` and `version.cuda None` mean a build that can never use a GPU.
    - **Make the job fail** when there is no GPU, rather than letting it run on
      the CPU for two days.
