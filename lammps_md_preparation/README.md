# LAMMPS MD Preparation

This directory contains notebook workflows and reusable Python helpers for:

- building slab supercells from POSCAR files
- exporting LAMMPS data files from POSCAR batches
- exporting a selected `vasprun.xml` snapshot to a LAMMPS data file with finite-difference velocities
- analysing temperature evolution from `log.lammps`
- extracting `possur` and `velsur` style files from LAMMPS trajectories

## Layout

The notebooks are intended to be configured through explicit variables near the top of each workflow.
The reusable Python logic now lives in the dedicated internal package directory:

- [lammps_md_preparation/python/lammps_md_preparation/__init__.py](/Users/samuel/Desktop/postdoc_PhLAM/codes/deepmd_toolkit/lammps_md_preparation/python/lammps_md_preparation/__init__.py)
- [lammps_md_preparation/python/lammps_md_preparation/utils.py](/Users/samuel/Desktop/postdoc_PhLAM/codes/deepmd_toolkit/lammps_md_preparation/python/lammps_md_preparation/utils.py)

## Environment

This subdirectory does not depend on `deepmd-kit` from code inspection.
Its notebooks only need:

- `ase`
- `numpy`
- `matplotlib`
- `jupyter`

You can therefore use either:

- the same environment as the rest of `deepmd_toolkit`
- or a separate lightweight virtual environment for this subdirectory alone

To install only the dependencies needed here:

```bash
python3 -m venv .venv-lammps-md
source .venv-lammps-md/bin/activate
pip install -r lammps_md_preparation/requirements.txt
```

## Notebooks

- [HOPG_preparation.ipynb](/Users/samuel/Desktop/postdoc_PhLAM/codes/deepmd_toolkit/lammps_md_preparation/HOPG_preparation.ipynb): build a repeated slab, optionally remove the top layer, and export POSCAR plus LAMMPS data
- [lammps_gen_from_POSCAR.ipynb](/Users/samuel/Desktop/postdoc_PhLAM/codes/deepmd_toolkit/lammps_md_preparation/lammps_gen_from_POSCAR.ipynb): convert a directory of POSCAR files into LAMMPS data files
- [vasprun_snapshot_to_lammps.ipynb](/Users/samuel/Desktop/postdoc_PhLAM/codes/deepmd_toolkit/lammps_md_preparation/vasprun_snapshot_to_lammps.ipynb): extract one ionic step from a file in `input/vasprun/`, estimate velocities by finite differences, and export a LAMMPS data file
- [thermalisation_analysis.ipynb](/Users/samuel/Desktop/postdoc_PhLAM/codes/deepmd_toolkit/lammps_md_preparation/thermalisation_analysis.ipynb): parse a LAMMPS log, compute summary statistics, and plot the temperature evolution
- [get_POSSUR_VELSUR.ipynb](/Users/samuel/Desktop/postdoc_PhLAM/codes/deepmd_toolkit/lammps_md_preparation/get_POSSUR_VELSUR.ipynb): select trajectory frames and export `possur` and `velsur` files for downstream codes

## Usage guidance

- Keep raw inputs outside the notebook code and point to them through the configuration cells.
- Notebook paths are now resolved relative to `lammps_md_preparation/` whether you launch Jupyter from the repository root or from inside this subdirectory.
- Default sample inputs currently follow this layout:
  `input/POSCAR_Unit_Cell`, `input/poscars/`, `input/lammps/`, and `input/vasprun/`
- The `vasprun_snapshot_to_lammps.ipynb` workflow defaults to the reduced committed example file `input/vasprun/vasprun-1_50frames.xml`; use `VASPRUN_PATTERN` and `VASPRUN_INDEX` to choose another XML file when needed.
- For `vasprun.xml` inputs, set `ION_TIMESTEP_FS` to the ionic MD timestep used in VASP; velocities are estimated from neighbouring frames and then converted by ASE when writing the LAMMPS data file.
- When a downstream code requires zeroed positions or velocities for a subset of atoms, pass the relevant atom indices explicitly instead of editing helper logic.
- `VELOCITY_SCALE` is a multiplicative unit-conversion factor applied before writing `velsur`. It is not the MD timestep by itself.
- If your downstream code expects a displacement per step rather than a velocity, then you would multiply by the relevant timestep separately.
