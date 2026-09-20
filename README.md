# Introduction to Using GPUs on High Performance Clusters (HPC)

Workshop material for **REANNZ's "Introduction to Using GPUs"**. It teaches
researchers how to choose, request and monitor GPUs on an HPC such as
[Mahuika](https://docs.nesi.org.nz/) — not how to program them.

📖 **Read the workshop here: <https://nesi.github.io/reannz-intro-gpu-workshop/>**

The material is a single track of nine chapters built around one question —
*which GPU should I use for my work?* — which the workshop opens with and can
only answer at the end, once a learner can measure the four things it depends
on. The pages live in [`docs/`](docs/).

## Who this is for

Researchers who have software that runs on a GPU, or think it might, and need
to work out which one to ask for and whether it helped. No CUDA, no C++, no
prior GPU experience. Everything is done from a terminal.

## Workshop structure

| Chapter | Covers |
|---|---|
| What a GPU is, and when it helps | Why some work suits a GPU and most does not |
| **Getting a GPU job running** | |
| 1. Requesting a GPU | The Slurm flags, and what each one asks for |
| 2. Did I get a GPU? | Checking, and the limits of `nvidia-smi` |
| **Is it doing any work?** | |
| 3. Watching a job with nvtop | `svisit`, and reading utilisation over time |
| 4. Reading seff | The report card, and the two GPU lines |
| **Asking for the right resources** | |
| 5. RAM and VRAM | Two separate pools; sizing each; reading an OOM error |
| 6. How many CPUs? | Measuring the point where more cores stop helping |
| 7. Splitting CPU and GPU work | Which stages a GPU can help with, and the ceiling |
| **Choosing your hardware** | |
| 8. Precision | fp32 vs fp64, and why it decides the card |
| 9. Choosing a GPU | The four measurements, combined into a request |

Plus a [summary and checklist](docs/summarising.md), a [command
reference](docs/R1-command-reference.md), a [GPU
reference](docs/R2-gpu-reference.md) and a [setup page for
trainers](docs/setup-gpu-workshop.md).

## Repository layout

| Path | Contents |
|------|----------|
| [`docs/`](docs/) | The lesson pages (Markdown), images and stylesheets |
| [`examples/`](examples/) | The scripts and Slurm job files used in the lessons, grouped by chapter |
| [`mkdocs.yml`](mkdocs.yml) | The MkDocs site configuration and navigation |
| [`overrides/`](overrides/) | Theme overrides |

## The training environment

The workshop runs in the [GPU JupyterLab
app](https://github.com/nesi/training-environment-jupyter-gpu-app) on the
[REANNZ training environment](https://github.com/nesi/training-environment).

**That environment has no GPUs.** It emulates one, closely enough that
`nvidia-smi`, `nvtop`, `seff`, `sbatch` and PyTorch's CUDA API all behave the
way they do on the cluster — real utilisation, real device memory, real job
accounting, real out-of-memory errors. The arithmetic runs on the CPU.

**No timing measured in that environment means anything about GPU
performance**, and nothing in this workshop asks anyone to time anything.
Reading the tools is the skill being taught, and it transfers unchanged.

To try it without deploying anything, with Docker:

```bash
git clone https://github.com/nesi/training-environment-jupyter-gpu-app.git
cd training-environment-jupyter-gpu-app
./run-local.sh
```

See [the setup page](docs/setup-gpu-workshop.md) for deployment, session
sizing and suggested timings.

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
