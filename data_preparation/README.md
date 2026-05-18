# Data Preparation

The notebook in this directory is for converting an ASE-readable labelled trajectory into DeepMD dataset formats.

Run it from a Python environment that has the repository root dependencies installed with `pip install -r requirements.txt`.
This notebook does require `deepmd-kit` because it is part of the DeepMD workflow.
The configuration cell near the top of the notebook includes brief inline comments for the non-obvious variables.

## Notebook

- [dpdata.ipynb](/Users/samuel/Desktop/postdoc_PhLAM/codes/deepmd_toolkit/data_preparation/dpdata.ipynb)

## Inputs

- add one or more ASE trajectory files in `data_preparation/input/`
- each trajectory should contain energies and forces, for example `.traj`

Current notebook behaviour:
- the notebook discovers all files matching `TRAJECTORY_PATTERN`
- it selects exactly one file using `TRAJECTORY_INDEX`
- it does not merge several `.traj` files automatically

## Outputs

By default the notebook writes into `data_preparation/outputs/dpdata_export/`:

- `raw/`: DeepMD raw format
- `npy/`: DeepMD numpy format
- `dataset.xyz`: optional XYZ preview

## Usage notes

- place trajectory files in `data_preparation/input/`
- use `TRAJECTORY_PATTERN` to filter matching files
- use `TRAJECTORY_INDEX` to choose which matching file to load
- if you want to combine several `.traj` files into one dataset, that needs an explicit notebook change; the current notebook exports one selected trajectory at a time
- treat the exported `npy` dataset as the handoff into training
