from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def md_cell(text: str) -> dict:
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": [line + "\n" for line in text.strip("\n").splitlines()],
    }


def code_cell(text: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [line + "\n" for line in text.strip("\n").splitlines()],
    }


def notebook(cells: list[dict]) -> dict:
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "deepmd",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "name": "python",
                "version": "3.x",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def write_notebook(relative_path: str, cells: list[dict]) -> None:
    path = ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(notebook(cells), handle, indent=1)
        handle.write("\n")


def build_dpdata_notebook() -> list[dict]:
    return [
        md_cell(
            """
            # Prepare DeepMD datasets with `dpdata`

            This notebook converts an ASE-readable trajectory into DeepMD training data.

            ## What it does
            - loads a labelled trajectory containing energies and forces
            - inspects the number of configurations
            - exports the dataset to DeepMD `raw` and `npy` formats
            - optionally writes an XYZ file for quick inspection

            ## Before you run it
            Run this notebook from the DeepMD Python environment.
            Place one or more `.traj` files in `data_preparation/input/`, then update the configuration cell below if needed.
            """
        ),
        code_cell(
            """
            from pathlib import Path

            import ase.io
            import dpdata
            """
        ),
        md_cell(
            """
            ## Configuration

            Select the trajectory from `data_preparation/input/` and choose the output directory here.
            Relative paths are resolved from the repository root.
            """
        ),
        code_cell(
            """
            PROJECT_ROOT = Path.cwd().resolve().parent if Path.cwd().name == "data_preparation" else Path.cwd().resolve()

            INPUT_DIR = PROJECT_ROOT / "data_preparation" / "input"
            TRAJECTORY_PATTERN = "*.traj"
            TRAJECTORY_INDEX = 0
            OUTPUT_DIR = PROJECT_ROOT / "data_preparation" / "outputs" / "dpdata_export"
            WRITE_XYZ = True

            INPUT_DIR.mkdir(parents=True, exist_ok=True)
            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

            print(f"Project root: {PROJECT_ROOT}")
            print(f"Input directory: {INPUT_DIR}")
            print(f"Output directory: {OUTPUT_DIR}")
            """
        ),
        code_cell(
            """
            candidate_files = sorted(INPUT_DIR.glob(TRAJECTORY_PATTERN))

            if not candidate_files:
                raise FileNotFoundError(
                    f"No trajectory file matched '{TRAJECTORY_PATTERN}' in {INPUT_DIR}\\n"
                    "Add one or more `.traj` files to data_preparation/input/ or update TRAJECTORY_PATTERN."
                )

            if TRAJECTORY_INDEX >= len(candidate_files):
                raise IndexError(
                    f"TRAJECTORY_INDEX={TRAJECTORY_INDEX} but only {len(candidate_files)} matching file(s) were found."
                )

            print("Available trajectory files:")
            for idx, path in enumerate(candidate_files):
                print(f"  [{idx}] {path.name}")

            TRAJECTORY_FILE = candidate_files[TRAJECTORY_INDEX]
            print(f"Selected trajectory: {TRAJECTORY_FILE.name}")

            ase_frames = ase.io.read(TRAJECTORY_FILE, index=":")
            n_frames = len(ase_frames)

            print(f"Loaded {n_frames} configurations from {TRAJECTORY_FILE.name}")
            """
        ),
        md_cell(
            """
            ## Convert to `dpdata`

            `LabeledSystem` expects energies and forces to be available in the input trajectory.
            """
        ),
        code_cell(
            """
            labeled_system = dpdata.LabeledSystem(
                str(TRAJECTORY_FILE),
                set_size=n_frames,
                fmt="ase/traj",
            )

            labeled_system
            """
        ),
        code_cell(
            """
            raw_dir = OUTPUT_DIR / "raw"
            npy_dir = OUTPUT_DIR / "npy"

            labeled_system.to("deepmd/raw", str(raw_dir))
            labeled_system.to("deepmd/npy", str(npy_dir))

            print(f"Wrote DeepMD raw dataset to: {raw_dir}")
            print(f"Wrote DeepMD npy dataset to: {npy_dir}")
            """
        ),
        code_cell(
            """
            if WRITE_XYZ:
                xyz_path = OUTPUT_DIR / "dataset.xyz"
                labeled_system.to("xyz", str(xyz_path))
                print(f"Wrote XYZ preview to: {xyz_path}")
            else:
                print("Skipping XYZ export.")
            """
        ),
        md_cell(
            """
            ## Notes

            Typical next step: use the exported `npy` dataset in your DeepMD training workflow.
            """
        ),
    ]


def build_inference_notebook() -> list[dict]:
    return [
        md_cell(
            """
            # Run DeepMD inference against a reference trajectory

            This notebook evaluates a frozen DeepMD model on an ASE trajectory that already contains
            reference energies and forces, then writes plain-text comparison files for downstream analysis.

            ## Outputs
            - `energies_forces.txt`: per-frame DFT vs DeepMD energies
            - `energies_forces_atoms.txt`: per-atom DFT vs DeepMD force components

            ## Before you run it
            Run this notebook from the DeepMD Python environment.
            Place one or more labelled validation/test trajectories in `model_analysis/input/`.
            """
        ),
        code_cell(
            """
            from pathlib import Path

            import numpy as np
            from ase.io import read
            from deepmd.infer import DeepPot
            from tqdm import tqdm

            try:
                from ase.calculators.deepmd import DeepMDCalculator as DP
            except Exception:
                from deepmd.calculator import DP
            """
        ),
        md_cell(
            """
            ## Configuration

            Select the model and reference trajectory here. Relative paths are resolved from the repository root.
            """
        ),
        code_cell(
            """
            PROJECT_ROOT = Path.cwd().resolve().parent if Path.cwd().name == "model_analysis" else Path.cwd().resolve()

            MODEL_FILE = PROJECT_ROOT / "model_analysis" / "model" / "graph.pb"
            INPUT_DIR = PROJECT_ROOT / "model_analysis" / "input"
            TRAJECTORY_PATTERN = "*.traj"
            TRAJECTORY_INDEX = 0
            OUTPUT_DIR = PROJECT_ROOT / "model_analysis" / "outputs" / "inference"

            INPUT_DIR.mkdir(parents=True, exist_ok=True)
            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

            print(f"Project root: {PROJECT_ROOT}")
            print(f"Model file: {MODEL_FILE}")
            print(f"Input directory: {INPUT_DIR}")
            print(f"Output directory: {OUTPUT_DIR}")
            """
        ),
        code_cell(
            """
            if not MODEL_FILE.exists():
                raise FileNotFoundError(
                    f"Model file not found: {MODEL_FILE}\\n"
                    "Update MODEL_FILE in the configuration cell before running the notebook."
                )

            trajectory_files = sorted(INPUT_DIR.glob(TRAJECTORY_PATTERN))
            if not trajectory_files:
                raise FileNotFoundError(
                    f"No trajectory file matched '{TRAJECTORY_PATTERN}' in {INPUT_DIR}\\n"
                    "Add one or more `.traj` files to model_analysis/input/ or update TRAJECTORY_PATTERN."
                )

            if TRAJECTORY_INDEX >= len(trajectory_files):
                raise IndexError(
                    f"TRAJECTORY_INDEX={TRAJECTORY_INDEX} but only {len(trajectory_files)} matching file(s) were found."
                )

            print("Available trajectory files:")
            for idx, path in enumerate(trajectory_files):
                print(f"  [{idx}] {path.name}")

            trajectory_file = trajectory_files[TRAJECTORY_INDEX]
            print(f"Selected trajectory: {trajectory_file.name}")

            frames = read(str(trajectory_file), ":")
            print(f"Loaded {len(frames)} frames from {trajectory_file}")
            """
        ),
        md_cell(
            """
            ## Load the model and attach the DeepMD calculator
            """
        ),
        code_cell(
            """
            model = DeepPot(str(MODEL_FILE))
            type_map = model.get_type_map()

            print(f"type_map: {type_map}")

            calculator = DP(model=str(MODEL_FILE), type_map=type_map)
            """
        ),
        code_cell(
            """
            reference_frames = []
            predicted_frames = []

            for atoms in frames:
                atoms_ref = atoms.copy()
                atoms_ref.calc = atoms.calc
                reference_frames.append(atoms_ref)

                atoms_dp = atoms.copy()
                atoms_dp.calc = calculator
                predicted_frames.append(atoms_dp)

            print(f"Prepared {len(reference_frames)} reference/prediction frame pairs")
            """
        ),
        md_cell(
            """
            ## Evaluate and write comparison files
            """
        ),
        code_cell(
            """
            frame_output = OUTPUT_DIR / "energies_forces.txt"
            atom_output = OUTPUT_DIR / "energies_forces_atoms.txt"

            with frame_output.open("w", encoding="utf-8") as fh_energy, atom_output.open("w", encoding="utf-8") as fh_atom:
                fh_energy.write("# frame energy_DFT_eV energy_DP_eV\\n")
                fh_atom.write(
                    "# frame atom element fx_DFT fy_DFT fz_DFT fx_DP fy_DP fz_DP energy_DFT energy_DP\\n"
                )

                for frame_index, (atoms_ref, atoms_dp) in enumerate(
                    tqdm(
                        zip(reference_frames, predicted_frames),
                        total=len(reference_frames),
                        desc="Evaluating",
                    )
                ):
                    energy_ref = atoms_ref.get_potential_energy()
                    forces_ref = atoms_ref.get_forces()

                    energy_dp = atoms_dp.get_potential_energy()
                    forces_dp = atoms_dp.get_forces()

                    fh_energy.write(f"{frame_index:6d} {energy_ref: .10f} {energy_dp: .10f}\\n")

                    for atom_index, symbol in enumerate(atoms_ref.get_chemical_symbols()):
                        fxr, fyr, fzr = forces_ref[atom_index]
                        fxd, fyd, fzd = forces_dp[atom_index]
                        fh_atom.write(
                            f"{frame_index:6d} {atom_index:6d} {symbol:2s} "
                            f"{fxr: .6f} {fyr: .6f} {fzr: .6f} "
                            f"{fxd: .6f} {fyd: .6f} {fzd: .6f} "
                            f"{energy_ref: .10f} {energy_dp: .10f}\\n"
                        )

            print(f"Wrote frame-level comparison file to: {frame_output}")
            print(f"Wrote atom-level comparison file to: {atom_output}")
            """
        ),
        md_cell(
            """
            ## Next step

            Open `dp_correlation_plots.ipynb` and point it at the files written in `model_analysis/outputs/inference/`.
            """
        ),
    ]


def build_correlation_notebook() -> list[dict]:
    return [
        md_cell(
            """
            # Plot DeepMD vs DFT correlation metrics

            This notebook reads the text files written by `dp_inference.ipynb` and produces parity plots,
            error histograms, and a text summary of regression statistics.

            Run this notebook from the DeepMD Python environment.
            """
        ),
        code_cell(
            """
            from pathlib import Path

            import matplotlib.pyplot as plt
            import numpy as np
            import pandas as pd
            """
        ),
        md_cell(
            """
            ## Configuration

            `STYLE_FILE` is optional. Leave it as `None` to use the default Matplotlib style.
            """
        ),
        code_cell(
            """
            PROJECT_ROOT = Path.cwd().resolve().parent if Path.cwd().name == "model_analysis" else Path.cwd().resolve()

            INFERENCE_DIR = PROJECT_ROOT / "model_analysis" / "outputs" / "inference"
            STYLE_FILE = None
            N_ATOMS = None

            ENERGY_FILE = INFERENCE_DIR / "energies_forces.txt"
            ATOM_FILE = INFERENCE_DIR / "energies_forces_atoms.txt"
            REPORT_FILE = PROJECT_ROOT / "model_analysis" / "outputs" / "dp_vs_dft_stats.txt"

            print(f"Energy file: {ENERGY_FILE}")
            print(f"Atom file: {ATOM_FILE}")
            print(f"Report file: {REPORT_FILE}")
            """
        ),
        code_cell(
            """
            if STYLE_FILE is not None:
                plt.style.use(STYLE_FILE)

            if not ENERGY_FILE.exists() or not ATOM_FILE.exists():
                raise FileNotFoundError(
                    "Inference outputs were not found. Run dp_inference.ipynb first or update the paths in the configuration cell."
                )

            energy_df = pd.read_csv(
                ENERGY_FILE,
                comment="#",
                delim_whitespace=True,
                names=["frame", "energy_DFT_eV", "energy_DP_eV"],
            )

            atom_df = pd.read_csv(
                ATOM_FILE,
                comment="#",
                delim_whitespace=True,
                names=[
                    "frame",
                    "atom",
                    "element",
                    "fx_DFT",
                    "fy_DFT",
                    "fz_DFT",
                    "fx_DP",
                    "fy_DP",
                    "fz_DP",
                    "energy_DFT",
                    "energy_DP",
                ],
            )

            energy_df = energy_df.dropna(subset=["energy_DFT_eV", "energy_DP_eV"]).reset_index(drop=True)
            atom_df = atom_df.dropna(
                subset=["fx_DFT", "fy_DFT", "fz_DFT", "fx_DP", "fy_DP", "fz_DP"]
            ).reset_index(drop=True)

            print(f"Loaded {len(energy_df)} frame-level entries")
            print(f"Loaded {len(atom_df)} atom-level entries")
            """
        ),
        code_cell(
            """
            def stats(y_true, y_pred):
                diff = np.asarray(y_pred) - np.asarray(y_true)
                mae = np.mean(np.abs(diff))
                rmse = np.sqrt(np.mean(diff ** 2))
                r2 = 1.0 - np.sum(diff ** 2) / np.sum((y_true - np.mean(y_true)) ** 2) if len(y_true) > 1 else np.nan
                return mae, rmse, r2
            """
        ),
        md_cell(
            """
            ## Energy parity and error distributions
            """
        ),
        code_cell(
            """
            y_true = energy_df["energy_DFT_eV"].to_numpy()
            y_pred = energy_df["energy_DP_eV"].to_numpy()
            _, rmse, r2 = stats(y_true, y_pred)

            lims = [min(y_true.min(), y_pred.min()) - 0.1, max(y_true.max(), y_pred.max()) + 0.1]
            abs_err = np.abs(y_pred - y_true)

            fig, ax = plt.subplots(figsize=(6, 6))
            scatter = ax.scatter(
                y_true,
                y_pred,
                c=abs_err,
                s=20,
                cmap="viridis",
                alpha=0.9,
                edgecolors="none",
            )
            ax.plot(lims, lims, color="black", linewidth=1)
            ax.set_xlim(lims)
            ax.set_ylim(lims)
            ax.set_aspect("equal", adjustable="box")
            ax.set_xlabel("Energy DFT (eV)")
            ax.set_ylabel("Energy DP (eV)")
            ax.text(
                0.05,
                0.95,
                f"RMSE = {rmse:.4f} eV\\nR² = {r2:.4f}",
                transform=ax.transAxes,
                fontsize=12,
                verticalalignment="top",
            )
            cbar = fig.colorbar(scatter, ax=ax, pad=0.03)
            cbar.set_label("Absolute error (eV)")
            fig.tight_layout()
            plt.show()
            """
        ),
        code_cell(
            """
            if N_ATOMS is None:
                atom_counts = atom_df.groupby("frame").size().reindex(energy_df["frame"]).to_numpy(dtype=float)
            else:
                atom_counts = np.full(len(energy_df), float(N_ATOMS))

            valid_atom_counts = np.isfinite(atom_counts) & (atom_counts > 0)
            y_true_pa = y_true[valid_atom_counts] / atom_counts[valid_atom_counts]
            y_pred_pa = y_pred[valid_atom_counts] / atom_counts[valid_atom_counts]

            _, rmse_pa, r2_pa = stats(y_true_pa, y_pred_pa)
            abs_err_pa = np.abs(y_pred_pa - y_true_pa) * 1000.0

            lims_pa = [
                min(y_true_pa.min(), y_pred_pa.min()) - 0.01,
                max(y_true_pa.max(), y_pred_pa.max()) + 0.01,
            ]

            fig, ax = plt.subplots(figsize=(6, 6))
            scatter = ax.scatter(
                y_true_pa,
                y_pred_pa,
                c=abs_err_pa,
                s=20,
                cmap="viridis",
                alpha=0.9,
                edgecolors="none",
            )
            ax.plot(lims_pa, lims_pa, color="black", linewidth=1)
            ax.set_xlim(lims_pa)
            ax.set_ylim(lims_pa)
            ax.set_aspect("equal", adjustable="box")
            ax.set_xlabel("Energy/atom DFT (eV/atom)")
            ax.set_ylabel("Energy/atom DP (eV/atom)")
            ax.text(
                0.05,
                0.95,
                f"RMSE = {rmse_pa * 1000:.2f} meV/atom\\nR² = {r2_pa:.4f}",
                transform=ax.transAxes,
                fontsize=12,
                verticalalignment="top",
            )
            cbar = fig.colorbar(scatter, ax=ax, pad=0.03)
            cbar.set_label("Absolute error (meV/atom)")
            fig.tight_layout()
            plt.show()
            """
        ),
        code_cell(
            """
            errors = y_pred - y_true

            fig, ax = plt.subplots(figsize=(6, 4))
            ax.hist(errors, bins=80, color="steelblue", alpha=0.8, edgecolor="black")
            ax.axvline(0.0, color="black", linestyle="--")
            ax.set_xlabel("Energy error (DP - DFT) [eV]")
            ax.set_ylabel("Count")
            ax.set_title(
                f"Mean = {errors.mean():.4f} eV, Std = {errors.std():.4f} eV"
            )
            fig.tight_layout()
            plt.show()

            errors_pa = y_pred_pa - y_true_pa
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.hist(errors_pa, bins=80, color="steelblue", alpha=0.8, edgecolor="black")
            ax.axvline(0.0, color="black", linestyle="--")
            ax.set_xlabel("Energy/atom error (DP - DFT) [eV/atom]")
            ax.set_ylabel("Count")
            ax.set_title(
                f"Mean = {errors_pa.mean():.6f} eV/atom, Std = {errors_pa.std():.6f} eV/atom"
            )
            fig.tight_layout()
            plt.show()
            """
        ),
        md_cell(
            """
            ## Force parity plots
            """
        ),
        code_cell(
            """
            for component in ["x", "y", "z"]:
                y_true_force = atom_df[f"f{component}_DFT"].to_numpy()
                y_pred_force = atom_df[f"f{component}_DP"].to_numpy()
                mae, rmse, r2 = stats(y_true_force, y_pred_force)

                force_limit = max(np.max(np.abs(y_true_force)), np.max(np.abs(y_pred_force)))
                fig, ax = plt.subplots(figsize=(6, 6))
                heatmap = ax.hexbin(y_true_force, y_pred_force, gridsize=120, bins="log", cmap="viridis")
                ax.plot([-force_limit, force_limit], [-force_limit, force_limit], color="black", linewidth=1)
                ax.set_xlim([-force_limit, force_limit])
                ax.set_ylim([-force_limit, force_limit])
                ax.set_aspect("equal", adjustable="box")
                ax.set_xlabel(f"F{component} DFT (eV/Å)")
                ax.set_ylabel(f"F{component} DP (eV/Å)")
                ax.set_title(f"Force {component.upper()} parity")
                ax.text(
                    0.05,
                    0.95,
                    f"MAE = {mae:.4f}\\nRMSE = {rmse:.4f}\\nR² = {r2:.4f}",
                    transform=ax.transAxes,
                    fontsize=11,
                    verticalalignment="top",
                    bbox=dict(boxstyle="round", facecolor="white", alpha=0.9, edgecolor="0.8"),
                )
                fig.colorbar(heatmap, ax=ax, label="log(count)", pad=0.03)
                fig.tight_layout()
                plt.show()
            """
        ),
        code_cell(
            """
            force_ref = np.sqrt(atom_df["fx_DFT"] ** 2 + atom_df["fy_DFT"] ** 2 + atom_df["fz_DFT"] ** 2).to_numpy()
            force_dp = np.sqrt(atom_df["fx_DP"] ** 2 + atom_df["fy_DP"] ** 2 + atom_df["fz_DP"] ** 2).to_numpy()
            mae, rmse, r2 = stats(force_ref, force_dp)

            force_limit = max(np.max(np.abs(force_ref)), np.max(np.abs(force_dp))) + 0.5
            fig, ax = plt.subplots(figsize=(6, 6))
            heatmap = ax.hexbin(force_ref, force_dp, gridsize=120, bins="log", cmap="viridis")
            ax.plot([0.0, force_limit], [0.0, force_limit], color="black", linewidth=1)
            ax.set_xlim([0.0, force_limit])
            ax.set_ylim([0.0, force_limit])
            ax.set_aspect("equal", adjustable="box")
            ax.set_xlabel("|F| DFT (eV/Å)")
            ax.set_ylabel("|F| DP (eV/Å)")
            ax.set_title("Force magnitude parity")
            ax.text(
                0.05,
                0.95,
                f"MAE = {mae:.4f}\\nRMSE = {rmse:.4f}\\nR² = {r2:.4f}",
                transform=ax.transAxes,
                fontsize=11,
                verticalalignment="top",
                bbox=dict(boxstyle="round", facecolor="white", alpha=0.9, edgecolor="0.8"),
            )
            fig.colorbar(heatmap, ax=ax, label="log(count)", pad=0.03)
            fig.tight_layout()
            plt.show()
            """
        ),
        md_cell(
            """
            ## Force-angle difference

            This plot shows the angular mismatch between the DFT and DeepMD force vectors for each atom.
            """
        ),
        code_cell(
            """
            force_ref_vectors = atom_df[["fx_DFT", "fy_DFT", "fz_DFT"]].to_numpy(float)
            force_dp_vectors = atom_df[["fx_DP", "fy_DP", "fz_DP"]].to_numpy(float)

            norm_ref = np.linalg.norm(force_ref_vectors, axis=1)
            norm_dp = np.linalg.norm(force_dp_vectors, axis=1)
            mask = (norm_ref > 1e-12) & (norm_dp > 1e-12)

            force_ref_vectors = force_ref_vectors[mask]
            force_dp_vectors = force_dp_vectors[mask]
            norm_ref = norm_ref[mask]
            norm_dp = norm_dp[mask]

            cosine = np.sum(force_ref_vectors * force_dp_vectors, axis=1) / (norm_ref * norm_dp)
            cosine = np.clip(cosine, -1.0, 1.0)
            angle_difference = np.degrees(np.arccos(cosine))
            """
        ),
        code_cell(
            """
            fig, ax = plt.subplots(figsize=(7, 4.5))
            ax.hist(angle_difference, bins=90, color="steelblue", alpha=0.85, edgecolor="black")
            ax.axvline(angle_difference.mean(), color="darkred", linestyle="--", linewidth=1.5)
            ax.set_xlabel("Angle difference between DFT and DP force vectors (deg)")
            ax.set_ylabel("Count")
            ax.set_title("Distribution of force-vector angle differences")
            ax.text(
                0.98,
                0.95,
                (
                    f"Mean = {angle_difference.mean():.2f} deg\\n"
                    f"Median = {np.median(angle_difference):.2f} deg\\n"
                    f"P90 = {np.percentile(angle_difference, 90):.2f} deg"
                ),
                transform=ax.transAxes,
                ha="right",
                va="top",
                fontsize=11,
                bbox=dict(boxstyle="round", facecolor="white", alpha=0.9, edgecolor="0.8"),
            )
            fig.tight_layout()
            plt.show()
            """
        ),
        md_cell(
            """
            ## Export summary statistics
            """
        ),
        code_cell(
            """
            REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

            with REPORT_FILE.open("w", encoding="utf-8") as handle:
                handle.write("=== DeePMD vs DFT Statistics Report ===\\n\\n")

                energy_ref = energy_df["energy_DFT_eV"].to_numpy(float)
                energy_dp = energy_df["energy_DP_eV"].to_numpy(float)
                energy_mask = np.isfinite(energy_ref) & np.isfinite(energy_dp)
                energy_ref = energy_ref[energy_mask]
                energy_dp = energy_dp[energy_mask]
                energy_error = energy_dp - energy_ref
                mae, rmse, r2 = stats(energy_ref, energy_dp)
                handle.write(
                    "[Energies]\\n"
                    f"N samples   : {energy_ref.size}\\n"
                    f"MAE         : {mae:.6f} eV\\n"
                    f"RMSE        : {rmse:.6f} eV\\n"
                    f"R²          : {r2:.6f}\\n"
                    f"Mean error  : {energy_error.mean():.6f} eV\\n"
                    f"Std error   : {energy_error.std():.6f} eV\\n"
                    f"Min/Max err : {energy_error.min():.6f} / {energy_error.max():.6f} eV\\n\\n"
                )

                for component in ["x", "y", "z"]:
                    force_ref_component = atom_df[f"f{component}_DFT"].to_numpy(float)
                    force_dp_component = atom_df[f"f{component}_DP"].to_numpy(float)
                    component_mask = np.isfinite(force_ref_component) & np.isfinite(force_dp_component)
                    force_ref_component = force_ref_component[component_mask]
                    force_dp_component = force_dp_component[component_mask]
                    force_error = force_dp_component - force_ref_component
                    mae, rmse, r2 = stats(force_ref_component, force_dp_component)
                    handle.write(
                        f"[Forces {component.upper()}]\\n"
                        f"N samples   : {force_ref_component.size}\\n"
                        f"MAE         : {mae:.6f} eV/Å\\n"
                        f"RMSE        : {rmse:.6f} eV/Å\\n"
                        f"R²          : {r2:.6f}\\n"
                        f"Mean error  : {force_error.mean():.6f} eV/Å\\n"
                        f"Std error   : {force_error.std():.6f} eV/Å\\n"
                        f"Min/Max err : {force_error.min():.6f} / {force_error.max():.6f} eV/Å\\n\\n"
                    )

                force_error = force_dp - force_ref
                mae, rmse, r2 = stats(force_ref, force_dp)
                handle.write(
                    "[Force Magnitudes]\\n"
                    f"N samples   : {force_ref.size}\\n"
                    f"MAE         : {mae:.6f} eV/Å\\n"
                    f"RMSE        : {rmse:.6f} eV/Å\\n"
                    f"R²          : {r2:.6f}\\n"
                    f"Mean error  : {force_error.mean():.6f} eV/Å\\n"
                    f"Std error   : {force_error.std():.6f} eV/Å\\n"
                    f"Min/Max err : {force_error.min():.6f} / {force_error.max():.6f} eV/Å\\n\\n"
                )

                handle.write(
                    "[Force Directions]\\n"
                    f"N samples   : {angle_difference.size}\\n"
                    f"Mean angle  : {angle_difference.mean():.6f} deg\\n"
                    f"Std angle   : {angle_difference.std():.6f} deg\\n"
                    f"Median      : {np.median(angle_difference):.6f} deg\\n"
                    f"P90         : {np.percentile(angle_difference, 90):.6f} deg\\n"
                    f"Min/Max     : {angle_difference.min():.6f} / {angle_difference.max():.6f} deg\\n"
                )

            print(f"Saved statistics report to {REPORT_FILE}")
            """
        ),
    ]


def build_training_notebook() -> list[dict]:
    return [
        md_cell(
            """
            # Analyse DeepMD training curves

            This notebook reads a `lcurve.out` file produced during DeepMD training and summarises
            the evolution of the learning rate and the energy/force RMSE values.

            Run this notebook from the DeepMD Python environment.
            """
        ),
        code_cell(
            """
            from pathlib import Path

            import matplotlib.pyplot as plt
            import numpy as np
            """
        ),
        md_cell(
            """
            ## Configuration
            """
        ),
        code_cell(
            """
            PROJECT_ROOT = Path.cwd().resolve().parent if Path.cwd().name == "model_analysis" else Path.cwd().resolve()

            LCURVE_FILE = PROJECT_ROOT / "model_analysis" / "training_res" / "lcurve.out"
            SUMMARY_WINDOW = 5

            print(f"lcurve file: {LCURVE_FILE}")
            """
        ),
        code_cell(
            """
            if not LCURVE_FILE.exists():
                raise FileNotFoundError(
                    f"Training curve file not found: {LCURVE_FILE}\\n"
                    "Update LCURVE_FILE in the configuration cell before running the notebook."
                )

            data = np.genfromtxt(LCURVE_FILE, comments="#", dtype=float)

            step = data[:, 0]
            rmse_val = data[:, 1]
            rmse_trn = data[:, 2]
            rmse_e_val = data[:, 3]
            rmse_e_trn = data[:, 4]
            rmse_f_val = data[:, 5]
            rmse_f_trn = data[:, 6]
            learning_rate = data[:, 7]

            print(f"Loaded {len(step)} optimisation steps")
            print(f"Learning rate evolution: {learning_rate[0]} -> {learning_rate[-1]}")
            """
        ),
        md_cell(
            """
            ## Learning rate schedule
            """
        ),
        code_cell(
            """
            fig, ax = plt.subplots(figsize=(7, 4))
            ax.plot(step, learning_rate, label="Learning rate")
            ax.set_xlabel("Step")
            ax.set_ylabel("Learning rate")
            ax.set_title("Learning rate schedule")
            ax.grid(True, alpha=0.3)
            ax.legend()
            fig.tight_layout()
            plt.show()
            """
        ),
        md_cell(
            """
            ## RMSE history
            """
        ),
        code_cell(
            """
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(step, rmse_val, label="rmse_val")
            ax.plot(step, rmse_trn, label="rmse_trn")
            ax.plot(step, rmse_e_val, label="rmse_e_val")
            ax.plot(step, rmse_e_trn, label="rmse_e_trn")
            ax.plot(step, rmse_f_val, label="rmse_f_val")
            ax.plot(step, rmse_f_trn, label="rmse_f_trn")
            ax.set_xlabel("Step")
            ax.set_ylabel("RMSE")
            ax.set_yscale("log")
            ax.set_title("DeepMD learning curve")
            ax.grid(True, alpha=0.3)
            ax.legend()
            fig.tight_layout()
            plt.show()
            """
        ),
        md_cell(
            """
            ## Final-window summary
            """
        ),
        code_cell(
            """
            print(
                f"Final energy RMSE over last {SUMMARY_WINDOW} steps (train): {rmse_e_trn[-SUMMARY_WINDOW:].mean():.8f}"
            )
            print(
                f"Final energy RMSE over last {SUMMARY_WINDOW} steps (val):   {rmse_e_val[-SUMMARY_WINDOW:].mean():.8f}"
            )
            print(
                f"Final force RMSE over last {SUMMARY_WINDOW} steps (train):  {rmse_f_trn[-SUMMARY_WINDOW:].mean():.8f}"
            )
            print(
                f"Final force RMSE over last {SUMMARY_WINDOW} steps (val):    {rmse_f_val[-SUMMARY_WINDOW:].mean():.8f}"
            )
            """
        ),
    ]


def main() -> None:
    write_notebook("data_preparation/dpdata.ipynb", build_dpdata_notebook())
    write_notebook("model_analysis/dp_inference.ipynb", build_inference_notebook())
    write_notebook("model_analysis/dp_correlation_plots.ipynb", build_correlation_notebook())
    write_notebook("model_analysis/dp_training_analysis.ipynb", build_training_notebook())


if __name__ == "__main__":
    main()
