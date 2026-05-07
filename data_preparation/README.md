# Data Preparation

The notebook in this directory is for converting an ASE-readable labelled trajectory into DeepMD dataset formats.

Run it from the DeepMD Python environment.
If needed, install the notebook dependencies from the repository root with `pip install -r requirements.txt` after activating that environment.

## Notebook

- [dpdata.ipynb](/Users/samuel/Desktop/postdoc_PhLAM/codes/deepmd_toolkit/data_preparation/dpdata.ipynb)

## Inputs

- add one or more ASE trajectory files in `data_preparation/input/`
- each trajectory should contain energies and forces, for example `.traj`

## Outputs

By default the notebook writes into `data_preparation/outputs/dpdata_export/`:

- `raw/`: DeepMD raw format
- `npy/`: DeepMD numpy format
- `dataset.xyz`: optional XYZ preview

## Usage notes

- place trajectory files in `data_preparation/input/`
- use `TRAJECTORY_PATTERN` to filter matching files
- use `TRAJECTORY_INDEX` to choose which matching file to load
- treat the exported `npy` dataset as the handoff into training
