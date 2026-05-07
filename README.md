# `deepmd_toolkit`

Small notebook-based utilities for preparing datasets and analysing DeePMD models.

Use the DeepMD Python environment for all notebooks in this repository. The notebooks assume `deepmd-kit` and its related scientific Python stack are already available in the active environment.

## Get The Code

Clone the repository with:

```bash
git clone https://github.com/SamDFr/deepmd_toolkit.git
cd deepmd_toolkit
```

After cloning:

1. Activate your `deepmd-kit` Python environment.
2. Install or refresh the notebook dependencies with `pip install -r requirements.txt`.
3. Start Jupyter from that environment.
4. Add your input files in the directories described below.

## Repository layout

- [data_preparation/dpdata.ipynb](/Users/samuel/Desktop/postdoc_PhLAM/codes/deepmd_toolkit/data_preparation/dpdata.ipynb): convert an ASE trajectory into DeepMD `raw` and `npy` datasets with `dpdata`
- [model_analysis/dp_inference.ipynb](/Users/samuel/Desktop/postdoc_PhLAM/codes/deepmd_toolkit/model_analysis/dp_inference.ipynb): run a frozen DeepMD model on a labelled trajectory and export DFT vs DeepMD comparisons
- [model_analysis/dp_correlation_plots.ipynb](/Users/samuel/Desktop/postdoc_PhLAM/codes/deepmd_toolkit/model_analysis/dp_correlation_plots.ipynb): inspect parity plots and force-angle differences in the notebook, then export summary statistics
- [model_analysis/dp_training_analysis.ipynb](/Users/samuel/Desktop/postdoc_PhLAM/codes/deepmd_toolkit/model_analysis/dp_training_analysis.ipynb): inspect `lcurve.out` learning curves from training

## Expected workflow

1. Prepare a labelled dataset in ASE trajectory format.
2. Use `data_preparation/dpdata.ipynb` to export DeepMD-ready data.
3. Train or select a frozen DeepMD model (`graph.pb`).
4. Use `model_analysis/dp_inference.ipynb` to compare model predictions against reference data from `model_analysis/input/`.
5. Use `model_analysis/dp_correlation_plots.ipynb` to visualise the agreement in the notebook and export summary metrics.
6. Use `model_analysis/dp_training_analysis.ipynb` to inspect the training curve.

## Requirements

Use the `deepmd-kit` Python environment for this repository.

The expected workflow is:

1. Activate your `deepmd-kit` environment.
2. Install or refresh the notebook dependencies with `pip install -r requirements.txt`.
3. Start Jupyter from that environment.
4. Run the notebooks from the activated environment.

This repository provides a minimal [requirements.txt](/Users/samuel/Desktop/postdoc_PhLAM/codes/deepmd_toolkit/requirements.txt) describing the notebook dependencies.
Install it into your existing `deepmd-kit` environment rather than treating it as a replacement for the full DeepMD setup.

Example:

```bash
conda activate deepmd
pip install -r requirements.txt
jupyter lab
```

## Environment

The notebooks assume a Python environment with at least:

- `ase`
- `dpdata`
- `deepmd-kit`
- `numpy`
- `pandas`
- `matplotlib`
- `tqdm`
- `jupyter`

Use your DeepMD environment when starting Jupyter, for example the environment you normally use for `deepmd-kit`.

These notebooks were rewritten to avoid hard-coded absolute paths. Each notebook now has a dedicated configuration section near the top where you set:

- the input trajectory or `lcurve.out` file
- the frozen model path when needed
- the output path for exported text files when a notebook writes them

## Suggested local data layout

This repository does not ship trajectory or training-curve data. A simple layout that matches the default notebook configuration is:

```text
deepmd_toolkit/
├── data_preparation/
│   └── input/
│       └── your_training_or_validation_set.traj
├── model_analysis/
│   ├── input/
│   │   └── your_validation_set.traj
│   │   └── lcurve.out
│   ├── model/
│   │   └── graph.pb
└── README.md
```

Put your files in these directories and select them with the configuration cells. If your files live elsewhere, edit the configuration cells instead of changing notebook logic.
