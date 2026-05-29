import os
from fastapi import FastAPI, WebSocket, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import numpy as np
from math import radians, cos, sin, asin, sqrt
from pathlib import Path

from labs.registry import scan_labs
from labs.runner import get_sim_params, run_simulation, check_dependencies

SIMULATIONS_DIR = Path(
    os.environ.get(
        "SIMULATIONS_DIR",
        Path(__file__).resolve().parent.parent / "simulations",
    )
)

app = FastAPI(title="Chronos-X API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

C = 299792458
G = 6.67430e-11
M_EARTH = 5.972e24
R_EARTH = 6371000
M_SAG_A = 4.154e6 * 1.989e30
M_CAR = 1500


class EtaWavepacket(BaseModel):
    t: list[float]
    prob: list[float]


class Metrics(BaseModel):
    gamma: float
    beta: float
    time_dilation_ns: float
    grav_dilation_ns: float
    doppler_factor: float
    contracted_dist_m: float
    real_dist_m: float
    rel_mass_kg: float
    kinetic_energy_j: float
    fuel_equiv_kg: float
    simultaneity_tilt: float
    speed_kmh: float
    altitude: float = 0
    is_black_hole: bool = False
    schwarzschild_radius: float
    current_radius: float
    eta_wavepacket: EtaWavepacket


class PhysicsEngine:
    def __init__(self) -> None:
        self.c = C

    @staticmethod
    def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        return 2 * asin(sqrt(a)) * 6371000

    def calculate_metrics(
        self,
        speed_mps: float,
        user_coords: list[float] | None = None,
        dest_coords: list[float] | None = None,
        manual_dist: float = 50000,
        is_black_hole: bool = False,
        proximity_factor: float = 1.0,
        altitude: float = 0,
    ) -> Metrics:
        speed_mps = min(speed_mps, self.c - 1)

        beta = speed_mps / self.c
        gamma = 1.0 / np.sqrt(1.0 - beta ** 2)
        time_dilation_ns = (1.0 - 1.0 / gamma) * 1e9

        if is_black_hole:
            mass = M_SAG_A
            rs = 2 * G * mass / self.c ** 2
            radius = rs * (1.0001 + proximity_factor * 9)
        else:
            mass = M_EARTH
            radius = R_EARTH + altitude
            rs = 2 * G * mass / self.c ** 2

        grav_factor = np.sqrt(max(0, 1 - rs / radius))
        grav_dilation_ns = (1.0 - grav_factor) * 1e9

        doppler_factor = np.sqrt((1 + beta) / (1 - beta)) if beta > 0 else 1.0
        rel_mass = gamma * M_CAR
        kinetic_energy_j = (gamma - 1) * M_CAR * self.c ** 2
        fuel_equiv_kg = kinetic_energy_j / self.c ** 2

        if user_coords and dest_coords:
            dist_m = self.haversine(user_coords[0], user_coords[1], dest_coords[0], dest_coords[1])
        else:
            dist_m = manual_dist

        contracted_dist = dist_m / gamma

        speed_safe = max(speed_mps, 0.001)
        dist_safe = max(dist_m, 1)
        delta_v = max(speed_safe * 0.05, 0.1)
        avg_eta = dist_safe / speed_safe
        delta_t = min(dist_safe / speed_safe ** 2 * delta_v, 3600)

        t_vals = np.linspace(max(0.1, avg_eta - 3 * delta_t), avg_eta + 3 * delta_t, 50)
        prob = np.exp(-(t_vals - avg_eta) ** 2 / (2 * delta_t ** 2))
        integral = np.trapezoid(prob, t_vals)
        if integral > 0:
            prob /= integral

        return Metrics(
            gamma=float(gamma),
            beta=float(beta),
            time_dilation_ns=float(time_dilation_ns),
            grav_dilation_ns=float(grav_dilation_ns),
            doppler_factor=float(doppler_factor),
            contracted_dist_m=float(contracted_dist),
            real_dist_m=float(dist_m),
            rel_mass_kg=float(rel_mass),
            kinetic_energy_j=float(kinetic_energy_j),
            fuel_equiv_kg=float(fuel_equiv_kg),
            simultaneity_tilt=float(beta),
            speed_kmh=float(speed_mps * 3.6),
            altitude=float(altitude),
            is_black_hole=is_black_hole,
            schwarzschild_radius=float(rs),
            current_radius=float(radius),
            eta_wavepacket=EtaWavepacket(t=t_vals.tolist(), prob=prob.tolist()),
        )


engine = PhysicsEngine()

# Serve simulation images statically
if SIMULATIONS_DIR.exists():
    app.mount("/simulations", StaticFiles(directory=str(SIMULATIONS_DIR)), name="simulations")


@app.get("/")
def read_root():
    return {"message": "Project Chronos-X Backend API"}


@app.get("/health")
def health():
    return {"status": "ok"}


# ---- Labs ----

@app.get("/labs")
def list_labs(category: str | None = None):
    labs = scan_labs()
    if category:
        labs = [l for l in labs if l.category.lower() == category.lower()]
    categories = sorted({l.category for l in labs})
    return {
        "categories": categories,
        "labs": [
            {
                "id": l.id,
                "name": l.name,
                "description": l.description,
                "category": l.category,
                "images": l.images,
            }
            for l in labs
        ],
    }


@app.get("/labs/{lab_id}")
def get_lab(lab_id: str):
    labs = scan_labs()
    for l in labs:
        if l.id == lab_id:
            return {
                "id": l.id,
                "name": l.name,
                "description": l.description,
                "category": l.category,
                "images": l.images,
                "functions": l.functions,
                "main_function": l.main_function,
            }
    from fastapi import HTTPException
    raise HTTPException(status_code=404, detail="Lab not found")


@app.get("/labs/status")
def labs_status():
    deps = check_dependencies()
    labs = scan_labs()
    return {
        "total_labs": len(labs),
        "categories": sorted({l.category for l in labs}),
        "dependencies": deps,
    }


@app.get("/labs/{lab_id}/params")
def lab_params(lab_id: str):
    params = get_sim_params(lab_id)
    if params is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Lab not found")
    return {"parameters": params}


@app.post("/labs/{lab_id}/run")
async def run_lab(lab_id: str, params: dict = {}):
    result = run_simulation(lab_id, params)
    return result


@app.get("/labs/{lab_id}/source")
def lab_source(lab_id: str):
    import os
    labs = scan_labs()
    for l in labs:
        if l.id == lab_id:
            source_path = os.path.join(SIMULATIONS_DIR, l.filename)
            if os.path.exists(source_path):
                with open(source_path, "r") as f:
                    content = f.read()
                return {"source": content, "filename": l.filename}
    from fastapi import HTTPException
    raise HTTPException(status_code=404, detail="Lab not found")


@app.get("/compute", response_model=Metrics)
def compute(
    speed: float = Query(default=0, ge=0, description="Speed in m/s"),
    ulat: float | None = Query(default=None, description="User latitude"),
    ulon: float | None = Query(default=None, description="User longitude"),
    dlat: float | None = Query(default=None, description="Destination latitude"),
    dlon: float | None = Query(default=None, description="Destination longitude"),
    alt: float = Query(default=0, ge=0, description="Altitude in meters"),
    dist: float = Query(default=50000, ge=1, description="Manual distance in meters"),
    bh: bool = Query(default=False, description="Black hole mode"),
    prox: float = Query(default=1.0, ge=0, le=1, description="Black hole proximity (0=event horizon, 1=far orbit)"),
):
    user_coords = [ulat, ulon] if ulat is not None and ulon is not None else None
    dest_coords = [dlat, dlon] if dlat is not None and dlon is not None else None
    return engine.calculate_metrics(speed, user_coords, dest_coords, dist, bh, prox, alt)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        try:
            data = await websocket.receive_json()
            speed = data.get("speed", 0)
            dist = data.get("dist", 50000)
            bh = data.get("bh", False)
            prox = data.get("prox", 1.0)
            alt = data.get("alt", 0)
            metrics = engine.calculate_metrics(
                speed,
                manual_dist=dist,
                is_black_hole=bh,
                proximity_factor=prox,
                altitude=alt,
            )
            await websocket.send_json(metrics.model_dump())
        except Exception:
            break
