export interface Metrics {
  speed_kmh: number;
  beta: number;
  gamma: number;
  time_dilation_ns: number;
  grav_dilation_ns: number;
  doppler_factor: number;
  simultaneity_tilt: number;
  real_dist_m: number;
  contracted_dist_m: number;
  rel_mass_kg: number;
  kinetic_energy_j: number;
  fuel_equiv_kg: number;
  schwarzschild_radius: number;
  current_radius: number;
}

export interface Position {
  lat: number;
  lon: number;
  alt: number;
  acc: number;
}

export interface DestPosition {
  lat: number;
  lon: number;
  label: string;
}

declare global {
  interface CanvasRenderingContext2D {
    roundRect: (x: number, y: number, w: number, h: number, radii: number[]) => void;
  }
}
