# B2: Where the time goes

!!! circle-info "Beyond the basics"

    Not covered in the live workshop. It is the next step when `seff` shows
    GPU utilisation lower than you would like, and more CPUs did not fix it.

    The scripts are in `~/gpu-training/where-the-time-goes/`, and also
    [on GitHub](https://github.com/nesi/reannz-intro-gpu-workshop/tree/main/examples/where-the-time-goes){: target="_blank" rel="noopener" }.

!!! clipboard-list "Lesson Objectives"

    - Measure what fraction of your runtime a GPU could affect
    - Recognise when storage, not the GPU, is holding a job up
    - Know where on Mahuika to keep data, and how to read it quickly

!!! clipboard-question "Questions"

    - My GPU utilisation is low, and more cores did not help. What now?
    - Where should my data live?

[The introduction](introduction.md) set out the ceiling: the work that is not
on the GPU limits what any GPU can do for your job. This page is about
measuring that split for your own job, and about the most common thing on the
CPU side of it — reading data.

## Measure your own stages

```bash
cd ~/gpu-training/where-the-time-goes
sbatch phases.sl
```

The job runs a workload in four stages, twice, and reports where the time
went. The first run, in `phases-<JobID>.out`, is reasonably balanced:

```
Where the time went
----------------------------------------------
  CPU  1. read input             3.0s   30.9%
  CPU  2. prepare                0.2s    2.0%
  GPU  3. compute                5.1s   51.6%
  CPU  4. write output           1.5s   15.5%
                             ----------------
       total                     9.8s  100.0%

The GPU was busy for 52% of this run.
A GPU 2x faster would cut 5.1s to 2.5s, saving 26% of the total runtime.
```

The second is the same computation, reading and writing much more
(`profile_phases.py --heavy-io`):

```
Where the time went
----------------------------------------------
  CPU  1. read input             6.0s   42.0%
  CPU  2. prepare                0.2s    1.6%
  GPU  3. compute                5.1s   35.3%
  CPU  4. write output           3.0s   21.1%
                             ----------------
       total                    14.3s  100.0%

The GPU was busy for 35% of this run.
A GPU 2x faster would cut 5.1s to 2.5s, saving 18% of the total runtime.
Most of this job is not on the GPU. Speeding up the part that is cannot
help much - look at the CPU phases first.
```

Nearly two thirds of the runtime is now reading and writing, and no GPU on
earth will do anything about it.

Run `seff <JobID>` afterwards, to compare the script's own figures with what
`seff` measures from outside.

## Timing your own code

You do not need any special tools. Put timers around the stages:

```python
import time

t0 = time.time()
data = load_and_prepare(path)
t1 = time.time()
result = model(data)            # the GPU part
t2 = time.time()
save(result, out)
t3 = time.time()

print(f"load    {t1-t0:6.1f}s")
print(f"compute {t2-t1:6.1f}s")
print(f"save    {t3-t2:6.1f}s")
```

Ten lines, once, and you will know more about your job than most people know
about theirs. For non-Python software, the same thing:

```bash
/usr/bin/time -v ./preprocess.sh
/usr/bin/time -v ./simulate.sh
```

## What to do with the answer

**If the GPU stage dominates (say over 70%)**

The GPU is the bottleneck. This is the one case where a faster or larger GPU is
the right answer — climb the ladder in
[Which GPU: will it fit?](gpu-memory.md).

**If preparation dominates**

- Parallelise it across more cores ([How many CPUs](how-many-cpus.md)).
- Do the preparation once and cache the result, if it is the same every run.
  People re-decode the same dataset every epoch for months.
- Consider moving that stage onto the GPU too, if it is arithmetic rather than
  parsing.

**If reading and writing dominate**

You are limited by storage. The rest of this page is about that.

## Data and storage

### Where your data lives

| Filesystem | For | Watch out for |
|---|---|---|
| `/home` | Configuration, source code, small environments | 20 GB, and not for running jobs from |
| `/nesi/project` | Data and software you keep and use regularly, including large environments | Your project's quota |
| `/nesi/nobackup` | Data your jobs read and write | Not backed up; files untouched for 90 days are deleted |

`storage_quota` shows how much of each you are using. The details are on
[Filesystems and quotas](https://docs.nesi.org.nz/Storage/Filesystems_and_Quotas/).

### Many small files are slow

A shared filesystem handles a few large files far better than many small ones.
A dataset of a million small images — the usual shape of a machine learning
dataset — is about the slowest thing you can ask of it, because every file
costs a lookup before a single byte is read.

Pack them into fewer, larger files: a `tar` archive, or a format such as HDF5
that holds many records in one file. Most machine learning frameworks can read
a dataset straight out of formats like these.

### Copy it to the node first

If a job reads the same data over and over — every epoch, say — copy it to
the node at the start of the job and read it from there. On Mahuika, every job
already has its own temporary directory, `$TMPDIR`:

- **By default, `$TMPDIR` is in RAM.** It is fast, but everything you copy
  there counts against your `--mem`
  ([How much CPU memory should I request?](cpu-memory.md)).
- **`#SBATCH --gres=ssd` gives the job a local 1.5 TB NVMe SSD instead**, and
  points `$TMPDIR` at it. The GPU nodes have them. It does not count against
  your memory, but only one job on a node can have it at a time.

```bash
tar -xf /nesi/nobackup/<project>/dataset.tar -C "$TMPDIR"
python3 train.py --data "$TMPDIR/dataset"
```

Either way, the directory is deleted when the job ends, so copy anything you
want to keep back out first. The
[Temporary directories](https://docs.nesi.org.nz/Batch_Computing/Temporary_Directories/)
page has the details.

!!! note "Overlapping is often the biggest win available"

    The stages above take turns. They do not have to. If batch N+1 is read and
    prepared while batch N is computing, the waiting disappears:

    ```
    taking turns:  [prep 1][gpu 1][prep 2][gpu 2][prep 3][gpu 3]
    overlapped:    [prep 1][prep 2][prep 3]
                          [gpu 1][gpu 2][gpu 3]
    ```

    This is what `num_workers` in a PyTorch `DataLoader`, or `prefetch` in a
    TensorFlow dataset, actually does — and it costs one argument. It is the
    background preparation from [How many CPUs](how-many-cpus.md).

!!! dumbbell "Exercise: your own workflow"

    On paper, break your own work into stages and answer, for each:

    | Stage | What it does | CPU or GPU? | Roughly what fraction of runtime? |
    |---|---|---|---|

    Then:

    1. What fraction of your runtime could a GPU possibly affect?
    2. If a GPU twice as fast were free tomorrow, how much would your job speed
       up?
    3. Is there a stage where a day of your time would save more than a better
       GPU would?

    For most real workflows the honest answer to 3 is yes, and it is usually
    the loading stage.

!!! graduation-cap "Keypoints"

    - **Time your stages before you ask for better hardware.** Ten lines.
    - If preparation dominates, add cores or cache the result. If storage
      dominates, fix the storage — a better GPU changes nothing.
    - Keep job data in **`/nesi/nobackup`**, and pack **many small files** into
      a few large ones.
    - **`$TMPDIR` is in RAM** unless you ask for `--gres=ssd`. Data you copy
      there counts against `--mem`.
    - Overlapping preparation with computation is often the cheapest large win
      available.
