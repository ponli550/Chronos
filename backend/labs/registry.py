import ast
import os
import time
from pathlib import Path
from dataclasses import dataclass, field

SIMULATIONS_DIR = Path(
    os.environ.get(
        "SIMULATIONS_DIR",
        Path(__file__).resolve().parent.parent.parent / "simulations",
    )
)

SIM_CATEGORIES: dict[str, str] = {
    "hydrogen_atom": "Quantum Mechanics",
    "qho": "Quantum Mechanics",
    "helium_atom": "Quantum Mechanics",
    "tunneling": "Quantum Mechanics",
    "tdse_2d": "Quantum Mechanics",
    "solid_state": "Condensed Matter",
    "exchange_interaction": "Many-Body Physics",
    "bells_theorem": "Quantum Information",
    "quantum_computing": "Quantum Computing",
    "qft": "Quantum Computing",
    "qft_klein_gordon": "Quantum Field Theory",
    "qec": "Quantum Error Correction",
    "quantum_teleportation": "Quantum Computing",
    "vqe_molecule": "Quantum Computing",
    "qcnn_research": "Quantum AI",
    "dirac_equation": "Relativistic QM",
    "path_integral": "Quantum Foundations",
    "quantum_eraser": "Quantum Foundations",
    "multiverse": "Quantum Foundations",
    "aharonov_bohm": "Quantum Foundations",
    "berry_phase": "Condensed Matter",
    "ssh_topology": "Topological Matter",
    "majorana_fermions": "Topological Matter",
    "lattice_gauge": "Gauge Theories",
    "non_hermitian": "Non-Hermitian Physics",
    "susy_quantum": "Theoretical Physics",
    "higgs_mechanism": "Particle Physics",
    "beta_decay": "Nuclear Physics",
    "nuclear_fusion": "Nuclear Physics",
    "quark_confinement": "Particle Physics",
    "quantum_optics": "Quantum Optics",
    "rabi_oscillations": "Quantum Optics",
    "quantum_biology": "Quantum Biology",
    "quantum_chaos": "Quantum Chaos",
    "quantum_scars": "Quantum Chaos",
    "mbl_localization": "Many-Body Physics",
    "time_crystal": "Many-Body Physics",
    "quantum_simulation_heisenberg": "Many-Body Physics",
    "quantum_engine": "Quantum Thermodynamics",
    "maxwell_demon": "Quantum Thermodynamics",
    "tech_quantum_battery": "Quantum Technology",
    "quantum_sensing": "Quantum Technology",
    "quantum_game_theory": "Quantum Information",
    "quantum_ml": "Quantum AI",
    "open_systems": "Open Quantum Systems",
    "syk_holography": "Quantum Gravity",
    "wormhole_epr": "Quantum Gravity",
    "quantum_gravity": "Quantum Gravity",
    "black_hole_quantum": "Quantum Gravity",
    "hawking_radiation": "Quantum Gravity",
    "gravitational_waves": "Cosmology",
    "cosmology_cmb": "Cosmology",
    "invisibility_cloak": "Metamaterials",
    "grav_lensing": "Relativity",
    "cern_collision": "Particle Physics",
    "muon_decay_proof": "Nuclear Physics",
    "quantum_satellite": "Quantum Technology",
    "superconductivity": "Condensed Matter",
    "dft_nanowire": "Condensed Matter",
    "complex_atoms": "Atomic Physics",
    "new_elemental": "Nuclear Physics",
    "bec_superfluid": "Condensed Matter",
    "agentic_ai_qac": "Quantum AI",
    "interactive_lab": "Labs",
}

EXCLUDE_FILES = {
    "__init__.py", "generate_report.py",
}


@dataclass
class LabInfo:
    id: str
    name: str
    description: str
    category: str
    images: list[str] = field(default_factory=list)
    functions: list[str] = field(default_factory=list)
    main_function: str | None = None


_cache: list[LabInfo] | None = None
_cache_time: float = 0
_CACHE_TTL = 30.0


def scan_labs(force: bool = False) -> list[LabInfo]:
    global _cache, _cache_time
    now = time.time()
    if not force and _cache is not None and (now - _cache_time) < _CACHE_TTL:
        return _cache

    labs: list[LabInfo] = []

    if not SIMULATIONS_DIR.exists():
        return labs

    for py_file in sorted(SIMULATIONS_DIR.glob("*.py"), key=_sort_key):
        if py_file.name in EXCLUDE_FILES:
            continue

        stem = py_file.stem

        description = ""
        functions = []
        try:
            with open(py_file) as f:
                tree = ast.parse(f.read())
            description = ast.get_docstring(tree) or ""
            if description:
                description = description.split("\n")[0].strip()

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
                    functions.append(node.name)
        except (SyntaxError, Exception):
            pass

        if not description:
            description = f"Simulation of {stem.replace('_', ' ')}"

        main_function = next(
            (f for f in functions if f.startswith(("simulate_", "solve_", "run_", "compute_"))),
            functions[0] if functions else None,
        )

        images = sorted(
            img.name for img in SIMULATIONS_DIR.glob(f"{stem}.*")
            if img.suffix in {".png", ".gif"}
        )

        labs.append(LabInfo(
            id=stem,
            name=stem.replace("_", " ").title(),
            description=description,
            category=SIM_CATEGORIES.get(stem, "Uncategorized"),
            images=images,
            functions=functions,
            main_function=main_function,
        ))

    _cache = labs
    _cache_time = now
    return labs


def _sort_key(path: Path) -> tuple:
    stem = path.stem
    cat = SIM_CATEGORIES.get(stem, "Uncategorized")
    return (cat, stem)
