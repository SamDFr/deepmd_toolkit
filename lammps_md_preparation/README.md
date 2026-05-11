# LAMMPS MD Preparation

This directory contains notebook workflows and reusable Python helpers for:

- building slab supercells from POSCAR files
- exporting LAMMPS data files from POSCAR batches
- analysing temperature evolution from `log.lammps`
- extracting `possur` and `velsur` style files from LAMMPS trajectories

## What was cleaned up

The original notebooks contained several assumptions tied to one local study:

- absolute paths under `/Users/samuel/...`
- hard-coded dataset names such as `TS5`, `AL1`, `500K`
- atom index ranges baked into the logic
- an external `matplotlib` style file outside this repository
- HOPG-specific atom type rewriting mixed directly into notebook cells

The notebooks are now intended to be configured through explicit variables near the top of each workflow, and the reusable logic lives in [utils.py](/Users/samuel/Desktop/postdoc_PhLAM/codes/deepmd_toolkit/lammps_md_preparation/utils.py).

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
- [thermalisation_analysis.ipynb](/Users/samuel/Desktop/postdoc_PhLAM/codes/deepmd_toolkit/lammps_md_preparation/thermalisation_analysis.ipynb): parse a LAMMPS log, compute summary statistics, and plot the temperature evolution
- [get_POSSUR_VELSUR.ipynb](/Users/samuel/Desktop/postdoc_PhLAM/codes/deepmd_toolkit/lammps_md_preparation/get_POSSUR_VELSUR.ipynb): select trajectory frames and export `possur` and `velsur` files for downstream codes

## Usage guidance

- Keep raw inputs outside the notebook code and point to them through the configuration cells.
- When a downstream code requires zeroed positions or velocities for a subset of atoms, pass the relevant atom indices explicitly instead of editing helper logic.
- `VELOCITY_SCALE` is a multiplicative unit-conversion factor applied before writing `velsur`. It is not the MD timestep by itself.
- If your downstream code expects a displacement per step rather than a velocity, then you would multiply by the relevant timestep separately.
