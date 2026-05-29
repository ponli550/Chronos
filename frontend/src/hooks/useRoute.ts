import { useState, useEffect } from 'react';
import type { Position, DestPosition } from '../types';

export interface RouteData {
  coordinates: [number, number][];
  distance: number;
  duration: number;
  steps: { instruction: string; distance: number; name: string }[];
}

export function useRoute(origin: Position | null, dest: DestPosition | null) {
  const [route, setRoute] = useState<RouteData | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!origin || !dest) {
      setRoute(null);
      return;
    }

    let cancelled = false;
    const fetchRoute = async () => {
      setLoading(true);
      try {
        const url = `https://router.project-osrm.org/route/v1/driving/${origin.lon},${origin.lat};${dest.lon},${dest.lat}?overview=full&geometries=geojson&steps=true&alternatives=false`;
        const res = await fetch(url);
        const data = await res.json();
        if (cancelled) return;
        if (!data.routes?.length) {
          setRoute(null);
          setLoading(false);
          return;
        }
        const r = data.routes[0];
        setRoute({
          coordinates: r.geometry.coordinates.map((c: [number, number]) => [c[1], c[0]]),
          distance: r.distance,
          duration: r.duration,
          steps: r.legs[0].steps.map((s: any) => ({
            instruction: s.maneuver?.instruction || s.name || '',
            distance: s.distance,
            name: s.name || '',
          })),
        });
      } catch {
        if (!cancelled) setRoute(null);
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    fetchRoute();
    return () => { cancelled = true; };
  }, [origin, dest]);

  return { route, loading };
}
