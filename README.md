# Introduction to Using GPUs on High Performance Clusters (HPC)

Workshop material for **REANNZ's "Introduction to Using GPUs"**. It teaches
researchers how to choose, request and monitor GPUs on an HPC such as
[Mahuika](https://docs.nesi.org.nz/) — not how to program them.

📖 **Read the workshop here: <https://nesi.github.io/reannz-intro-gpu-workshop/>**

The material is ten chapters in five stages, built around one question —
*which GPU should I use for my work?* — which the workshop opens with and can
only answer at the end, once a learner can measure what it depends on. It is
sized for a single four-hour session. The pages live in [`docs/`](docs/).

It assumes most of the audience has run a Slurm job before, so the opening
moves quickly. What a GPU is good for comes first, briefly, for anyone meeting
GPUs for the first time.

## Who this is for

Researchers who have software that runs on a GPU, or think it might, and need
to work out which one to ask for and whether it helped. No CUDA, no C++, no
prior GPU experience. Everything is done from a terminal.

## Workshop structure

| Stage | Chapters |
|---|---|
| 1. Getting started with GPUs | [Introduction](docs/introduction.md) · [Your first GPU job](docs/first-gpu-job.md) · [Is it really using the GPU?](docs/using-the-gpu.md) |
| 2. Asking for the right resources | [Which GPU: precision](docs/precision.md) · [Which GPU: will it fit?](docs/gpu-memory.md) · [How many CPUs](docs/how-many-cpus.md) · [How much CPU memory](docs/cpu-memory.md) |
| 3. Measuring your GPU jobs | [Measuring a GPU job](docs/measuring.md) |
| 4. Running interactive jobs | [Running interactive sessions with GPUs](docs/interactive-sessions.md) |
| 5. Putting it all together | [Putting it all together](docs/putting-it-together.md) · [Summary and checklist](docs/summarising.md) |

**Beyond the basics**, for after the workshop, when a learner sets up their
own work:

| | |
|---|---|
| [B1: Getting your software running on a GPU](docs/software.md) | Modules, Python environments, containers, and builds too old for the card |
| [B2: Where the time goes](docs/where-the-time-goes.md) | Measuring the CPU and GPU parts of a job, and reading data quickly |
| [B3: Long jobs](docs/long-jobs.md) | Time limits, checkpoints, and why a job is pending |
| [B4: More than one GPU, and less than one](docs/more-than-one-gpu.md) | When a second GPU helps, and what to do with small jobs |

**Reference:** [commands](docs/R1-command-reference.md) and [the GPUs on this
cluster](docs/R2-gpu-reference.md).

## Repository layout

| Path | Contents |
|------|----------|
| [`docs/`](docs/) | The lesson pages (Markdown), images and stylesheets |
| [`examples/`](examples/) | The scripts and Slurm job files used in the lessons, one folder per topic |
| [`mkdocs.yml`](mkdocs.yml) | The MkDocs site configuration and navigation |
| [`overrides/`](overrides/) | Theme overrides |

## Teaching it

The pages are written for Mahuika: every command, script and output on them is
what a learner would type and see there.

The workshop is taught in the [GPU JupyterLab app](https://github.com/nesi/training-environment-jupyter-gpu-app) on the
[REANNZ training environment](https://github.com/nesi/training-environment),
which emulates Mahuika's GPUs on infrastructure that has none. The trainers'
guide, `TEACHING.md` in that repository, covers deployment, session sizing,
timings, and where a session differs from the pages.

To try it without deploying anything, with Docker:

```bash
git clone https://github.com/nesi/training-environment-jupyter-gpu-app.git
cd training-environment-jupyter-gpu-app
./run-local.sh
```

## Building the site locally

```bash
pip install -r requirements.txt
mkdocs serve
```

## A note on `examples/`

[`examples/`](examples/) mirrors `docker/workshop/` in the app repository,
which is what actually ships inside the session image. If you change an
exercise, change it in both places — otherwise the page a learner reads will
not match the file in front of them.

## License

This workshop material is licensed under the [GNU General Public License
v3.0](https://www.gnu.org/licenses/gpl-3.0.en.html).

It draws on the [NeSI support
documentation](https://docs.nesi.org.nz/Batch_Computing/Using_GPUs/) for GPU
usage and hardware, and documents `seff` and `svisit` as implemented in
[nesi/opt-nesi-bin](https://github.com/nesi/opt-nesi-bin).
