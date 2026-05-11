# `deepmd_toolkit`

Small notebook-based utilities for:

- preparing datasets for DeePMD
- analysing DeePMD models
- preparing LAMMPS MD inputs and derived trajectory files for downstream codes

The repository no longer requires you to reuse a pre-existing DeepMD environment.
You can install the repository requirements into a dedicated virtual environment.
Only the DeepMD-specific notebooks require `deepmd-kit`; the `lammps_md_preparation/` workflows do not, based on code inspection.

## Get The Code

Clone the repository with:

```bash
git clone https://github.com/SamDFr/deepmd_toolkit.git
cd deepmd_toolkit
```

After cloning:

1. Create or activate a Python environment.
2. Install the dependencies with `pip install -r requirements.txt`.
3. Start Jupyter from that environment.
4. Add your input files in the directories described below.

Example with a dedicated virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Repository layout

- [data_preparation/dpdata.ipynb](/Users/samuel/Desktop/postdoc_PhLAM/codes/deepmd_toolkit/data_preparation/dpdata.ipynb): convert an ASE trajectory into DeepMD `raw` and `npy` datasets with `dpdata`
- [model_analysis/dp_inference.ipynb](/Users/samuel/Desktop/postdoc_PhLAM/codes/deepmd_toolkit/model_analysis/dp_inference.ipynb): run a frozen DeepMD model on a labelled trajectory and export DFT vs DeepMD comparisons
- [model_analysis/dp_correlation_plots.ipynb](/Users/samuel/Desktop/postdoc_PhLAM/codes/deepmd_toolkit/model_analysis/dp_correlation_plots.ipynb): inspect parity plots and force-angle differences in the notebook, then export summary statistics
- [model_analysis/dp_training_analysis.ipynb](/Users/samuel/Desktop/postdoc_PhLAM/codes/deepmd_toolkit/model_analysis/dp_training_analysis.ipynb): inspect `lcurve.out` learning curves from training
- [lammps_md_preparation/README.md](/Users/samuel/Desktop/postdoc_PhLAM/codes/deepmd_toolkit/lammps_md_preparation/README.md): notebook workflows and helpers for preparing LAMMPS inputs, analysing thermalisation, and exporting `possur` / `velsur`

## Expected workflow

1. Prepare a labelled dataset in ASE trajectory format.
2. Use `data_preparation/dpdata.ipynb` to export DeepMD-ready data.
3. Train or select a frozen DeepMD model (`graph.pb`).
4. Use `model_analysis/dp_inference.ipynb` to compare model predictions against reference data from `model_analysis/input/`.
5. Use `model_analysis/dp_correlation_plots.ipynb` to visualise the agreement in the notebook and export summary metrics.
6. Use `model_analysis/dp_training_analysis.ipynb` to inspect the training curve.
7. Use `lammps_md_preparation/` when you need to generate LAMMPS-ready structures or derive trajectory exports for external MD workflows.

## Requirements

This repository provides a global [requirements.txt](/Users/samuel/Desktop/postdoc_PhLAM/codes/deepmd_toolkit/requirements.txt) for all notebooks.

If you only need the LAMMPS preparation workflows, use the lighter file [lammps_md_preparation/requirements.txt](/Users/samuel/Desktop/postdoc_PhLAM/codes/deepmd_toolkit/lammps_md_preparation/requirements.txt).

## Environment

For the full repository, the notebooks assume a Python environment with at least:

- `ase`
- `dpdata`
- `deepmd-kit`
- `numpy`
- `pandas`
- `matplotlib`
- `tqdm`
- `jupyter`

For `lammps_md_preparation/` only, the required subset is:

- `ase`
- `numpy`
- `matplotlib`
- `jupyter`

These notebooks were rewritten to avoid hard-coded absolute paths. Each notebook now has a dedicated configuration section near the top where you set:

- the input trajectory or `lcurve.out` file
- the frozen model path when needed
- the output path for exported text files when a notebook writes them
- the trajectory filters, atom index selections, and export options for LAMMPS preparation workflows

## Suggested local data layout

This repository does not ship trajectory or training-curve data. A simple layout that matches the default notebook configuration is:

```text
deepmd_toolkit/
├── data_preparation/
│   └── input/
│       └── your_training_or_validation_set.traj
├── lammps_md_preparation/
│   ├── input/
│   │   ├── POSCAR_Unit_Cell
│   │   ├── log.lammps
│   │   └── traj.lammpstrj
│   └── output/
├── model_analysis/
│   ├── input/
│   │   └── your_validation_set.traj
│   │   └── lcurve.out
│   ├── model/
│   │   └── graph.pb
└── README.md
```

Put your files in these directories and select them with the configuration cells. If your files live elsewhere, edit the configuration cells instead of changing notebook logic.
