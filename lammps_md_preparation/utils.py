from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence
import random

import matplotlib.pyplot as plt
import numpy as np
from ase.atoms import Atoms
from ase.io import read, write


@dataclass(frozen=True)
class TemperatureSelection:
    """Result of filtering a trajectory against a temperature window."""
    frames: list[Atoms]
    selected_indices: list[int]
    lower_bound: float
    upper_bound: float


def ensure_parent_dir(path: str | Path) -> Path:
    """Create the parent directory for an output file if needed."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    return output_path


def sanitize_basename(path: str | Path) -> str:
    """Remove characters that are awkward in generated filenames."""
    return Path(path).name.replace(":", "_").replace(" ", "_")


def collect_poscar_files(src_dir: str | Path, pattern: str = "POSCAR*") -> list[Path]:
    """Collect POSCAR-like files from one directory using a glob pattern."""
    return sorted(Path(src_dir).glob(pattern))


def specorder_from_atoms(atoms: Atoms) -> list[str]:
    """Preserve first appearance order for deterministic LAMMPS typing."""
    seen: set[str] = set()
    order: list[str] = []
    for symbol in atoms.get_chemical_symbols():
        if symbol not in seen:
            seen.add(symbol)
            order.append(symbol)
    return order


def build_slab_supercell(
    input_poscar: str | Path,
    repeats: Sequence[int],
    vacuum: float = 0.0,
    remove_top_layer: bool = False,
    layer_tolerance: float = 0.5,
    sort_by_z: bool = True,
) -> Atoms:
    """Build a repeated slab and optionally trim the top layer."""
    atoms = read(str(input_poscar), format="vasp")
    supercell = atoms.repeat(tuple(repeats))

    if sort_by_z:
        # Sorting by z makes layer-based manipulations predictable.
        order = np.argsort(supercell.positions[:, 2])
        supercell = supercell[order]

    if remove_top_layer:
        # Remove atoms within a tolerance of the topmost z coordinate.
        z_values = supercell.positions[:, 2]
        keep_mask = z_values < (z_values.max() - layer_tolerance)
        supercell = supercell[keep_mask]

    if vacuum > 0.0:
        supercell.center(vacuum=vacuum, axis=2)

    return supercell


def write_lammps_data_file(
    atoms: Atoms,
    output_path: str | Path,
    specorder: Sequence[str] | None = None,
    atom_style: str = "atomic",
    units: str = "metal",
    write_velocities: bool = True,
) -> Path:
    """Write one ASE structure as a LAMMPS data file."""
    output_path = ensure_parent_dir(output_path)
    atoms_to_write = atoms.copy()
    effective_specorder = list(specorder) if specorder is not None else specorder_from_atoms(atoms_to_write)

    kwargs: dict[str, object] = {
        "filename": str(output_path),
        "images": atoms_to_write,
        "format": "lammps-data",
        "atom_style": atom_style,
        "units": units,
        "specorder": effective_specorder,
    }
    if write_velocities and atoms_to_write.get_velocities() is not None:
        # ASE writes velocities in the target LAMMPS data-file section format.
        kwargs["velocities"] = True

    write(**kwargs)
    return output_path


def rewrite_lammps_atom_types(
    input_path: str | Path,
    output_path: str | Path,
    atom_type_count: int | None = None,
    atom_type_value: int | None = None,
    atom_type_map: Mapping[int, int] | None = None,
) -> Path:
    """Rewrite atom types in a LAMMPS data file without touching coordinates."""
    if atom_type_value is None and atom_type_map is None and atom_type_count is None:
        raise ValueError("Provide at least one of atom_type_count, atom_type_value, or atom_type_map.")
    if atom_type_value is not None and atom_type_map is not None:
        raise ValueError("atom_type_value and atom_type_map are mutually exclusive.")

    input_path = Path(input_path)
    output_path = ensure_parent_dir(output_path)
    lines = input_path.read_text().splitlines(keepends=True)

    rewritten_lines: list[str] = []
    in_atoms_section = False

    for line in lines:
        stripped = line.strip()

        if atom_type_count is not None and stripped.endswith("atom types"):
            # Update the header if downstream inputs expect a larger type table.
            parts = stripped.split()
            parts[0] = str(atom_type_count)
            rewritten_lines.append(" ".join(parts) + "\n")
            continue

        if stripped.startswith("Atoms"):
            in_atoms_section = True
            rewritten_lines.append(line)
            continue

        if in_atoms_section:
            if not stripped:
                rewritten_lines.append(line)
                continue

            if stripped[0].isalpha():
                # Another section starts here, so stop rewriting atom rows.
                in_atoms_section = False
                rewritten_lines.append(line)
                continue

            parts = line.split()
            if len(parts) >= 2:
                current_type = int(parts[1])
                if atom_type_value is not None:
                    # Force every atom to a single type id.
                    parts[1] = str(atom_type_value)
                elif atom_type_map is not None and current_type in atom_type_map:
                    # Rewrite only the requested type ids.
                    parts[1] = str(atom_type_map[current_type])
                rewritten_lines.append(" ".join(parts) + "\n")
                continue

        rewritten_lines.append(line)

    output_path.write_text("".join(rewritten_lines))
    return output_path


def read_lammps_temperature_log(log_file: str | Path) -> tuple[list[int], list[float]]:
    """Parse the first thermo table containing Step and Temp columns."""
    log_file = Path(log_file)
    timesteps: list[int] = []
    temperatures: list[float] = []
    reading_table = False
    step_column = None
    temp_column = None

    with log_file.open() as handle:
        for raw_line in handle:
            stripped = raw_line.strip()
            if not stripped:
                if reading_table and timesteps:
                    break
                continue

            parts = stripped.split()
            if "Step" in parts and "Temp" in parts:
                # Record the thermo column positions instead of assuming fixed indices.
                reading_table = True
                step_column = parts.index("Step")
                temp_column = parts.index("Temp")
                continue

            if not reading_table:
                continue

            if stripped.startswith("Loop time"):
                break

            if step_column is None or temp_column is None:
                raise ValueError(f"Failed to detect Step/Temp columns in {log_file}")

            if len(parts) <= max(step_column, temp_column):
                continue

            try:
                timesteps.append(int(float(parts[step_column])))
                temperatures.append(float(parts[temp_column]))
            except ValueError:
                continue

    if not timesteps:
        raise ValueError(f"No temperature table found in {log_file}")
    return timesteps, temperatures


def summarise_temperatures(temperatures: Sequence[float]) -> dict[str, float]:
    """Return common descriptive statistics for a temperature series."""
    values = np.asarray(temperatures, dtype=float)
    if values.size == 0:
        raise ValueError("Temperature series is empty.")
    return {
        "count": float(values.size),
        "mean": float(np.mean(values)),
        "median": float(np.median(values)),
        "min": float(np.min(values)),
        "max": float(np.max(values)),
        "std": float(np.std(values)),
        "variance": float(np.var(values)),
        "p25": float(np.percentile(values, 25)),
        "p75": float(np.percentile(values, 75)),
    }


def plot_temperature_series(
    timesteps: Sequence[int],
    temperatures: Sequence[float],
    title: str = "Temperature Evolution",
):
    """Plot temperature evolution together with summary reference lines."""
    stats = summarise_temperatures(temperatures)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(timesteps, temperatures, label="Temperature", color="tab:blue")
    ax.axhline(stats["mean"], color="tab:red", linestyle="--", label=f"Mean: {stats['mean']:.2f}")
    ax.axhline(stats["median"], color="tab:green", linestyle="-.", label=f"Median: {stats['median']:.2f}")
    ax.axhline(stats["p25"], color="tab:purple", linestyle=":", label=f"25th %: {stats['p25']:.2f}")
    ax.axhline(stats["p75"], color="tab:orange", linestyle=":", label=f"75th %: {stats['p75']:.2f}")
    ax.set_xlabel("Timestep")
    ax.set_ylabel("Temperature")
    ax.set_title(title)
    ax.legend(loc="best")

    stats_text = "\n".join(
        [
            f"Count: {int(stats['count'])}",
            f"Mean: {stats['mean']:.3f}",
            f"Median: {stats['median']:.3f}",
            f"Min: {stats['min']:.3f}",
            f"Max: {stats['max']:.3f}",
            f"Std: {stats['std']:.3f}",
            f"Var: {stats['variance']:.3f}",
            f"25th %: {stats['p25']:.3f}",
            f"75th %: {stats['p75']:.3f}",
        ]
    )
    ax.text(
        0.99,
        0.01,
        stats_text,
        fontsize=10,
        color="black",
        verticalalignment="bottom",
        horizontalalignment="right",
        transform=ax.transAxes,
        bbox={"facecolor": "white", "alpha": 0.7, "edgecolor": "gray"},
    )
    fig.tight_layout()
    return fig, ax, stats


def select_frames_by_temperature(
    trajectory: Sequence[Atoms],
    temperatures: Sequence[float],
    start_index: int = 0,
    end_index: int | None = None,
    use_percentile_window: bool = False,
    lower_percentile: float = 25.0,
    upper_percentile: float = 75.0,
) -> TemperatureSelection:
    """Select frames inside either a full or percentile-based temperature window."""
    if len(trajectory) != len(temperatures):
        raise ValueError("Trajectory length does not match the number of temperatures.")

    if end_index is None:
        end_index = len(trajectory)
    if start_index < 0 or end_index > len(trajectory) or start_index >= end_index:
        raise ValueError("Invalid frame selection bounds.")

    window = np.asarray(temperatures[start_index:end_index], dtype=float)
    if window.size == 0:
        raise ValueError("Temperature selection window is empty.")

    if use_percentile_window:
        # Restrict the selection to the inter-percentile band of the chosen window.
        lower_bound = float(np.percentile(window, lower_percentile))
        upper_bound = float(np.percentile(window, upper_percentile))
    else:
        lower_bound = float(window.min())
        upper_bound = float(window.max())

    selected_indices = [
        index
        for index in range(start_index, end_index)
        if lower_bound <= float(temperatures[index]) <= upper_bound
    ]
    frames = [trajectory[index] for index in selected_indices]
    return TemperatureSelection(
        frames=frames,
        selected_indices=selected_indices,
        lower_bound=lower_bound,
        upper_bound=upper_bound,
    )


def random_sample_frames(frames: Sequence[Atoms], n_frames: int, seed: int | None = None) -> list[Atoms]:
    """Shuffle frames reproducibly and optionally truncate to n_frames."""
    if n_frames < 0:
        raise ValueError("n_frames must be non-negative.")
    frames_copy = list(frames)
    rng = random.Random(seed)
    rng.shuffle(frames_copy)
    if n_frames == 0:
        return frames_copy
    return frames_copy[: min(n_frames, len(frames_copy))]


def set_component_for_atom_indices(
    atoms: Atoms,
    atom_indices: Iterable[int],
    component: int,
    value: float = 0.0,
) -> Atoms:
    """Set one Cartesian component to a fixed value for selected atoms."""
    positions = atoms.get_positions(copy=True)
    for atom_index in atom_indices:
        positions[atom_index, component] = value
    atoms.set_positions(positions)
    return atoms


def recenter_first_atom_to_xy_center(atoms: Atoms) -> Atoms:
    """Translate the structure so atom 0 sits at the xy center of the cell."""
    recentered = atoms.copy()
    cell = recentered.get_cell()
    center_xy = (cell[0][:2] + cell[1][:2]) / 2.0
    first_atom_xy = recentered.get_positions()[0][:2]
    translation = np.array([*(center_xy - first_atom_xy), 0.0], dtype=float)
    recentered.translate(translation)
    recentered.set_pbc([True, True, False])
    recentered.wrap()
    return recentered


def write_possur(output_file: str | Path, trajectory: Sequence[Atoms]) -> Path:
    """Write fractional coordinates frame by frame for downstream surface codes."""
    output_file = ensure_parent_dir(output_file)
    with output_file.open("w") as handle:
        for atoms in trajectory:
            positions = atoms.get_positions()
            # Use ASE's scaled coordinates directly to avoid manual matrix inversion.
            fractional = atoms.get_scaled_positions(wrap=False)
            if positions is None:
                raise ValueError("Positions are not present in the trajectory.")
            for vector in fractional:
                handle.write(f"{vector[0]:15.10f} {vector[1]:15.10f} {vector[2]:15.10f}\n")
    return output_file


def write_velsur(
    output_file: str | Path,
    trajectory: Sequence[Atoms],
    velocity_scale: float = 1.0,
    zero_velocity_indices: Iterable[int] | None = None,
) -> Path:
    """Write velocities frame by frame after optional zeroing and rescaling."""
    output_file = ensure_parent_dir(output_file)
    zero_velocity_indices = list(zero_velocity_indices or [])

    with output_file.open("w") as handle:
        for atoms in trajectory:
            velocities = atoms.get_velocities()
            if velocities is None:
                raise ValueError("Velocities are not present in the trajectory.")
            velocities_to_write = velocities.copy()
            if zero_velocity_indices:
                # Freeze chosen atoms in the exported file without altering the source frame.
                velocities_to_write[zero_velocity_indices] = 0.0
            # `velocity_scale` is a unit-conversion factor, not a timestep.
            velocities_to_write *= velocity_scale
            for vector in velocities_to_write:
                handle.write(f"{vector[0]:15.10f} {vector[1]:15.10f} {vector[2]:15.10f}\n")
    return output_file
