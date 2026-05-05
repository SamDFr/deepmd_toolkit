# Model Analysis

This directory contains notebooks for evaluating a frozen DeepMD model and inspecting training quality.

Run these notebooks from the DeepMD Python environment.

## Notebooks

- [dp_inference.ipynb](/Users/samuel/Desktop/postdoc_PhLAM/codes/deepmd_toolkit/model_analysis/dp_inference.ipynb)
- [dp_correlation_plots.ipynb](/Users/samuel/Desktop/postdoc_PhLAM/codes/deepmd_toolkit/model_analysis/dp_correlation_plots.ipynb)
- [dp_training_analysis.ipynb](/Users/samuel/Desktop/postdoc_PhLAM/codes/deepmd_toolkit/model_analysis/dp_training_analysis.ipynb)

## Recommended order

1. Run `dp_inference.ipynb` to generate `energies_forces.txt` and `energies_forces_atoms.txt`.
2. Run `dp_correlation_plots.ipynb` to inspect the plots in the notebook and write `dp_vs_dft_stats.txt`.
3. Run `dp_training_analysis.ipynb` to inspect `lcurve.out`.

## Default output directories

- `model_analysis/outputs/inference/`
- `model_analysis/outputs/dp_vs_dft_stats.txt`

## Required inputs

- a frozen DeepMD model file such as `graph.pb`
- one or more labelled ASE trajectories in `model_analysis/input/`
- a DeepMD `lcurve.out` file in `model_analysis/input/` for training analysis

## Usage notes

- use `TRAJECTORY_PATTERN` to filter matching trajectories
- use `TRAJECTORY_INDEX` to choose which matching file to evaluate
