# 2. Did I get a GPU?

!!! clipboard-list "Lesson Objectives"

    - Use `nvidia-smi` for the one job it does well
    - Explain why `nvidia-smi` is a poor way to check whether a job is *using*
      the GPU
    - Tell the difference between "Slurm gave me no GPU" and "my software
      ignored the GPU I was given"

!!! clipboard-question "Questions"

    - How do I know my job actually got a GPU?
    - How do I know my software is using it?

## `nvidia-smi` answers exactly one question

`nvidia-smi` is the NVIDIA System Management Interface. It asks the driver what
GPUs are present and what they are doing *at this instant*, and prints a table.

It is the right tool for:

> **"Is there a GPU here that I am allowed to use?"**

It is the wrong tool for almost everything else people use it for, and the
reason is in the phrase *at this instant*.

!!! warning "nvidia-smi is a snapshot, not a monitor"

    When you run `nvidia-smi` inside a job, you get one reading, taken in the
    fraction of a second the command was running.

    A training loop that alternates between loading data and computing might
    spend 70% of its time waiting on the CPU. Run `nvidia-smi` once and you
    have a 70% chance of catching it during a pause and concluding the GPU is
    idle, and a 30% chance of catching it mid-calculation and concluding
    everything is fine. **Neither conclusion is justified by one sample.**

    People do this constantly: they run `nvidia-smi` in a job, see `0%`,
    panic — or see `100%`, relax — and both times they have learned nothing.

    For "is it busy?" use `nvtop` (chapter 3) while it runs, or `seff`
    (chapter 4) after it finishes. Both sample over time. `nvidia-smi` does
    not.

## Reading the table

```
+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 550.54.15              Driver Version: 550.54.15      CUDA Version: 12.4     |
|-----------------------------------------+------------------------+----------------------+
| GPU  Name                 Persistence-M | Bus-Id          Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |           Memory-Usage | GPU-Util  Compute M. |
|=========================================+========================+======================|
|   0  NVIDIA L4                      On  |   00000000:00:04.0 Off |                    0 |
| N/A   38C    P8             12W /  72W  |       1MiB /   1024MiB |      0%      Default |
+-----------------------------------------+------------------------+----------------------+
```

The parts worth knowing:

| Field | Meaning |
|---|---|
| `0` | The device number. This is what `CUDA_VISIBLE_DEVICES` refers to |
| `NVIDIA L4` | Which card you got. **Check this is what you asked for** |
| `38C` | Temperature |
| `12W / 72W` | Power draw now, and the card's limit. A good proxy for how hard it is working |
| `1MiB / 1024MiB` | GPU memory used / total. This is VRAM (chapter 5) |
| `0%` | Utilisation, **right now, for an instant** |

Below the table is a process list showing which processes hold GPU memory. If
your job is running and your process is not in that list, your software is not
using the GPU.

!!! note "What `GPU-Util` actually measures"

    It is the percentage of the last sampling period during which *at least one*
    calculation was running on the card. It is not how much of the card is
    being used.

    A job using a single one of the L4's 60 processing blocks, badly, for the
    whole period reports 100%. This is why "my utilisation is 100%" is not
    proof that anything is going well — it only means the GPU was never
    completely idle.

## Ask your software, not just the driver

The driver reporting a GPU does not mean your program found it. These are two
separate things and they fail separately:

| Slurm gave you a GPU? | Your software found it? | Symptom |
|---|---|---|
| No | — | `CUDA_VISIBLE_DEVICES` empty, `nvidia-smi` finds nothing |
| Yes | No | Everything looks fine. Job runs slowly on the CPU |
| Yes | Yes | What you wanted |

The middle row is the dangerous one. Causes include a CPU-only build of the
software, a module not loaded, a GPU feature not switched on in a config file,
or a library version mismatch.

So check both. There is a script for it:

```bash
cd ~/gpu-training/02_did_i_get_a_gpu
cat check_gpu.py
```

It prints three sections: what Slurm gave the job, what the driver reports, and
what PyTorch reports. Run it inside a job:

```bash
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
  NVIDIA L4, 1024 MiB

3. What your software reports (PyTorch)
---------------------------------------
  torch version:         2.14.0+cpu
  torch.cuda.is_available(): True
  device count:          1
  device name:           NVIDIA L4
  compute capability:    8.9
  device memory (VRAM):  1.0 GB
  test calculation:      1000 (expected 1000)

  This job has a GPU and your software is using it.
```

Section 3 is the one that matters. The equivalent for other software:

| Software | How to ask |
|---|---|
| PyTorch | `python -c "import torch; print(torch.cuda.is_available())"` |
| TensorFlow | `python -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"` |
| GROMACS | `gmx mdrun` prints the GPUs it detected in the log header |
| Most others | Look at the top of the program's own log. GPU-aware software almost always announces which device it picked |

!!! dumbbell "Exercise: catch the failure"

    1. Run `sbatch check-gpu.sl` and read the output.
    2. Now edit `check-gpu.sl` and comment out the `--gpus-per-node` line by
       putting a second `#` in front of it:
       ```bash
       ##SBATCH --gpus-per-node l4:1
       ```
    3. Submit it again and compare.

    ??? "What you should see"

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
          torch.cuda.is_available(): False
        ```

        All three agree, which tells you the problem is the Slurm request.

        Had section 1 shown a GPU while section 3 said `False`, the problem
        would be the software instead — and the fix would be completely
        different. That is why the script prints all three.

    4. **Undo your edit** before moving on.

!!! note "Put this in your own jobs"

    Four lines at the top of a job script that print what the job can see cost
    nothing and are in the output file forever:

    ```bash
    echo "CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES}"
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
    ```

    When you come back to a result in six months and wonder whether that run
    used the GPU, this is the difference between knowing and guessing.

!!! graduation-cap "Keypoints"

    - `nvidia-smi` is for **"is there a GPU I can use?"** — and it is good at that.
    - It is a **snapshot**. Never conclude a job is or is not busy from one
      reading of it.
    - `GPU-Util` is "was anything running?", not "how much of the card is in
      use?".
    - Check the driver **and** your software. A job can have a perfect GPU
      sitting idle beside it.
    - Print what the job can see, at the top of every GPU job.
