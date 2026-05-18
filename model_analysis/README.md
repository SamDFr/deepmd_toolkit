# Model Analysis

This directory contains notebooks for evaluating one or more frozen DeepMD models and inspecting training quality.

Run these notebooks from a Python environment that has the repository root dependencies installed with `pip install -r requirements.txt`.
These notebooks do require `deepmd-kit`.

## Notebooks

- [01_dp_training_analysis.ipynb](/Users/samuel/Desktop/postdoc_PhLAM/codes/deepmd_toolkit/model_analysis/01_dp_training_analysis.ipynb)
- [02_dp_inference.ipynb](/Users/samuel/Desktop/postdoc_PhLAM/codes/deepmd_toolkit/model_analysis/02_dp_inference.ipynb)
- [03_dp_correlation_plots.ipynb](/Users/samuel/Desktop/postdoc_PhLAM/codes/deepmd_toolkit/model_analysis/03_dp_correlation_plots.ipynb)

## Recommended order

1. Run `01_dp_training_analysis.ipynb` to inspect the `lcurve` files that correspond to your model files.
2. Run `02_dp_inference.ipynb` to generate `energies_forces.txt` and `energies_forces_atoms.txt`.
3. Run `03_dp_correlation_plots.ipynb` to inspect the plots in the notebook and write per-model reports.

## Default output directories

- `model_analysis/outputs/inference/<model_label>/`
- `model_analysis/outputs/correlation_reports/`

## Required inputs

- one or more frozen DeepMD model files such as `graph.pb`, `graph.001.pb`, `graph_001.pb`, or `model.001.pb`
- one or more labelled ASE trajectories in `model_analysis/input/`
- one or more DeepMD `lcurve*.out` files in `model_analysis/input/` for training analysis

## Usage notes

- `01_dp_training_analysis.ipynb` matches training curves by filename: `graph.pb -> lcurve.out`, `model.pb -> lcurve.out`, `graph.001.pb -> lcurve.001.out`, `model.001.pb -> lcurve.001.out`, `graph_001.pb -> lcurve_001.out`
- place several `.pb` files under `model_analysis/model/`; `02_dp_inference.ipynb` evaluates all matches from `MODEL_PATTERN`
- each model writes to its own subdirectory in `model_analysis/outputs/inference/`
- `TEST_selected.traj` is kept as a tracked example input for testing the inference/correlation workflow
- place the matching `lcurve*.out` files under `model_analysis/input/`
- use `TRAJECTORY_PATTERN` to filter matching trajectories
- use `TRAJECTORY_INDEX` to choose which matching file to evaluate
