import 'leaflet/dist/leaflet.css';
import { Component, createContext, type ErrorInfo, type ReactNode, useCallback, useContext, useEffect, useRef, useState } from 'react';
import { Activity, ChevronDown, ChevronUp, CircleAlert, Download, Flame, Gauge, Ruler, ShieldAlert, Timer, Volume2, VolumeX, Zap } from 'lucide-react';
import { Circle, MapContainer, Marker, Polyline, Popup, TileLayer, useMap, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import type { DestPosition, Metrics, Position } from './types';
import type { RouteData } from './hooks';

/* Consolidated — all components inlined */

interface AboutPanelProps {
  open: boolean;
  onClose: () => void;
}

const deps = [
  { name: 'React 18', desc: 'UI framework' },
  { name: 'TypeScript', desc: 'Type safety' },
  { name: 'Vite 5', desc: 'Build tool' },
  { name: 'Tailwind CSS', desc: 'Styling' },
  { name: 'Recharts', desc: 'Charts' },
  { name: 'Leaflet', desc: 'Maps' },
  { name: 'Lucide', desc: 'Icons' },
  { name: 'FastAPI', desc: 'Backend API' },
  { name: 'NumPy/SciPy', desc: 'Scientific computing' },
  { name: 'QuTiP', desc: 'Quantum simulations' },
  { name: 'matplotlib', desc: 'Plotting' },
];

export function AboutPanel({ open, onClose }: AboutPanelProps) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center" onClick={onClose}>
      <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" />
      <div
        className="relative card p-6 max-w-md w-full mx-4 space-y-5"
        onClick={e => e.stopPropagation()}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-cyan-400 flex items-center justify-center shadow-[0_0_16px_-4px_#3b82f6]">
              <span className="text-white font-bold text-xs">X</span>
            </div>
            <div>
              <h2 className="font-bold text-sm text-slate-100">CHRONOS-X</h2>
              <p className="text-[8px] text-slate-500 uppercase tracking-[0.2em]">Relativistic Dashboard v1.0</p>
            </div>
          </div>
          <button onClick={onClose} className="text-[10px] text-slate-500 hover:text-slate-300 font-mono">✕</button>
        </div>

        <p className="text-[10px] text-slate-500 leading-relaxed">
          A real-time relativistic physics dashboard that combines GPS tracking, special/general relativity
          simulations, and interactive visualizations. Explore time dilation, length contraction, Doppler shift,
          and black hole physics through an immersive sci-fi HUD.
        </p>

        <div>
          <p className="text-[8px] uppercase tracking-[0.2em] text-slate-600 mb-2">Technology Stack</p>
          <div className="grid grid-cols-2 gap-x-4 gap-y-1.5">
            {deps.map(d => (
              <div key={d.name} className="flex items-center gap-2 text-[9px] font-mono">
                <span className="text-blue-400">▸</span>
                <span className="text-slate-400">{d.name}</span>
                <span className="text-slate-700 ml-auto">{d.desc}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="pt-3 border-t border-slate-800/50 text-[7px] text-slate-700 font-mono text-center">
          68 simulation scripts · 0 errors · Built with science
        </div>
      </div>
    </div>
  );
}


const SI_PREFIXES = [
  { min: 1e15, sym: 'P' }, { min: 1e12, sym: 'T' },
  { min: 1e9, sym: 'G' }, { min: 1e6, sym: 'M' },
  { min: 1e3, sym: 'k' }, { min: 1, sym: '' },
  { min: 1e-3, sym: 'm' }, { min: 1e-6, sym: 'µ' },
  { min: 1e-9, sym: 'n' }, { min: 1e-12, sym: 'p' },
];

function formatSI(value: number, decimals: number): { display: number; prefix: string } {
  const abs = Math.abs(value);
  for (const p of SI_PREFIXES) {
    if (abs >= p.min) return { display: value / p.min, prefix: p.sym };
  }
  return { display: value, prefix: '' };
}

interface AnimatedValueProps {
  value: number;
  decimals?: number;
  unit?: string;
  color?: string;
  compact?: boolean;
  si?: boolean;
}

export function AnimatedValue({ value, decimals = 2, unit = '', color = '#3b82f6', compact = false, si = true }: AnimatedValueProps) {
  const [display, setDisplay] = useState(value);
  const frameRef = useRef<number>(0);
  const startRef = useRef(display);
  const targetRef = useRef(value);
  const startTime = useRef(Date.now());

  useEffect(() => {
    if (value === targetRef.current && Math.abs(display - value) < 0.001) return;
    targetRef.current = value;
    startRef.current = display;
    startTime.current = Date.now();
    cancelAnimationFrame(frameRef.current);

    const animate = () => {
      const elapsed = Date.now() - startTime.current;
      const dur = 400;
      const t = Math.min(elapsed / dur, 1);
      const eased = 1 - Math.pow(1 - t, 3);
      const current = startRef.current + (targetRef.current - startRef.current) * eased;
      setDisplay(current);
      if (t < 1) frameRef.current = requestAnimationFrame(animate);
    };
    frameRef.current = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(frameRef.current);
  }, [value]);

  const { display: dispVal, prefix } = si ? formatSI(display, decimals) : { display, prefix: '' };
  const formatted = dispVal.toFixed(decimals);
  const intDigits = formatted.split('.')[0];
  const fracDigits = decimals > 0 ? formatted.split('.')[1] : '';

  const size = compact ? 'text-sm' : 'text-xl';
  const unitSize = compact ? 'text-[9px]' : 'text-[9px]';

  return (
    <span className={`font-mono font-bold tracking-tight ${size}`} style={{ color }}>
      <span className="value-digit">{intDigits}</span>
      {fracDigits && <span className="value-digit text-[0.7em] opacity-60">.{fracDigits}</span>}
      {prefix && <span className="text-[0.7em] opacity-60">{prefix}</span>}
      {unit && <span className={`${unitSize} ml-0.5 font-normal tracking-wider opacity-50`}>{prefix}{unit}</span>}
    </span>
  );
}


interface AudioVisualizerProps {
  active: boolean;
  gamma: number;
}

export function AudioVisualizer({ active, gamma }: AudioVisualizerProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const W = 200, H = 48;
    canvas.width = W;
    canvas.height = H;

    const bars = 32;
    let frame: number;
    let t = 0;

    const animate = () => {
      t += 0.03;
      ctx.clearRect(0, 0, W, H);

      const bw = (W - bars) / bars;
      const spread = active ? 1 : 0.08;
      const speed = active ? 1 / Math.max(gamma, 0.01) : 0.3;

      for (let i = 0; i < bars; i++) {
        const phase = (i / bars) * Math.PI * 2;
        const envelope = 1 - Math.abs(i / bars - 0.5) * 1.2;
        const h = Math.max(
          1,
          (H * 0.15 + H * 0.6 * envelope *
            (0.5 + 0.5 * Math.sin(t * speed * 6 + phase * 2)) +
            H * 0.2 * envelope * Math.sin(t * speed * 13 + phase * 3.7) +
            H * 0.15 * envelope * Math.random() * spread) *
          (active ? 1 : 0.3)
        );

        const x = i * (bw + 1);
        const y = (H - h) / 2;

        const grad = ctx.createLinearGradient(x, y, x, y + h);
        grad.addColorStop(0, `hsla(${210 + i * 1.5}, 80%, 60%, ${active ? 0.8 : 0.2})`);
        grad.addColorStop(0.5, `hsla(${230 + i * 1.5}, 80%, 45%, ${active ? 0.6 : 0.15})`);
        grad.addColorStop(1, `hsla(${250 + i * 1.5}, 70%, 35%, ${active ? 0.4 : 0.1})`);

        ctx.fillStyle = grad;
        ctx.beginPath();
        ctx.roundRect(x, y, bw, h, [1, 1, 0, 0]);
        ctx.fill();
      }

      frame = requestAnimationFrame(animate);
    };
    animate();

    return () => cancelAnimationFrame(frame);
  }, [active, gamma]);

  return (
    <canvas
      ref={canvasRef}
      className="w-full h-12 rounded-lg"
      style={{ background: 'transparent' }}
    />
  );
}


export function AuroraBackground() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resize();
    window.addEventListener('resize', resize);

    let frame: number;
    let time = 0;

    const bands = 5;
    const bandData = Array.from({ length: bands }, () => ({
      speed: 0.1 + Math.random() * 0.2,
      offset: Math.random() * Math.PI * 2,
      height: 0.15 + Math.random() * 0.25,
      width: 0.3 + Math.random() * 0.4,
      hue: 160 + Math.random() * 100,
    }));

    const animate = () => {
      time += 0.002;
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Subtle base gradient
      const baseGrad = ctx.createLinearGradient(0, 0, 0, canvas.height);
      baseGrad.addColorStop(0, 'rgba(10, 15, 30, 0.3)');
      baseGrad.addColorStop(1, 'rgba(5, 8, 15, 0.1)');
      ctx.fillStyle = baseGrad;
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      for (const band of bandData) {
        const bandHeight = canvas.height * band.height;
        const bandTop = canvas.height * (0.05 + Math.random() * 0.02);
        const bandWidth = canvas.width * band.width;
        const bandLeft = (canvas.width - bandWidth) * 0.3;

        ctx.globalAlpha = 0.12 + 0.06 * Math.sin(time * band.speed + band.offset);

        for (let strip = 0; strip < 30; strip++) {
          const progress = strip / 30;
          const xOffset = Math.sin(time * band.speed * 2 + progress * 8 + band.offset) * bandWidth * 0.15;
          const yOffset = Math.sin(time * band.speed + progress * 5 + band.offset * 2) * bandHeight * 0.2;

          const x = bandLeft + progress * bandWidth + xOffset;
          const y = bandTop + progress * bandHeight * 0.5 + yOffset;

          const gradient = ctx.createLinearGradient(x - 40, y - 20, x + 40, y + bandHeight * 0.4);

          const alpha = 0.15 + 0.3 * (1 - Math.abs(progress - 0.5) * 1.2);
          const hueShift = Math.sin(time * band.speed + progress * 3) * 20;

          gradient.addColorStop(0, `hsla(${band.hue + hueShift}, 80%, 50%, 0)`);
          gradient.addColorStop(0.3, `hsla(${band.hue + hueShift + 10}, 80%, 55%, ${alpha * 0.3})`);
          gradient.addColorStop(0.5, `hsla(${band.hue + hueShift + 20}, 80%, 60%, ${alpha * 0.5})`);
          gradient.addColorStop(0.7, `hsla(${band.hue + hueShift + 10}, 80%, 55%, ${alpha * 0.3})`);
          gradient.addColorStop(1, `hsla(${band.hue + hueShift}, 80%, 50%, 0)`);

          ctx.fillStyle = gradient;
          ctx.beginPath();
          ctx.moveTo(x - 80, y - 15);
          ctx.quadraticCurveTo(x, y - 30 - Math.sin(time * 0.5 + strip) * 10, x + 80, y - 15);
          ctx.quadraticCurveTo(x, y + 20, x - 80, y - 15);
          ctx.fill();
        }

        ctx.globalAlpha = 1;
      }

      // Vertical light shafts
      ctx.globalAlpha = 0.03;
      for (let i = 0; i < 8; i++) {
        const sx = canvas.width * (0.1 + Math.random() * 0.8);
        const sw = 20 + Math.random() * 60;
        const grad = ctx.createLinearGradient(sx, 0, sx + sw, 0);
        grad.addColorStop(0, 'transparent');
        grad.addColorStop(0.5, 'rgba(150, 200, 255, 0.3)');
        grad.addColorStop(1, 'transparent');
        ctx.fillStyle = grad;
        ctx.fillRect(sx, 0, sw, canvas.height * 0.4);
      }
      ctx.globalAlpha = 1;

      frame = requestAnimationFrame(animate);
    };
    animate();

    return () => {
      cancelAnimationFrame(frame);
      window.removeEventListener('resize', resize);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 pointer-events-none z-[1]"
      style={{ opacity: 0.5 }}
    />
  );
}


interface BlackHoleVisualProps {
  proximity: number; // 0 = deep orbit, 1 = event horizon
}

interface Particle {
  x: number; y: number; angle: number; radius: number;
  speed: number; size: number; alpha: number;
}

export function BlackHoleVisual({ proximity }: BlackHoleVisualProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const W = 280, H = 200;
    canvas.width = W;
    canvas.height = H;
    const cx = W / 2, cy = H / 2;
    const horizonR = 14;

    const particles: Particle[] = [];
    for (let i = 0; i < 60; i++) {
      const angle = Math.random() * Math.PI * 2;
      const radius = horizonR * 1.5 + Math.random() * (W * 0.4);
      particles.push({
        x: cx + radius * Math.cos(angle),
        y: cy + radius * Math.sin(angle),
        angle, radius,
        speed: 0.002 + Math.random() * 0.008,
        size: 0.5 + Math.random() * 1.5,
        alpha: 0.1 + Math.random() * 0.3,
      });
    }

    let frame: number;
    const animate = () => {
      ctx.clearRect(0, 0, W, H);

      // Outer glow
      const outerGlow = ctx.createRadialGradient(cx, cy, horizonR, cx, cy, W * 0.45);
      const glowIntensity = 0.15 + proximity * 0.35;
      outerGlow.addColorStop(0, `rgba(200, 100, 50, ${glowIntensity * 0.4})`);
      outerGlow.addColorStop(0.3, `rgba(200, 80, 30, ${glowIntensity * 0.2})`);
      outerGlow.addColorStop(1, 'transparent');
      ctx.fillStyle = outerGlow;
      ctx.fillRect(0, 0, W, H);

      // Gravitational lensing rings
      const ringCount = 3 + Math.floor(proximity * 4);
      for (let i = 0; i < ringCount; i++) {
        const r = horizonR * (1.8 + i * 1.2 + proximity * 0.5);
        const alpha = 0.08 + (1 - i / ringCount) * 0.12 * proximity;
        ctx.beginPath();
        ctx.arc(cx, cy, r, 0, Math.PI * 2);
        ctx.strokeStyle = `rgba(255, 180, 100, ${alpha})`;
        ctx.lineWidth = 1 + (1 - i / ringCount) * 1.5;
        ctx.stroke();
      }

      // Accretion disk (elliptical glow)
      for (let ring = 0; ring < 8; ring++) {
        const r = horizonR * (1.6 + ring * 0.7);
        const tilt = 0.3;
        ctx.beginPath();
        ctx.ellipse(cx, cy, r, r * (1 - tilt), 0, 0, Math.PI * 2);
        const a = 0.04 + (1 - ring / 8) * 0.08 * proximity;
        ctx.strokeStyle = `rgba(${255 - ring * 20}, ${120 + ring * 10}, ${40 + ring * 5}, ${a})`;
        ctx.lineWidth = 1.5 + ring * 0.3;
        ctx.stroke();
      }

      // Event horizon (black circle)
      const horGrad = ctx.createRadialGradient(
        cx - horizonR * 0.2, cy - horizonR * 0.2, 0,
        cx, cy, horizonR * 1.3
      );
      horGrad.addColorStop(0, '#000');
      horGrad.addColorStop(0.6, '#0a0a0f');
      horGrad.addColorStop(1, 'rgba(30, 15, 10, 0.8)');
      ctx.beginPath();
      ctx.arc(cx, cy, horizonR * 1.3, 0, Math.PI * 2);
      ctx.fillStyle = horGrad;
      ctx.fill();

      // Horizon glow ring
      ctx.beginPath();
      ctx.arc(cx, cy, horizonR * 1.3, 0, Math.PI * 2);
      ctx.strokeStyle = `rgba(255, 150, 50, ${0.2 + proximity * 0.4})`;
      ctx.lineWidth = 2 + proximity * 3;
      ctx.shadowColor = '#ff6633';
      ctx.shadowBlur = 10 + proximity * 30;
      ctx.stroke();
      ctx.shadowBlur = 0;

      // Particles spiraling in
      for (const p of particles) {
        p.angle += p.speed * (1 + proximity * 2);
        p.radius -= proximity * 0.3;
        if (p.radius < horizonR * 1.3) {
          p.radius = horizonR * 1.5 + Math.random() * 40;
          p.angle = Math.random() * Math.PI * 2;
        }
        p.x = cx + p.radius * Math.cos(p.angle);
        p.y = cy + p.radius * Math.sin(p.angle);
        const dist = Math.sqrt((p.x - cx) ** 2 + (p.y - cy) ** 2);
        const brightness = Math.min(1, Math.max(0.1, (dist - horizonR) / 60));
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size * brightness, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(255, ${180 + Math.floor(brightness * 75)}, ${100 + Math.floor(brightness * 50)}, ${p.alpha * brightness})`;
        ctx.fill();
      }

      frame = requestAnimationFrame(animate);
    };
    animate();

    return () => cancelAnimationFrame(frame);
  }, [proximity]);

  return (
    <canvas
      ref={canvasRef}
      className="w-full h-[200px] rounded-xl"
      style={{ background: 'transparent' }}
    />
  );
}

interface CompassIndicatorProps {
  bearing: number;
}

export function CompassIndicator({ bearing }: CompassIndicatorProps) {
  const dirs = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'];
  const dirIndex = Math.round(bearing / 45) % 8;
  const dir = dirs[dirIndex];

  return (
    <div className="card-accent" style={{ '--accent': '#3b82f6' } as React.CSSProperties}>
      <div className="p-3 flex items-center gap-3">
        <div className="relative w-12 h-12 flex-shrink-0">
          <svg viewBox="0 0 48 48" className="w-full h-full">
            {/* Outer ring */}
            <circle cx="24" cy="24" r="22" fill="none" stroke="rgba(51,65,85,0.3)" strokeWidth="1" />
            {/* Cardinal ticks */}
            {[0, 45, 90, 135, 180, 225, 270, 315].map((a, i) => {
              const rad = (a - 90) * Math.PI / 180;
              const r1 = i % 2 === 0 ? 17 : 19;
              const r2 = 21;
              return (
                <line
                  key={a}
                  x1={24 + r1 * Math.cos(rad)}
                  y1={24 + r1 * Math.sin(rad)}
                  x2={24 + r2 * Math.cos(rad)}
                  y2={24 + r2 * Math.sin(rad)}
                  stroke={i % 2 === 0 ? 'rgba(148,163,184,0.5)' : 'rgba(148,163,184,0.2)'}
                  strokeWidth="1"
                />
              );
            })}
            {/* N label */}
            <text x="24" y="8" textAnchor="middle" fill="rgba(239,68,68,0.6)" fontSize="5" fontFamily="monospace" fontWeight="bold">N</text>
            <text x="24" y="42" textAnchor="middle" fill="rgba(148,163,184,0.3)" fontSize="4" fontFamily="monospace">S</text>
            <text x="6" y="25" textAnchor="middle" fill="rgba(148,163,184,0.3)" fontSize="4" fontFamily="monospace">W</text>
            <text x="42" y="25" textAnchor="middle" fill="rgba(148,163,184,0.3)" fontSize="4" fontFamily="monospace">E</text>
            {/* Needle */}
            <line
              x1="24" y1="24"
              x2={24 + 14 * Math.sin(bearing * Math.PI / 180)}
              y2={24 - 14 * Math.cos(bearing * Math.PI / 180)}
              stroke="#3b82f6"
              strokeWidth="2"
              strokeLinecap="round"
              className="transition-all duration-300"
            />
            {/* Center dot */}
            <circle cx="24" cy="24" r="2" fill="#3b82f6" />
          </svg>
        </div>
        <div>
          <p className="text-[7px] uppercase tracking-[0.2em] text-slate-600">Heading</p>
          <p className="text-sm font-mono font-bold text-blue-400 tabular-nums">
            {bearing.toFixed(1)}°
          </p>
          <p className="text-[8px] font-mono text-slate-500 mt-0.5">{dir}</p>
        </div>
      </div>
      <div className="absolute top-2 left-2 w-2 h-2 border-t border-l opacity-15" style={{ borderColor: '#3b82f6' }} />
    </div>
  );
}


interface CurvatureVisualProps {
  gamma: number;
  gravDilation: number;
}

export function CurvatureVisual({ gamma, gravDilation }: CurvatureVisualProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const W = 280, H = 200;
    canvas.width = W;
    canvas.height = H;

    let frame: number;
    let time = 0;
    const warpStrength = Math.min(1, Math.log10(gamma) / 3);

    const animate = () => {
      time += 0.005;
      ctx.clearRect(0, 0, W, H);

      const cx = W / 2, cy = H / 2;
      const gridSize = 16;
      const spacing = 16;
      const offset = gridSize * spacing / 2;

      // Draw warped grid
      for (let i = 0; i <= gridSize; i++) {
        ctx.beginPath();
        for (let j = 0; j <= gridSize; j++) {
          const nx = (i / gridSize - 0.5) * 2;
          const ny = (j / gridSize - 0.5) * 2;
          const dist = Math.sqrt(nx * nx + ny * ny);
          const warp = warpStrength * 12 / (1 + dist * 2);
          const wave = Math.sin(dist * 3 - time * 2) * warp * 0.2;

          const wx = nx * spacing * gridSize / 2 + (warp + wave) * nx / (dist || 1);
          const wy = ny * spacing * gridSize / 2 + (warp + wave) * ny / (dist || 1);

          const px = cx + wx;
          const py = cy + wy + (warp * 4) * (1 - dist * 0.3);

          if (j === 0) ctx.moveTo(px, py);
          else ctx.lineTo(px, py);
        }
        const alpha = 0.1 + warpStrength * 0.25;
        ctx.strokeStyle = `rgba(100, 180, 255, ${alpha})`;
        ctx.lineWidth = 0.5;
        ctx.stroke();
      }

      for (let j = 0; j <= gridSize; j++) {
        ctx.beginPath();
        for (let i = 0; i <= gridSize; i++) {
          const nx = (i / gridSize - 0.5) * 2;
          const ny = (j / gridSize - 0.5) * 2;
          const dist = Math.sqrt(nx * nx + ny * ny);
          const warp = warpStrength * 12 / (1 + dist * 2);
          const wave = Math.sin(dist * 3 - time * 2) * warp * 0.2;

          const wx = nx * spacing * gridSize / 2 + (warp + wave) * nx / (dist || 1);
          const wy = ny * spacing * gridSize / 2 + (warp + wave) * ny / (dist || 1);

          const px = cx + wx;
          const py = cy + wy + (warp * 4) * (1 - dist * 0.3);

          if (i === 0) ctx.moveTo(px, py);
          else ctx.lineTo(px, py);
        }
        const alpha = 0.1 + warpStrength * 0.25;
        ctx.strokeStyle = `rgba(100, 180, 255, ${alpha})`;
        ctx.lineWidth = 0.5;
        ctx.stroke();
      }

      // Central gravity well
      const wellR = 6 + warpStrength * 14;
      const grad = ctx.createRadialGradient(
        cx + warpStrength * 4, cy + warpStrength * 6, 0,
        cx, cy, wellR * 2.5
      );
      grad.addColorStop(0, `rgba(255, 150, 50, ${warpStrength * 0.4})`);
      grad.addColorStop(0.3, `rgba(200, 100, 50, ${warpStrength * 0.2})`);
      grad.addColorStop(0.7, `rgba(100, 150, 255, ${warpStrength * 0.08})`);
      grad.addColorStop(1, 'transparent');
      ctx.fillStyle = grad;
      ctx.beginPath();
      ctx.arc(cx + warpStrength * 4, cy + warpStrength * 6, wellR * 2.5, 0, Math.PI * 2);
      ctx.fill();

      // Well ring
      ctx.beginPath();
      ctx.arc(cx + warpStrength * 4, cy + warpStrength * 6, wellR, 0, Math.PI * 2);
      ctx.strokeStyle = `rgba(255, 200, 100, ${warpStrength * 0.3})`;
      ctx.lineWidth = 1 + warpStrength;
      ctx.shadowColor = '#ff8833';
      ctx.shadowBlur = 8 * warpStrength;
      ctx.stroke();
      ctx.shadowBlur = 0;

      // Info overlay
      ctx.fillStyle = `rgba(255, 255, 255, ${0.15 + warpStrength * 0.35})`;
      ctx.font = '9px monospace';
      ctx.textAlign = 'center';
      ctx.fillText(`γ = ${gamma.toFixed(2)}`, cx, 14);
      ctx.fillText(`δG = ${(gravDilation * 1e9).toFixed(1)} ns/s`, cx, H - 6);

      const bendLabel = `Curvature: ${(warpStrength * 100).toFixed(0)}%`;
      ctx.fillStyle = `rgba(100, 200, 255, ${0.2 + warpStrength * 0.3})`;
      ctx.fillText(bendLabel, cx, 28);

      frame = requestAnimationFrame(animate);
    };
    animate();

    return () => cancelAnimationFrame(frame);
  }, [gamma, gravDilation]);

  return (
    <canvas
      ref={canvasRef}
      className="w-full h-[200px] rounded-xl"
      style={{ background: 'transparent' }}
    />
  );
}


interface DataAgeIndicatorProps {
  connected: boolean;
  version: number;
}

export function DataAgeIndicator({ connected, version }: DataAgeIndicatorProps) {
  const [age, setAge] = useState(Infinity);
  const lastRef = useRef(Date.now());

  useEffect(() => {
    lastRef.current = Date.now();
  }, [version, connected]);

  useEffect(() => {
    if (!connected) return;
    const interval = setInterval(() => {
      setAge((Date.now() - lastRef.current) / 1000);
    }, 200);
    return () => clearInterval(interval);
  }, [connected, version]);

  if (!connected) return null;

  const fresh = age < 1;
  const warning = age >= 1 && age < 3;
  const stale = age >= 3;

  const color = stale ? 'text-red-400' : warning ? 'text-yellow-400' : 'text-emerald-400';
  const dotColor = stale ? 'bg-red-500' : warning ? 'bg-yellow-500' : 'bg-emerald-500';

  return (
    <div className="card px-3 py-2 flex items-center gap-2">
      <span className={`w-2 h-2 rounded-full ${dotColor} ${fresh ? 'animate-ping' : ''}`} />
      <span className={`text-[8px] font-mono ${color} tabular-nums`}>
        {age < 100 ? `${age.toFixed(1)}s` : '---'}
      </span>
      <span className="text-[6px] text-slate-700 uppercase tracking-wider ml-auto">
        {stale ? 'STALE' : fresh ? 'LIVE' : 'DELAYED'}
      </span>
    </div>
  );
}


interface SearchResult {
  lat: string;
  lon: string;
  display_name: string;
  type: string;
}

interface DestinationSearchProps {
  onSelect: (pos: DestPosition) => void;
}

export function DestinationSearch({ onSelect }: DestinationSearchProps) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(false);
  const timerRef = useRef<ReturnType<typeof setTimeout>>();
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClick = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, []);

  const search = useCallback((q: string) => {
    if (q.length < 3) { setResults([]); return; }
    setLoading(true);
    fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(q)}&limit=5`)
      .then(r => r.json())
      .then((data: SearchResult[]) => {
        setResults(data);
        setOpen(true);
      })
      .catch(() => setResults([]))
      .finally(() => setLoading(false));
  }, []);

  const handleChange = (val: string) => {
    setQuery(val);
    clearTimeout(timerRef.current);
    timerRef.current = setTimeout(() => search(val), 400);
  };

  const handleSelect = (r: SearchResult) => {
    onSelect({ lat: parseFloat(r.lat), lon: parseFloat(r.lon), label: r.display_name.split(',')[0] });
    setQuery(r.display_name.split(',')[0]);
    setOpen(false);
    setResults([]);
  };

  return (
    <div ref={ref} className="relative">
      <div className="relative">
        <span className="absolute left-2 top-1/2 -translate-y-1/2 text-[8px] text-slate-600">⌕</span>
        <input
          type="text"
          value={query}
          onChange={(e) => handleChange(e.target.value)}
          onFocus={() => results.length > 0 && setOpen(true)}
          placeholder="Search destination..."
          className="w-full pl-6 pr-3 py-1.5 text-[9px] font-mono bg-slate-900/60 border border-slate-800 rounded-lg text-slate-300 placeholder-slate-700 focus:outline-none focus:border-blue-500/40"
        />
        {loading && (
          <span className="absolute right-2 top-1/2 -translate-y-1/2 w-2 h-2 border border-slate-600 border-t-blue-400 rounded-full animate-spin" />
        )}
      </div>
      {open && results.length > 0 && (
        <div className="absolute top-full left-0 right-0 mt-1 bg-slate-900/95 backdrop-blur-xl border border-slate-800 rounded-lg z-50 max-h-48 overflow-y-auto">
          {results.map((r, i) => (
            <button
              key={i}
              onClick={() => handleSelect(r)}
              className="w-full text-left px-3 py-2 text-[8px] font-mono text-slate-400 hover:bg-white/5 hover:text-slate-200 transition-colors border-b border-slate-800/50 last:border-0"
            >
              <span className="block truncate">{r.display_name}</span>
              <span className="text-[6px] text-slate-700 mt-0.5">{r.type} · {parseFloat(r.lat).toFixed(4)}, {parseFloat(r.lon).toFixed(4)}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}


interface DeviceInfo {
  battery: number | null;
  charging: boolean | null;
  connection: string;
}

export function DeviceStatus() {
  const [info, setInfo] = useState<DeviceInfo>({ battery: null, charging: null, connection: 'unknown' });

  useEffect(() => {
    const conn = (navigator as any).connection;
    if (conn) {
      const updateConn = () => setInfo(prev => ({ ...prev, connection: conn.effectiveType || 'unknown' }));
      updateConn();
      conn.addEventListener('change', updateConn);
      return () => conn.removeEventListener('change', updateConn);
    }
  }, []);

  useEffect(() => {
    if ('getBattery' in navigator) {
      (navigator as any).getBattery().then((battery: any) => {
        const update = () => setInfo(prev => ({ ...prev, battery: battery.level * 100, charging: battery.charging }));
        update();
        battery.addEventListener('levelchange', update);
        battery.addEventListener('chargingchange', update);
      });
    }
  }, []);

  const batteryColor = info.battery === null ? 'text-slate-600' :
    info.battery < 20 ? 'text-red-400' :
    info.battery < 50 ? 'text-yellow-400' : 'text-emerald-400';

  return (
    <div className="card p-3">
      <div className="flex items-center gap-2 mb-2">
        <span className="text-[8px]">🔋</span>
        <span className="font-bold text-[7px] uppercase tracking-[0.2em] text-slate-600">Device</span>
      </div>
      <div className="space-y-1 text-[8px] font-mono">
        <div className="flex justify-between">
          <span className="text-slate-500">Battery</span>
          <span className={batteryColor}>{info.battery !== null ? `${info.battery.toFixed(0)}%${info.charging ? ' ⚡' : ''}` : '--'}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-slate-500">Network</span>
          <span className="text-slate-400 uppercase">{info.connection}</span>
        </div>
      </div>
    </div>
  );
}

interface DopplerShiftPreviewProps {
  dopplerFactor: number;
}

export function DopplerShiftPreview({ dopplerFactor }: DopplerShiftPreviewProps) {
  const pos = dopplerFactor < 1
    ? Math.max(0, 50 - (1 - dopplerFactor) * 200)
    : Math.min(100, 50 + (dopplerFactor - 1) * 100);

  return (
    <div className="card-accent p-5" style={{ '--accent': '#f97316' } as React.CSSProperties}>
      <div className="flex items-center gap-2 mb-3">
        <span className="w-1.5 h-1.5 rounded-full bg-gradient-to-r from-red-500 via-green-400 to-blue-500" />
        <h2 className="font-bold text-[10px] uppercase tracking-[0.2em] text-slate-400">Doppler Shift</h2>
      </div>
      <div className="h-6 w-full rounded-lg bg-gradient-to-r from-red-600 via-yellow-200 via-green-400 to-blue-600 relative overflow-hidden">
        <div
          className="absolute top-0.5 bottom-0.5 w-1.5 bg-white rounded-full shadow-[0_0_12px_rgba(255,255,255,0.8)] transition-all duration-300"
          style={{ left: `${pos}%`, transform: 'translateX(-50%)' }}
        />
      </div>
      <div className="flex justify-between text-[8px] mt-1.5 uppercase tracking-tighter">
        <span className="text-red-400/60">Redshift</span>
        <span className="font-mono text-white text-[11px]">{dopplerFactor.toFixed(4)}x</span>
        <span className="text-blue-400/60">Blueshift</span>
      </div>
    </div>
  );
}


interface ClockProps {
  gamma: number;
}

export function DualClock({ gamma }: ClockProps) {
  const [utc, setUtc] = useState(new Date());
  const [dilatedOffset, setDilatedOffset] = useState(0);

  useEffect(() => {
    let last = Date.now();
    const interval = setInterval(() => {
      const now = Date.now();
      const dt = (now - last) / 1000;
      setDilatedOffset(prev => prev + dt / Math.max(gamma, 1));
      setUtc(new Date());
      last = now;
    }, 200);
    return () => clearInterval(interval);
  }, [gamma]);

  const fmt = (d: Date) =>
    d.toISOString().slice(11, 22).replace('Z', '');

  const dilatedFrom = (offset: number) => {
    const base = utc.getTime();
    const d = new Date(base - (utc.getTime() - (utc.getTime() - offset * 1000)));
    return fmt(new Date(base + (dilatedOffset - (Date.now() - utc.getTime()) / 1000) * 1000));
  };

  const coordTime = fmt(utc);
  const propTime = fmt(new Date(utc.getTime() + (dilatedOffset - (Date.now() - utc.getTime()) / 1000 / Math.max(gamma, 1)) * 1000));

  return (
    <div className="card-accent" style={{ '--accent': '#10b981' } as React.CSSProperties}>
      <div className="p-4 space-y-3">
        <div className="flex items-center gap-2" style={{ color: '#10b981' }}>
          <span className="text-[8px]">◷</span>
          <span className="font-bold uppercase tracking-[0.2em] text-[10px]" style={{ color: '#10b981' }}>Timeline</span>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-[7px] uppercase tracking-[0.2em] text-slate-600 mb-1">Coordinate</p>
            <p className="text-lg font-mono font-bold text-slate-200 tracking-tight tabular-nums">
              {coordTime}
            </p>
          </div>
          <div>
            <p className="text-[7px] uppercase tracking-[0.2em] text-slate-600 mb-1">Proper (dilated)</p>
            <p className="text-lg font-mono font-bold text-emerald-400 tracking-tight tabular-nums">
              {propTime}
            </p>
          </div>
        </div>

        <div className="flex justify-between text-[7px] text-slate-600 font-mono">
          <span>γ = {gamma.toFixed(2)}</span>
          <span>Δτ = {(dilatedOffset / 1000).toFixed(1)}s behind</span>
        </div>
      </div>
      <div className="absolute top-2 left-2 w-2.5 h-2.5 border-t border-l opacity-15" style={{ borderColor: '#10b981' }} />
      <div className="absolute bottom-2 right-2 w-2.5 h-2.5 border-b border-r opacity-15" style={{ borderColor: '#10b981' }} />
    </div>
  );
}


interface EnergeticsPanelProps {
  metrics: Metrics | null;
}

function MetricCard({ icon: Icon, label, value, unit, desc, accent, decimals = 2 }: any) {
  return (
    <div className="card-accent" style={{ '--accent': accent } as React.CSSProperties}>
      <div className="p-5">
        <div className="flex items-center gap-2 mb-3" style={{ color: accent }}>
          <Icon size={18} />
          <span className="font-bold uppercase tracking-[0.2em] text-[10px]" style={{ color: accent }}>{label}</span>
        </div>
        <div className="mb-1">
          {value !== null && value !== undefined
            ? <AnimatedValue value={value} decimals={decimals} unit={unit} color={accent} />
            : <span className="text-xl font-mono font-bold tracking-tight text-slate-700">--</span>
          }
        </div>
        <p className="text-[8px] mt-1 opacity-40 tracking-wider leading-relaxed">{desc}</p>
      </div>
      <div className="absolute top-2 left-2 w-3 h-3 border-t border-l opacity-20" style={{ borderColor: accent }} />
      <div className="absolute bottom-2 right-2 w-3 h-3 border-b border-r opacity-20" style={{ borderColor: accent }} />
    </div>
  );
}

export function EnergeticsPanel({ metrics }: EnergeticsPanelProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-5 stagger-fade">
      <MetricCard
        icon={Activity}
        label="Relativistic Mass"
        value={metrics?.rel_mass_kg ?? null}
        unit="kg"
        desc="Car mass including kinetic increase (m = γm₀)"
        accent="#f97316"
        decimals={2}
      />
      <MetricCard
        icon={Zap}
        label="Kinetic Energy"
        value={metrics?.kinetic_energy_j ?? null}
        unit="J"
        desc="Total energy in your inertial frame"
        accent="#3b82f6"
        decimals={3}
      />
      <MetricCard
        icon={Flame}
        label="Matter Equivalent"
        value={metrics?.fuel_equiv_kg ?? null}
        unit="g"
        desc="Mass converted to pure energy (E/c²)"
        accent="#ef4444"
        decimals={4}
      />
    </div>
  );
}


interface EnvironmentDataProps {
  lat: number;
  lon: number;
  alt: number;
  accuracy: number;
  bearing: number;
}

function julianDay(date: Date) {
  const y = date.getFullYear();
  const m = date.getMonth() + 1;
  const d = date.getDate();
  const h = date.getUTCHours() + date.getUTCMinutes() / 60 + date.getUTCSeconds() / 3600;
  const a = Math.floor((14 - m) / 12);
  const yy = y + 4800 - a;
  const mm = m + 12 * a - 3;
  return d + Math.floor((153 * mm + 2) / 5) + 365 * yy + Math.floor(yy / 4) - Math.floor(yy / 100) + Math.floor(yy / 400) - 32045 + h / 24;
}

function sunPosition(lat: number, lon: number, date: Date) {
  const jd = julianDay(date);
  const n = jd - 2451545;
  const L = (280.46 + 0.9856474 * n) % 360;
  const g = (357.528 + 0.9856003 * n) % 360;
  const lambda = L + 1.915 * Math.sin(g * Math.PI / 180) + 0.02 * Math.sin(2 * g * Math.PI / 180);
  const epsilon = 23.439 - 0.0000004 * n;
  const ra = Math.atan2(Math.cos(epsilon * Math.PI / 180) * Math.sin(lambda * Math.PI / 180), Math.cos(lambda * Math.PI / 180)) * 180 / Math.PI;
  const dec = Math.asin(Math.sin(epsilon * Math.PI / 180) * Math.sin(lambda * Math.PI / 180)) * 180 / Math.PI;
  const gmst = (280.46061837 + 360.98564736629 * (jd - 2451545)) % 360;
  const lmst = (gmst + lon) % 360;
  const ha = (lmst - ra + 360) % 360;
  const alt = Math.asin(Math.sin(lat * Math.PI / 180) * Math.sin(dec * Math.PI / 180) + Math.cos(lat * Math.PI / 180) * Math.cos(dec * Math.PI / 180) * Math.cos(ha * Math.PI / 180)) * 180 / Math.PI;
  const az = Math.atan2(-Math.sin(ha * Math.PI / 180), Math.tan(dec * Math.PI / 180) * Math.cos(lat * Math.PI / 180) - Math.sin(lat * Math.PI / 180) * Math.cos(ha * Math.PI / 180)) * 180 / Math.PI + 180;
  return { elevation: alt, azimuth: az % 360 };
}

function moonPhase(date: Date) {
  const jd = julianDay(date);
  const n = jd - 2451550;
  const phase = ((n / 29.53058867) % 1 + 1) % 1;
  const illuminated = (1 - Math.cos(phase * 2 * Math.PI)) / 2;
  const age = phase * 29.53058867;
  const names = ['New Moon', 'Waxing Crescent', 'First Quarter', 'Waxing Gibbous', 'Full Moon', 'Waning Gibbous', 'Last Quarter', 'Waning Crescent'];
  const idx = Math.round(phase * 8) % 8;
  return { phase: phase * 100, illuminated: illuminated * 100, name: names[idx], age };
}

function isaModel(altM: number) {
  const T0 = 288.15;
  const P0 = 101325;
  const L = 0.0065;
  const R = 287.05;
  const g = 9.80665;
  const h = Math.max(0, altM);
  const T = T0 - L * h;
  const P = P0 * Math.pow(T / T0, g / (L * R));
  const rho = P / (R * T);
  return { temperature: T - 273.15, pressure: P / 100, density: rho };
}

export function EnvironmentData({ lat, lon, alt, accuracy, bearing }: EnvironmentDataProps) {
  const [now, setNow] = useState(new Date());

  useEffect(() => {
    const interval = setInterval(() => setNow(new Date()), 10000);
    return () => clearInterval(interval);
  }, []);

  const sun = sunPosition(lat, lon, now);
  const moon = moonPhase(now);
  const isDay = sun.elevation > 0;
  const atmos = isaModel(alt);
  // Approximate moon azimuth: opposite sun near full moon, same as sun near new moon
  const moonAzimuth = (sun.azimuth + 180 * (1 - moon.phase / 50) + 360) % 360;

  const fiv = (n: number, d = 1) => n.toFixed(d);
  const bearingDegToDir = (deg: number) => {
    const dirs = ['ahead', 'ahead right', 'right', 'behind right', 'behind', 'behind left', 'left', 'ahead left'];
    return dirs[Math.round(deg / 45) % 8];
  };

  return (
    <div className="card-accent" style={{ '--accent': '#f97316' } as React.CSSProperties}>
      <div className="p-4 space-y-3">
        <div className="flex items-center gap-2" style={{ color: '#f97316' }}>
          <span className="text-[8px]">⊕</span>
          <span className="font-bold uppercase tracking-[0.2em] text-[10px]" style={{ color: '#f97316' }}>
            Environment
          </span>
        </div>

        {/* Sun / Day-Night */}
        <div className="flex items-center gap-3">
          <div className={`w-8 h-8 rounded-full flex items-center justify-center text-[10px] font-bold ${isDay ? 'bg-yellow-500/20 text-yellow-400' : 'bg-indigo-500/20 text-indigo-400'}`}>
            {isDay ? '☀' : '☾'}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-[7px] uppercase tracking-[0.2em] text-slate-600">Solar</p>
            <p className="text-[10px] font-mono text-slate-300">
              {isDay ? 'Daytime' : 'Nighttime'} · Alt {fiv(sun.elevation)}° · Az {fiv(sun.azimuth)}°
            </p>
            <div className="mt-1 h-1 w-full rounded-full bg-slate-800 overflow-hidden">
              <div
                className={`h-full rounded-full transition-all duration-1000 ${isDay ? 'bg-gradient-to-r from-yellow-500 to-orange-500' : 'bg-gradient-to-r from-indigo-500 to-purple-500'}`}
                style={{ width: `${Math.max(0, Math.min(100, (sun.elevation + 90) / 180 * 100))}%` }}
              />
            </div>
          </div>
        </div>

        {/* Moon Phase */}
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-slate-800 flex items-center justify-center text-[8px] font-mono text-slate-400 overflow-hidden relative">
            <div className="absolute inset-0 bg-slate-900 rounded-full" />
            <div
              className="absolute inset-0 bg-slate-300 rounded-full"
              style={{ clipPath: `inset(0 ${50 - moon.phase / 2}% 0 0)` }}
            />
            <div
              className="absolute inset-0 bg-slate-900 rounded-full"
              style={{ clipPath: `inset(0 0 0 ${50 + moon.phase / 2}%)` }}
            />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-[7px] uppercase tracking-[0.2em] text-slate-600">Lunar</p>
            <p className="text-[10px] font-mono text-slate-300">
              {moon.name} · {fiv(moon.illuminated)}% · {fiv(moon.age, 0)}d
            </p>
          </div>
        </div>

        {/* Atmospheric Data */}
        <div className="grid grid-cols-3 gap-2 pt-2 border-t border-slate-800/50">
          <div>
            <p className="text-[6px] uppercase tracking-[0.2em] text-slate-600">Temp</p>
            <p className="text-[10px] font-mono text-slate-400">{fiv(atmos.temperature)} °C</p>
          </div>
          <div>
            <p className="text-[6px] uppercase tracking-[0.2em] text-slate-600">Pressure</p>
            <p className="text-[10px] font-mono text-slate-400">{fiv(atmos.pressure, 0)} hPa</p>
          </div>
          <div>
            <p className="text-[6px] uppercase tracking-[0.2em] text-slate-600">GPS σ</p>
            <p className="text-[10px] font-mono text-slate-400">±{accuracy.toFixed(0)}m</p>
          </div>
        </div>

        {/* Sky Direction Strip */}
        <div className="pt-2 border-t border-slate-800/50">
          <p className="text-[6px] uppercase tracking-[0.2em] text-slate-600 mb-1.5">Sky Relative to Heading</p>
          <svg viewBox="0 0 120 20" className="w-full h-5">
            {/* Background arc */}
            <path d="M 10 15 A 50 50 0 0 1 110 15" fill="none" stroke="rgba(51,65,85,0.3)" strokeWidth="1" />
            {/* Sun marker */}
            {(() => {
              const rel = ((sun.azimuth - bearing + 360) % 360);
              const x = 10 + (rel / 180) * 50;
              const y = 15 - 50 + 50 * Math.cos((rel * Math.PI) / 180);
              return (
                <>
                  <text x={x} y={y - 6} textAnchor="middle" fontSize="6" fill="#fbbf24">☀</text>
                  <text x={x} y={y + 8} textAnchor="middle" fontSize="3" fill="rgba(251,191,36,0.5)">
                    {rel.toFixed(0)}°
                  </text>
                </>
              );
            })()}
            {/* Moon marker */}
            {(() => {
              const rel = ((moonAzimuth - bearing + 360) % 360);
              const x = 10 + (rel / 180) * 50;
              const y = 15 - 50 + 50 * Math.cos((rel * Math.PI) / 180);
              return (
                <text x={x} y={y - 6} textAnchor="middle" fontSize="5" fill="rgba(196,181,253,0.6)">☾</text>
              );
            })()}
            {/* Heading marker */}
            <line x1="60" y1="10" x2="60" y2="17" stroke="rgba(59,130,246,0.6)" strokeWidth="1.5" />
            <text x="60" y="9" textAnchor="middle" fontSize="3" fill="rgba(59,130,246,0.5)">▲</text>
            {/* Cardinal labels */}
            <text x="60" y="19" textAnchor="middle" fontSize="3.5" fill="rgba(148,163,184,0.4)" fontFamily="monospace">N</text>
            <text x="10" y="17" textAnchor="middle" fontSize="3.5" fill="rgba(148,163,184,0.2)" fontFamily="monospace">W</text>
            <text x="110" y="17" textAnchor="middle" fontSize="3.5" fill="rgba(148,163,184,0.2)" fontFamily="monospace">E</text>
          </svg>
          <div className="flex justify-between text-[6px] font-mono text-slate-700 mt-0.5">
            <span>Sun: {((sun.azimuth - bearing + 360) % 360).toFixed(0)}° {bearingDegToDir((sun.azimuth - bearing + 360) % 360)}</span>
            <span>Moon: {((moonAzimuth - bearing + 360) % 360).toFixed(0)}°</span>
            <span>Heading: {bearing.toFixed(0)}°</span>
          </div>
        </div>
      </div>
      <div className="absolute top-2 left-2 w-2.5 h-2.5 border-t border-l opacity-15" style={{ borderColor: '#f97316' }} />
      <div className="absolute bottom-2 right-2 w-2.5 h-2.5 border-b border-r opacity-15" style={{ borderColor: '#f97316' }} />
    </div>
  );
}


interface ErrorBannerProps {
  error: string | null;
}

export function ErrorBanner({ error }: ErrorBannerProps) {
  if (!error) return null;

  return (
    <div className="bg-red-900/20 border border-red-500/50 p-4 rounded-lg flex items-center gap-3 text-red-200 animate-bounce">
      <ShieldAlert size={20} />
      <p>{error}</p>
    </div>
  );
}


interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false, error: null };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('ErrorBoundary caught:', error, info);
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) return this.props.fallback;
      return (
        <div className="p-8 max-w-lg mx-auto mt-20 text-center">
          <div className="bg-red-900/20 border border-red-500/50 rounded-2xl p-8 space-y-4">
            <h2 className="text-xl font-bold text-red-400">Something went wrong</h2>
            <p className="text-slate-400 text-sm font-mono">
              {this.state.error?.message || 'Unknown error'}
            </p>
            <button
              onClick={() => {
                this.setState({ hasError: false, error: null });
                window.location.reload();
              }}
              className="px-6 py-2 bg-red-600 hover:bg-red-500 text-white rounded-lg text-sm transition-colors"
            >
              Reload
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}


export function FpsMonitor() {
  const [fps, setFps] = useState(0);
  const framesRef = useRef(0);
  const lastRef = useRef(performance.now());

  useEffect(() => {
    let frame: number;
    const tick = () => {
      framesRef.current++;
      const now = performance.now();
      const delta = now - lastRef.current;
      if (delta >= 1000) {
        setFps(Math.round(framesRef.current * 1000 / delta));
        framesRef.current = 0;
        lastRef.current = now;
      }
      frame = requestAnimationFrame(tick);
    };
    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, []);

  const color = fps >= 55 ? 'text-emerald-500' : fps >= 30 ? 'text-yellow-500' : 'text-red-500';

  return (
    <div className="card px-2 py-1 flex items-center gap-1.5">
      <span className={`text-[7px] font-mono ${color} tabular-nums`}>{fps}</span>
      <span className="text-[5px] text-slate-700 uppercase tracking-wider">FPS</span>
    </div>
  );
}


export function GlitchOverlay() {
  const [glitch, setGlitch] = useState(false);

  useEffect(() => {
    const schedule = () => {
      const delay = 3000 + Math.random() * 12000;
      return setTimeout(() => {
        setGlitch(true);
        setTimeout(() => setGlitch(false), 100 + Math.random() * 150);
        schedule();
      }, delay);
    };
    const timer = schedule();
    return () => clearTimeout(timer);
  }, []);

  if (!glitch) return null;

  return (
    <div className="fixed inset-0 pointer-events-none z-50 overflow-hidden">
      <div
        className="absolute inset-0 opacity-[0.07]"
        style={{
          background: 'linear-gradient(0deg, rgba(0,100,255,0.3) 0%, transparent 5%, transparent 95%, rgba(0,100,255,0.3) 100%)',
          transform: `translateY(${Math.random() * 10 - 5}px)`,
        }}
      />
      <div
        className="absolute left-0 right-0 opacity-30"
        style={{
          top: `${Math.random() * 100}%`,
          height: `${1 + Math.random() * 4}px`,
          background: '#4488ff',
          boxShadow: '0 0 20px #4488ff',
          transform: `translateX(${Math.random() * 20 - 10}px)`,
        }}
      />
    </div>
  );
}


interface HeaderProps {
  audioEnabled: boolean;
  bhMode: boolean;
  warpMode: boolean;
  onToggleAudio: () => void;
  onToggleBh: () => void;
  onExportLog: () => void;
  onToggleWarp: () => void;
}

function StatusDot({ active, color }: { active: boolean; color: string }) {
  return (
    <span className="relative inline-flex w-2 h-2 mr-1.5">
      <span className={`absolute inset-0 rounded-full ${active ? `bg-${color}-500` : 'bg-slate-600'}`} />
      {active && <span className={`absolute inset-0 rounded-full bg-${color}-500 animate-ping opacity-40`} />}
    </span>
  );
}

export function Header({ audioEnabled, bhMode, warpMode, onToggleAudio, onToggleBh, onExportLog, onToggleWarp }: HeaderProps) {
  const navItems = [
    { key: '1', label: 'DASH' },
    { key: '2', label: 'LABS' },
  ];

  return (
    <header className="card overflow-visible">
      <div className="flex flex-wrap items-center justify-between gap-3 px-5 py-3">
        {/* Left: Logo + Status */}
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-cyan-400 flex items-center justify-center shadow-[0_0_16px_-4px_#3b82f6]">
              <Zap size={16} className="text-white" />
            </div>
            <div>
              <h1 className="text-lg font-bold tracking-widest text-transparent bg-clip-text bg-gradient-to-r from-cyan-300 to-blue-400 leading-none">
                CHRONOS-X
              </h1>
              <p className="text-[7px] uppercase tracking-[0.3em] text-slate-600 leading-none mt-0.5">Relativistic Dashboard</p>
            </div>
          </div>
          <div className="hidden md:flex items-center gap-3 pl-4 border-l border-slate-800">
            <span className="flex items-center text-[9px] text-slate-500 uppercase tracking-wider">
              <StatusDot active={true} color="emerald" />
              ONLINE
            </span>
            <span className={`flex items-center text-[9px] uppercase tracking-wider ${warpMode ? 'text-red-400' : 'text-slate-500'}`}>
              <StatusDot active={warpMode} color="red" />
              {warpMode ? 'WARP' : 'NORMAL'}
            </span>
            <span className={`flex items-center text-[9px] uppercase tracking-wider ${bhMode ? 'text-red-500' : 'text-slate-500'}`}>
              <StatusDot active={bhMode} color="red" />
              {bhMode ? 'BH ACTIVE' : 'BH OFF'}
            </span>
          </div>
        </div>

        {/* Right: Controls */}
        <div className="flex items-center gap-2">
          <button
            onClick={onToggleAudio}
            className={`p-2 rounded-lg transition-all ${audioEnabled ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 shadow-[0_0_12px_-4px_#10b981]' : 'bg-slate-800/50 text-slate-600 border border-slate-800 hover:text-slate-400 hover:border-slate-700'}`}
            title="Auditory Time Dilation [A]"
          >
            {audioEnabled ? <Volume2 size={15} /> : <VolumeX size={15} />}
          </button>
          <button
            onClick={onToggleBh}
            className={`p-2 rounded-lg transition-all ${bhMode ? 'bg-red-500/15 text-red-400 border border-red-500/30 shadow-[0_0_12px_-4px_#ef4444]' : 'bg-slate-800/50 text-slate-600 border border-slate-800 hover:text-slate-400 hover:border-slate-700'}`}
            title="Black Hole Mode [B]"
          >
            <CircleAlert size={15} />
          </button>
          <div className="w-px h-6 bg-slate-800 mx-1" />
          <button
            onClick={onExportLog}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800/50 border border-slate-800 text-[9px] font-bold tracking-widest text-emerald-400 hover:bg-slate-800 hover:border-emerald-500/30 transition-all"
          >
            <Download size={12} /> LOG
          </button>
          <button
            onClick={onToggleWarp}
            className={`px-3 py-1.5 rounded-lg text-[9px] font-bold tracking-widest transition-all border ${
              warpMode
                ? 'bg-red-500/15 text-red-400 border-red-500/40 animate-flicker shadow-[0_0_20px_-6px_#ef4444]'
                : 'bg-slate-800/50 text-slate-500 border-slate-800 hover:text-slate-300 hover:border-slate-700'
            }`}
          >
            {warpMode ? 'WARP ACTIVE' : 'WARP [W]'}
          </button>
        </div>
      </div>

      {/* Keyboard shortcut hint bar */}
      <div className="flex gap-4 px-5 pb-2.5 text-[7px] tracking-widest text-slate-700 uppercase">
        <span><kbd className="text-slate-600 bg-slate-800/50 px-1 rounded">1</kbd> DASH</span>
        <span><kbd className="text-slate-600 bg-slate-800/50 px-1 rounded">2</kbd> LABS</span>
        <span><kbd className="text-slate-600 bg-slate-800/50 px-1 rounded">W</kbd> WARP</span>
        <span><kbd className="text-slate-600 bg-slate-800/50 px-1 rounded">B</kbd> BLACKHOLE</span>
        <span><kbd className="text-slate-600 bg-slate-800/50 px-1 rounded">M</kbd> MANUAL</span>
        <span><kbd className="text-slate-600 bg-slate-800/50 px-1 rounded">A</kbd> AUDIO</span>
      </div>
    </header>
  );
}


interface TimelineEvent {
  time: number;
  type: 'speed' | 'warp' | 'bh' | 'dest' | 'real' | 'alert';
  label: string;
  value?: string;
}

interface JourneyTimelineProps {
  events: TimelineEvent[];
  collapsed: boolean;
  onToggle: () => void;
}

export function JourneyTimeline({ events, collapsed, onToggle }: JourneyTimelineProps) {
  const listRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!collapsed && listRef.current) {
      listRef.current.scrollTop = listRef.current.scrollHeight;
    }
  }, [events, collapsed]);

  const typeColor = (t: string) => {
    switch (t) {
      case 'warp': return 'text-purple-400';
      case 'bh': return 'text-red-400';
      case 'dest': return 'text-emerald-400';
      case 'real': return 'text-cyan-400';
      case 'alert': return 'text-yellow-400';
      default: return 'text-blue-400';
    }
  };

  const fmt = (ts: number) => {
    const d = new Date(ts);
    return d.toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
  };

  return (
    <div className="card p-3">
      <button onClick={onToggle} className="w-full flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-[8px]">◷</span>
          <span className="font-bold uppercase tracking-[0.2em] text-[9px] text-slate-400">Journey Log</span>
          <span className="text-[7px] font-mono text-slate-600">({events.length})</span>
        </div>
        <span className="text-[8px] text-slate-600 transition-transform" style={{ transform: collapsed ? '' : 'rotate(180deg)' }}>
          ▾
        </span>
      </button>

      {!collapsed && (
        <div ref={listRef} className="mt-2 max-h-40 overflow-y-auto space-y-0.5">
          {events.length === 0 && (
            <p className="text-[8px] text-slate-700 font-mono text-center py-4">No events yet</p>
          )}
          {events.slice(-50).reverse().map((e, i) => (
            <div key={i} className="flex items-start gap-2 text-[8px] font-mono leading-relaxed">
              <span className="text-slate-700 w-14 flex-shrink-0 tabular-nums">{fmt(e.time)}</span>
              <span className={`flex-shrink-0 ${typeColor(e.type)}`}>▸</span>
              <span className="text-slate-500">{e.label}</span>
              {e.value && <span className="text-slate-600 ml-auto tabular-nums">{e.value}</span>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export type { TimelineEvent };


const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const FAV_KEY = 'chronos-lab-favorites';
const HISTORY_KEY = 'chronos-lab-history';
const PRESET_KEY = 'chronos-lab-presets';

interface Lab {
  id: string;
  name: string;
  description: string;
  category: string;
  images: string[];
}

interface ParamDef {
  name: string;
  type: string;
  default: number | string | boolean | null;
  required: boolean;
}

interface RunResult {
  image?: string;
  text?: string;
  data?: Record<string, string>;
  error?: string;
  compute_time_s?: number;
}

interface RunHistoryEntry {
  labId: string;
  params: Record<string, string>;
  time: number;
  computeTime: number;
}

interface SavedPreset {
  labId: string;
  name: string;
  values: Record<string, string>;
}

const CAT_COLORS: Record<string, string> = {
  astrophysics: '#f59e0b',
  quantum: '#a855f7',
  cosmology: '#06b6d4',
  thermodynamics: '#ef4444',
  mechanics: '#3b82f6',
  electromagnetism: '#ec4899',
  nuclear: '#84cc16',
  optics: '#f97316',
  'fluid-dynamics': '#14b8a6',
};

function stringToColor(s: string): string {
  if (CAT_COLORS[s]) return CAT_COLORS[s];
  let hash = 0;
  for (let i = 0; i < s.length; i++) hash = s.charCodeAt(i) + ((hash << 5) - hash);
  const hue = hash % 360;
  return `hsl(${hue < 0 ? hue + 360 : hue}, 70%, 55%)`;
}

function loadFavorites(): Set<string> {
  try { return new Set(JSON.parse(localStorage.getItem(FAV_KEY) || '[]')); } catch { return new Set(); }
}

function saveFavorites(favs: Set<string>) {
  localStorage.setItem(FAV_KEY, JSON.stringify([...favs]));
}

function loadRunHistory(): RunHistoryEntry[] {
  try { return JSON.parse(localStorage.getItem(HISTORY_KEY) || '[]'); } catch { return []; }
}

function saveRunHistory(h: RunHistoryEntry[]) {
  localStorage.setItem(HISTORY_KEY, JSON.stringify(h.slice(-20)));
}

function loadPresets(): SavedPreset[] {
  try { return JSON.parse(localStorage.getItem(PRESET_KEY) || '[]'); } catch { return []; }
}

function savePresets(p: SavedPreset[]) {
  localStorage.setItem(PRESET_KEY, JSON.stringify(p));
}

function LabsSkeletonCard() {
  return (
    <div className="card overflow-hidden animate-pulse">
      <div className="h-36 bg-slate-800/50" />
      <div className="p-3 space-y-2">
        <div className="h-2 w-16 bg-slate-800/50 rounded" />
        <div className="h-3 w-32 bg-slate-800/50 rounded" />
        <div className="h-2 w-full bg-slate-800/30 rounded" />
        <div className="h-2 w-3/4 bg-slate-800/30 rounded" />
      </div>
    </div>
  );
}

function Lightbox({ src, alt, onClose }: { src: string; alt: string; onClose: () => void }) {
  useEffect(() => {
    const handler = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [onClose]);

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/90 backdrop-blur-sm p-4"
      onClick={onClose}
    >
      <button onClick={onClose} className="absolute top-4 right-4 text-slate-400 hover:text-white text-lg z-10 w-8 h-8 flex items-center justify-center rounded-full bg-white/10 backdrop-blur-xl border border-white/20">&times;</button>
      <img src={src} alt={alt} className="max-w-full max-h-full object-contain rounded-xl shadow-2xl" onClick={(e) => e.stopPropagation()} />
    </div>
  );
}

export function LabsPage() {
  const [labs, setLabs] = useState<Lab[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [activeCategory, setActiveCategory] = useState<string | null>(null);
  const [selectedLab, setSelectedLab] = useState<Lab | null>(null);
  const [search, setSearch] = useState('');
  const [favorites, setFavorites] = useState<Set<string>>(loadFavorites);
  const [showFavorites, setShowFavorites] = useState(false);
  const [sortBy, setSortBy] = useState<'name' | 'category'>('name');
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('asc');
  const [loading, setLoading] = useState(true);
  const [listView, setListView] = useState(false);

  useEffect(() => {
    fetch(`${API_URL}/labs`)
      .then((r) => r.json())
      .then((data) => {
        setLabs(data.labs);
        setCategories(data.categories);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const toggleFav = (id: string) => {
    setFavorites(prev => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id); else next.add(id);
      saveFavorites(next);
      return next;
    });
  };

  const filtered = labs
    .filter((l) => {
      const cat = activeCategory ? l.category === activeCategory : true;
      const fav = showFavorites ? favorites.has(l.id) : true;
      const q = search.toLowerCase();
      const match = q
        ? l.name.toLowerCase().includes(q) ||
          l.description.toLowerCase().includes(q) ||
          l.category.toLowerCase().includes(q) ||
          l.id.toLowerCase().includes(q)
        : true;
      return cat && fav && match;
    })
    .sort((a, b) => {
      const aVal = sortBy === 'name' ? a.name : a.category;
      const bVal = sortBy === 'name' ? b.name : b.category;
      const cmp = aVal.localeCompare(bVal);
      return sortDir === 'asc' ? cmp : -cmp;
    });

  if (selectedLab) {
    return (
      <LabDetail
        lab={selectedLab}
        onBack={() => setSelectedLab(null)}
        apiUrl={API_URL}
        isFavorite={favorites.has(selectedLab.id)}
        onToggleFav={() => toggleFav(selectedLab.id)}
      />
    );
  }

  const favCount = [...labs].filter(l => favorites.has(l.id)).length;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-4 card p-4">
        <h2 className="font-bold text-sm uppercase tracking-[0.2em] text-blue-400">Physics Labs</h2>
        <div className="flex items-center gap-3">
          <span className="text-[10px] font-mono text-slate-500">{labs.length} experiments</span>
          <span className="text-[9px] font-mono text-yellow-500">{favCount > 0 ? `★ ${favCount}` : ''}</span>
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
        </div>
      </div>

      {!loading && labs.length > 0 && (
        <div className="flex gap-3 text-[7px] font-mono text-slate-600 card px-4 py-2 flex-wrap">
          <span>{labs.length} total</span>
          <span className="text-slate-800">|</span>
          <span>{categories.length} categories</span>
          <span className="text-slate-800">|</span>
          <span>{labs.reduce((a, l) => a + l.images.length, 0)} previews</span>
          <span className="text-slate-800">|</span>
          <span>{favCount} ★</span>
        </div>
      )}

      <div className="flex gap-3 flex-wrap items-center">
        <div className="relative flex-1 min-w-[200px]">
          <span className="absolute left-3 top-1/2 -translate-y-1/2 text-[10px] text-slate-600 font-mono">⌕</span>
          <input
            type="text"
            placeholder="Search experiments..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full card px-8 py-2.5 text-xs text-slate-200 placeholder-slate-600 font-mono focus:outline-none focus:border-blue-500/50 transition-colors"
          />
          {search && (
            <button
              onClick={() => setSearch('')}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-[10px] text-slate-600 hover:text-slate-400"
            >
              ✕
            </button>
          )}
        </div>
        <div className="flex gap-1">
          <span className="text-[7px] text-slate-600 self-center uppercase tracking-widest mr-0.5">Sort:</span>
          <button
            onClick={() => { if (sortBy === 'name') setSortDir(d => d === 'asc' ? 'desc' : 'asc'); else setSortBy('name'); }}
            className={`px-2 py-1 rounded text-[7px] font-mono uppercase tracking-wider border transition-all ${
              sortBy === 'name' ? 'bg-blue-500/20 border-blue-500/40 text-blue-400' : 'bg-white/5 border-white/10 text-slate-500'
            }`}
          >
            Name {sortBy === 'name' ? (sortDir === 'asc' ? '↑' : '↓') : ''}
          </button>
          <button
            onClick={() => { if (sortBy === 'category') setSortDir(d => d === 'asc' ? 'desc' : 'asc'); else { setSortBy('category'); setSortDir('asc'); } }}
            className={`px-2 py-1 rounded text-[7px] font-mono uppercase tracking-wider border transition-all ${
              sortBy === 'category' ? 'bg-blue-500/20 border-blue-500/40 text-blue-400' : 'bg-white/5 border-white/10 text-slate-500'
            }`}
          >
            Cat {sortBy === 'category' ? (sortDir === 'asc' ? '↑' : '↓') : ''}
          </button>
          <button
            onClick={() => setListView(prev => !prev)}
            className={`px-2 py-1 rounded text-[7px] font-mono uppercase tracking-wider border transition-all ${
              listView ? 'bg-blue-500/20 border-blue-500/40 text-blue-400' : 'bg-white/5 border-white/10 text-slate-500'
            }`}
            title={listView ? 'Grid view' : 'List view'}
          >
            {listView ? '▦' : '☰'}
          </button>
        </div>
      </div>

      <div className="flex flex-wrap gap-1.5">
        <button
          onClick={() => setActiveCategory(null)}
          className={`px-3 py-1 rounded-full text-[9px] font-bold uppercase tracking-[0.15em] transition-all ${
            activeCategory === null && !showFavorites
              ? 'bg-blue-500/20 text-blue-400 border border-blue-500/40 shadow-[0_0_12px_-4px_#3b82f6]'
              : 'bg-white/5 text-slate-500 border border-white/10 hover:text-slate-300 hover:border-white/20'
          }`}
        >
          All
        </button>
        <button
          onClick={() => { setShowFavorites(prev => !prev); if (showFavorites) setActiveCategory(null); }}
          className={`px-3 py-1 rounded-full text-[9px] font-bold uppercase tracking-[0.15em] transition-all ${
            showFavorites
              ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/40 shadow-[0_0_12px_-4px_#eab308]'
              : 'bg-white/5 text-slate-500 border border-white/10 hover:text-slate-300 hover:border-white/20'
          }`}
        >
          ★ Favorites {favCount > 0 && <span className="ml-1 text-[7px] opacity-70">({favCount})</span>}
        </button>
        {categories.map((cat) => {
          const color = stringToColor(cat);
          return (
            <button
              key={cat}
              onClick={() => { setActiveCategory(cat); setShowFavorites(false); }}
              className={`px-3 py-1 rounded-full text-[9px] font-bold uppercase tracking-[0.15em] transition-all ${
                activeCategory === cat && !showFavorites
                  ? 'border shadow-[0_0_12px_-4px] text-white'
                  : 'bg-white/5 text-slate-500 border border-white/10 hover:text-slate-300 hover:border-white/20'
              }`}
              style={activeCategory === cat && !showFavorites ? {
                backgroundColor: `${color}20`,
                borderColor: `${color}66`,
                color: color,
                boxShadow: `0 0 12px -4px ${color}`,
              } : {}}
            >
              {cat}
            </button>
          );
        })}
      </div>

      {listView ? (
        <div className="space-y-1 stagger-fade">
          {loading && Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="card p-3 animate-pulse flex gap-3 items-center">
              <div className="w-10 h-10 rounded bg-slate-800/50 flex-shrink-0" />
              <div className="flex-1 space-y-1">
                <div className="h-2 w-24 bg-slate-800/50 rounded" />
                <div className="h-2 w-48 bg-slate-800/30 rounded" />
              </div>
            </div>
          ))}
          {!loading && filtered.length === 0 && (
            <div className="text-center py-12 text-slate-600 text-[10px] uppercase tracking-widest font-mono">
              {showFavorites ? '☆ No favorited labs. Click ★ on a lab to add it.' : '∅ No labs match your search.'}
            </div>
          )}
          {!loading && filtered.map((lab) => {
            const color = stringToColor(lab.category);
            return (
              <button
                key={lab.id}
                onClick={() => setSelectedLab(lab)}
                className="card w-full text-left group flex items-center gap-3 p-3 hover:bg-white/[0.03] transition-all"
              >
                <div className="w-10 h-10 rounded-lg overflow-hidden bg-slate-800/50 flex-shrink-0">
                  {lab.images.length > 0 && (
                    <img src={`${API_URL}/simulations/${lab.images[0]}`} alt="" className="w-full h-full object-cover opacity-60" />
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-[7px] uppercase tracking-[0.2em] font-bold" style={{ color }}>{lab.category}</span>
                    <span className="text-[10px] font-semibold text-slate-200 truncate">{lab.name}</span>
                  </div>
                  <p className="text-[8px] text-slate-600 truncate">{lab.description}</p>
                </div>
                <button
                  onClick={(e) => { e.stopPropagation(); toggleFav(lab.id); }}
                  className={`text-[10px] flex-shrink-0 w-5 h-5 flex items-center justify-center rounded ${
                    favorites.has(lab.id) ? 'text-yellow-400' : 'text-slate-700'
                  }`}
                >
                  {favorites.has(lab.id) ? '★' : '☆'}
                </button>
              </button>
            );
          })}
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 stagger-fade">
          {loading && Array.from({ length: 8 }).map((_, i) => <LabsSkeletonCard key={i} />)}
          {!loading && filtered.length === 0 && (
            <div className="col-span-full text-center py-12 text-slate-600 text-[10px] uppercase tracking-widest font-mono">
              {showFavorites ? '☆ No favorited labs. Click ★ on a lab to add it.' : '∅ No labs match your search.'}
            </div>
          )}
          {!loading && filtered.map((lab) => {
            const color = stringToColor(lab.category);
            return (
              <button
                key={lab.id}
                onClick={() => setSelectedLab(lab)}
                className="card-accent text-left group overflow-hidden relative"
                style={{ '--accent': color } as React.CSSProperties}
              >
                <div className="h-36 overflow-hidden bg-slate-900/50">
                  {lab.images.length > 0 ? (
                    <img
                      src={`${API_URL}/simulations/${lab.images[0]}`}
                      alt={lab.name}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500 opacity-70 group-hover:opacity-100"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-slate-700 text-[10px] uppercase tracking-widest font-mono">
                      ∅ No preview
                    </div>
                  )}
                </div>
                <div className="p-3">
                  <span className="text-[7px] uppercase tracking-[0.2em] font-bold" style={{ color }}>{lab.category}</span>
                  <h3 className="font-semibold text-xs mt-1 leading-tight text-slate-200 group-hover:text-white transition-colors">{lab.name}</h3>
                  <p className="text-[9px] text-slate-500 mt-1 line-clamp-2 leading-relaxed">{lab.description}</p>
                </div>
                <div className="absolute top-2 left-2 w-2.5 h-2.5 border-t border-l opacity-15" style={{ borderColor: color }} />
                <div className="absolute bottom-2 right-2 w-2.5 h-2.5 border-b border-r opacity-15" style={{ borderColor: color }} />
                <button
                  onClick={(e) => { e.stopPropagation(); toggleFav(lab.id); }}
                  className={`absolute top-2 right-2 w-6 h-6 flex items-center justify-center rounded-full text-[10px] transition-all ${
                    favorites.has(lab.id)
                      ? 'text-yellow-400 bg-yellow-500/20 border border-yellow-500/40'
                      : 'text-slate-700 bg-black/30 border border-white/10 opacity-0 group-hover:opacity-100'
                  }`}
                >
                  {favorites.has(lab.id) ? '★' : '☆'}
                </button>
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}

function LabDetail({ lab, onBack, apiUrl, isFavorite, onToggleFav }: {
  lab: Lab; onBack: () => void; apiUrl: string; isFavorite: boolean; onToggleFav: () => void;
}) {
  const [params, setParams] = useState<ParamDef[]>([]);
  const [paramValues, setParamValues] = useState<Record<string, string>>({});
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<RunResult | null>(null);
  const [paramsLoading, setParamsLoading] = useState(true);
  const [lightbox, setLightbox] = useState<string | null>(null);
  const [galleryIdx, setGalleryIdx] = useState(0);
  const [runHistory, setRunHistory] = useState<RunHistoryEntry[]>(loadRunHistory);
  const [presets, setPresets] = useState<SavedPreset[]>(loadPresets);
  const [savingPreset, setSavingPreset] = useState('');
  const [showingSource, setShowingSource] = useState(false);
  const [sourceCode, setSourceCode] = useState('');
  const [sourceLoading, setSourceLoading] = useState(false);
  const [copiedKey, setCopiedKey] = useState<string | null>(null);

  useEffect(() => {
    setResult(null);
    setParamsLoading(true);
    setGalleryIdx(0);
    fetch(`${apiUrl}/labs/${lab.id}/params`)
      .then((r) => r.json())
      .then((data) => {
        const p: ParamDef[] = data.parameters || [];
        setParams(p);
        const initial: Record<string, string> = {};
        for (const param of p) {
          if (param.default !== null && param.default !== undefined) {
            initial[param.name] = String(param.default);
          }
        }
        setParamValues(initial);
      })
      .catch(() => {})
      .finally(() => setParamsLoading(false));
  }, [lab.id, apiUrl]);

  const loadSource = useCallback(async () => {
    setSourceLoading(true);
    setShowingSource(true);
    try {
      const res = await fetch(`${apiUrl}/labs/${lab.id}/source`);
      const data = await res.json();
      setSourceCode(data.source || '// Source not available');
    } catch {
      setSourceCode('// Failed to load source');
    } finally {
      setSourceLoading(false);
    }
  }, [lab.id, apiUrl]);

  const run = async () => {
    setRunning(true);
    setResult(null);
    try {
      const parsed: Record<string, number | string | boolean> = {};
      for (const param of params) {
        const raw = paramValues[param.name];
        if (raw === undefined || raw === '') continue;
        if (param.type === 'int') parsed[param.name] = parseInt(raw, 10);
        else if (param.type === 'float') parsed[param.name] = parseFloat(raw);
        else if (param.type === 'number') parsed[param.name] = raw.includes('.') ? parseFloat(raw) : parseInt(raw, 10);
        else if (param.type === 'bool') parsed[param.name] = raw === 'true' || raw === '1';
        else parsed[param.name] = raw;
      }

      const res = await fetch(`${apiUrl}/labs/${lab.id}/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(parsed),
      });
      const data = await res.json();
      setResult(data);

      if (data.compute_time_s != null) {
        setRunHistory(prev => {
          const next = [{ labId: lab.id, params: { ...paramValues }, time: Date.now(), computeTime: data.compute_time_s }, ...prev];
          saveRunHistory(next);
          return next;
        });
      }
    } catch (err: any) {
      setResult({ error: err.message });
    } finally {
      setRunning(false);
    }
  };

  const savePreset = () => {
    const name = savingPreset.trim();
    if (!name) return;
    const newPreset: SavedPreset = { labId: lab.id, name, values: { ...paramValues } };
    const updated = [...presets.filter(p => !(p.labId === lab.id && p.name === name)), newPreset];
    setPresets(updated);
    savePresets(updated);
    setSavingPreset('');
  };

  const loadPreset = (preset: SavedPreset) => {
    setParamValues({ ...preset.values });
  };

  const deletePreset = (name: string) => {
    const updated = presets.filter(p => !(p.labId === lab.id && p.name === name));
    setPresets(updated);
    savePresets(updated);
  };

  const copyData = (data: Record<string, string>) => {
    navigator.clipboard.writeText(JSON.stringify(data, null, 2));
    setCopiedKey('data');
    setTimeout(() => setCopiedKey(null), 1500);
  };

  const labPresets = presets.filter(p => p.labId === lab.id);

  const hardcodedPresets = [
    { label: 'Defaults', values: {} },
    ...(params.some((p) => p.name === 'T_millions')
      ? [
          { label: 'Sun Core (15MK)', values: { T_millions: '15' } },
          { label: 'Hot Star (40MK)', values: { T_millions: '40' } },
        ]
      : []),
    ...(params.some((p) => p.name === 'M1')
      ? [
          { label: 'GW150914 (30+30)', values: { M1: '30', M2: '30' } },
          { label: 'Equal Mass (10+10)', values: { M1: '10', M2: '10' } },
        ]
      : []),
    ...(params.some((p) => p.name === 'depth')
      ? [
          { label: 'Shallow (4)', values: { depth: '4' } },
          { label: 'Deep (10)', values: { depth: '10' } },
        ]
      : []),
    ...(params.some((p) => p.name === 'omega_low')
      ? [
          { label: 'Otto Cycle', values: { omega_low: '1.0', omega_high: '3.0', T_hot: '5.0', T_cold: '0.1' } },
        ]
      : []),
    ...(params.some((p) => p.name === 'T_hot')
      ? [
          { label: 'Hot Bath (T=5)', values: { T_hot: '5.0', T_cold: '0.1' } },
        ]
      : []),
  ];

  const displayImages = result?.image ? [result.image] : lab.images;
  const labHistory = runHistory.filter(h => h.labId === lab.id);
  const color = stringToColor(lab.category);

  return (
    <div className="space-y-6 stagger-fade">
      {lightbox && <Lightbox src={lightbox} alt={`${lab.name}`} onClose={() => setLightbox(null)} />}

      <div className="flex items-center justify-between gap-3 flex-wrap">
        <button
          onClick={onBack}
          className="card px-3 py-2 text-[10px] font-mono text-slate-400 hover:text-white transition-colors flex items-center gap-2 w-fit"
        >
          <span className="text-slate-600">&larr;</span> Back to labs
        </button>
        <div className="flex gap-2">
          <button onClick={loadSource} className="px-3 py-1.5 rounded-lg text-[7px] font-mono uppercase tracking-wider border border-white/10 text-slate-500 hover:text-slate-300 bg-white/5 transition-all">
            {showingSource ? 'Source ▲' : 'Source ▼'}
          </button>
          <button
            onClick={onToggleFav}
            className={`px-3 py-1.5 rounded-lg text-[9px] font-bold uppercase tracking-[0.15em] border transition-all ${
              isFavorite
                ? 'bg-yellow-500/20 border-yellow-500/40 text-yellow-400'
                : 'bg-white/5 border-white/10 text-slate-500 hover:text-slate-300'
            }`}
          >
            {isFavorite ? '★ Favorited' : '☆ Add Favorite'}
          </button>
        </div>
      </div>

      {/* Source code viewer */}
      {showingSource && (
        <div className="card overflow-hidden">
          <div className="flex items-center justify-between px-4 py-2 border-b border-slate-800/50">
            <span className="text-[7px] font-mono text-slate-600 uppercase tracking-widest">Source</span>
            <button onClick={() => setShowingSource(false)} className="text-[8px] text-slate-600 hover:text-slate-400">&times;</button>
          </div>
          <pre className="p-4 text-[9px] font-mono text-slate-400 overflow-x-auto max-h-96 overflow-y-auto leading-relaxed">
            {sourceLoading ? (
              <span className="text-slate-700">Loading...</span>
            ) : sourceCode ? (
              sourceCode
            ) : (
              <span className="text-slate-700">Click "Source ▼" to load</span>
            )}
          </pre>
        </div>
      )}

      <div className="card p-5">
        <div className="flex items-center gap-3 mb-2">
          <span className="text-[8px] uppercase tracking-[0.2em] font-bold" style={{ color }}>{lab.category}</span>
          <span className="text-[7px] font-mono text-slate-700">{lab.id}</span>
        </div>
        <h2 className="text-lg font-bold mt-1 text-slate-100">{lab.name}</h2>
        <p className="text-[11px] text-slate-500 mt-2 leading-relaxed">{lab.description}</p>
      </div>

      {displayImages.length > 0 && !result && (
        <div className="space-y-2">
          <div className={`grid gap-4 ${displayImages.length > 1 ? 'grid-cols-2' : 'grid-cols-1'}`}>
            {displayImages.map((img, i) => (
              <div key={i} className="card overflow-hidden cursor-pointer group relative" onClick={() => setLightbox(typeof img === 'string' && img.startsWith('data:') ? img : `${apiUrl}/simulations/${img}`)}>
                <img
                  src={typeof img === 'string' && img.startsWith('data:') ? img : `${apiUrl}/simulations/${img}`}
                  alt={`${lab.name} - ${typeof img === 'string' ? img : i}`}
                  className="w-full h-auto group-hover:scale-105 transition-transform duration-500"
                />
                <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors flex items-center justify-center">
                  <span className="text-white/0 group-hover:text-white/70 text-[10px] font-mono uppercase tracking-widest transition-all">🔍 View</span>
                </div>
              </div>
            ))}
          </div>
          {displayImages.length > 1 && (
            <div className="flex justify-center gap-1.5">
              {displayImages.map((_, i) => (
                <button
                  key={i}
                  onClick={() => setGalleryIdx(i)}
                  className={`w-2 h-2 rounded-full transition-all ${i === galleryIdx ? 'bg-blue-400 w-4' : 'bg-slate-700 hover:bg-slate-500'}`}
                />
              ))}
            </div>
          )}
        </div>
      )}

      {result && (
        <div className="space-y-4 stagger-fade">
          {result.compute_time_s != null && (
            <div className="flex items-center gap-2 text-[10px] font-mono text-slate-500 card px-3 py-2">
              <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse" />
              Computed in {result.compute_time_s < 1 ? (result.compute_time_s * 1000).toFixed(0) + 'ms' : result.compute_time_s.toFixed(2) + 's'}
            </div>
          )}
          {result.image && (
            <div className="card overflow-hidden relative group cursor-pointer" onClick={() => setLightbox(`data:image/png;base64,${result.image}`)}>
              <img
                src={`data:image/png;base64,${result.image}`}
                alt="Simulation output"
                className="w-full h-auto"
              />
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  const a = document.createElement('a');
                  a.href = `data:image/png;base64,${result.image}`;
                  a.download = `${lab.id}_result.png`;
                  a.click();
                }}
                className="absolute top-2 right-2 px-3 py-1.5 bg-white/10 hover:bg-white/20 backdrop-blur-xl border border-white/20 rounded-lg text-[10px] text-slate-300 opacity-0 group-hover:opacity-100 transition-opacity font-mono"
              >
                Download PNG
              </button>
            </div>
          )}
          {result.text && (
            <div className="card p-4">
              <pre className="text-xs text-slate-400 font-mono whitespace-pre-wrap leading-relaxed">{result.text}</pre>
            </div>
          )}
          {result.data && (
            <div className="card p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-[10px] font-mono text-slate-500">Result Data</span>
                <button
                  onClick={() => copyData(result.data!)}
                  className="px-2 py-1 rounded text-[7px] font-mono uppercase tracking-wider border border-white/10 text-slate-500 hover:text-slate-300 transition-all"
                >
                  {copiedKey === 'data' ? '✓ Copied' : 'Copy JSON'}
                </button>
              </div>
              <dl className="space-y-1.5 text-xs">
                {Object.entries(result.data).map(([k, v]) => (
                  <div key={k} className="flex gap-3">
                    <dt className="text-slate-600 font-mono">{k}:</dt>
                    <dd className="text-slate-300">{v}</dd>
                  </div>
                ))}
              </dl>
            </div>
          )}
          {result.error && (
            <div className="card p-4 border-l-2 border-red-500/50">
              <p className="text-[10px] font-mono text-red-300">{result.error}</p>
            </div>
          )}
        </div>
      )}

      {params.length > 0 && !paramsLoading && (
        <div className="card p-5 space-y-4">
          <div className="flex items-center justify-between flex-wrap gap-2">
            <h3 className="font-bold text-[10px] uppercase tracking-[0.2em] text-blue-400">
              Parameters
            </h3>
            <div className="flex gap-1.5 flex-wrap">
              {hardcodedPresets.length > 0 && (
                <span className="text-[7px] text-slate-600 self-center mr-0.5 uppercase tracking-widest">Presets:</span>
              )}
              {hardcodedPresets.map((preset) => (
                <button
                  key={preset.label}
                  onClick={() => {
                    const merged = { ...paramValues };
                    for (const [k, v] of Object.entries(preset.values)) {
                      merged[k] = v;
                    }
                    setParamValues(merged);
                  }}
                  className="px-2 py-1 bg-white/5 hover:bg-white/10 rounded text-[8px] text-slate-500 hover:text-slate-300 transition-colors font-mono"
                >
                  {preset.label}
                </button>
              ))}
            </div>
          </div>

          {/* User saved presets */}
          {labPresets.length > 0 && (
            <div className="flex flex-wrap gap-1">
              <span className="text-[7px] text-slate-600 self-center uppercase tracking-widest mr-0.5">Saved:</span>
              {labPresets.map((p) => (
                <div key={p.name} className="flex items-center gap-0.5">
                  <button
                    onClick={() => loadPreset(p)}
                    className="px-2 py-0.5 bg-emerald-500/10 hover:bg-emerald-500/20 rounded text-[7px] font-mono text-emerald-500 transition-colors"
                  >
                    {p.name}
                  </button>
                  <button
                    onClick={() => deletePreset(p.name)}
                    className="px-1 py-0.5 text-[7px] text-slate-600 hover:text-red-400 transition-colors"
                  >
                    ✕
                  </button>
                </div>
              ))}
            </div>
          )}

          {/* Save current config */}
          <div className="flex gap-2">
            <input
              type="text"
              value={savingPreset}
              onChange={(e) => setSavingPreset(e.target.value)}
              placeholder="Save config as..."
              className="flex-1 bg-white/5 border border-white/10 rounded px-3 py-1.5 text-[9px] text-slate-200 font-mono focus:outline-none focus:border-blue-500/50 placeholder-slate-700"
              onKeyDown={(e) => { if (e.key === 'Enter') savePreset(); }}
            />
            <button
              onClick={savePreset}
              disabled={!savingPreset.trim()}
              className="px-3 py-1.5 rounded text-[8px] font-mono uppercase tracking-wider bg-emerald-600/60 hover:bg-emerald-500/60 disabled:bg-slate-800/50 disabled:text-slate-600 text-white transition-all border border-emerald-400/20 disabled:border-slate-700"
            >
              Save
            </button>
          </div>

          {params.map((param) => {
            const val = paramValues[param.name] ?? '';
            const isNumeric = param.type === 'int' || param.type === 'float' || param.type === 'number';
            const defaultNum = param.default != null ? Number(param.default) : 0;

            return (
              <div key={param.name}>
                <label className="block text-[9px] text-slate-500 mb-1.5 font-mono">
                  {param.name}
                  {param.required && <span className="text-red-400 ml-1">*</span>}
                  <span className="text-slate-700 ml-2">({param.type})</span>
                </label>
                {param.type === 'bool' ? (
                  <input
                    type="checkbox"
                    checked={val === 'true'}
                    onChange={(e) =>
                      setParamValues((prev) => ({ ...prev, [param.name]: e.target.checked ? 'true' : 'false' }))
                    }
                    className="w-4 h-4 accent-blue-500"
                  />
                ) : isNumeric ? (
                  <div className="flex gap-3 items-center">
                    <input
                      type="range"
                      min={defaultNum > 0 ? 0 : defaultNum * 2}
                      max={defaultNum > 0 ? defaultNum * 4 || 100 : Math.abs(defaultNum) * 4 || 100}
                      step={param.type === 'int' ? '1' : 'any'}
                      value={val === '' ? 0 : parseFloat(val) || 0}
                      onChange={(e) =>
                        setParamValues((prev) => ({ ...prev, [param.name]: e.target.value }))
                      }
                      className="flex-1 h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-blue-500"
                    />
                    <input
                      type="number"
                      step={param.type === 'int' ? '1' : 'any'}
                      value={val}
                      onChange={(e) =>
                        setParamValues((prev) => ({ ...prev, [param.name]: e.target.value }))
                      }
                      placeholder={param.default != null ? String(param.default) : ''}
                      className="w-16 bg-white/5 border border-white/10 rounded px-2 py-1.5 text-xs text-slate-200 text-center font-mono focus:outline-none focus:border-blue-500/50"
                    />
                  </div>
                ) : (
                  <input
                    type="text"
                    value={val}
                    onChange={(e) =>
                      setParamValues((prev) => ({ ...prev, [param.name]: e.target.value }))
                    }
                    placeholder={param.default != null ? String(param.default) : ''}
                    className="w-full bg-white/5 border border-white/10 rounded px-3 py-2 text-xs text-slate-200 font-mono focus:outline-none focus:border-blue-500/50"
                  />
                )}
              </div>
            );
          })}

          <button
            onClick={run}
            disabled={running}
            className="w-full px-6 py-2.5 bg-blue-600/80 hover:bg-blue-500/80 disabled:bg-slate-800/50 disabled:text-slate-600 text-white rounded-lg text-[10px] font-bold uppercase tracking-[0.2em] transition-all backdrop-blur-xl border border-blue-400/20 hover:border-blue-400/40 disabled:border-slate-700"
          >
            {running ? (
              <span className="flex items-center justify-center gap-2">
                <span className="w-3 h-3 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Running...
              </span>
            ) : (
              'Run Simulation'
            )}
          </button>
        </div>
      )}

      {params.length === 0 && !paramsLoading && (
        <button
          onClick={run}
          disabled={running}
          className="w-full px-6 py-2.5 bg-blue-600/80 hover:bg-blue-500/80 disabled:bg-slate-800/50 disabled:text-slate-600 text-white rounded-lg text-[10px] font-bold uppercase tracking-[0.2em] transition-all backdrop-blur-xl border border-blue-400/20 hover:border-blue-400/40 disabled:border-slate-700"
        >
          {running ? 'Running...' : 'Run Simulation'}
        </button>
      )}

      {labHistory.length > 0 && (
        <div className="card p-4">
          <h3 className="font-bold text-[10px] uppercase tracking-[0.2em] text-slate-500 mb-3">Recent Runs</h3>
          <div className="space-y-1.5 max-h-32 overflow-y-auto">
            {labHistory.map((h, i) => (
              <div key={i} className="flex justify-between items-center text-[8px] font-mono">
                <span className="text-slate-600">{new Date(h.time).toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' })}</span>
                <span className="text-slate-500 truncate mx-2 flex-1 text-center">
                  {Object.entries(h.params).map(([k, v]) => `${k}=${v}`).join(', ') || 'defaults'}
                </span>
                <span className="text-slate-600 tabular-nums">{h.computeTime < 1 ? (h.computeTime * 1000).toFixed(0) + 'ms' : h.computeTime.toFixed(2) + 's'}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="card p-4">
        <h3 className="font-bold text-[10px] uppercase tracking-[0.2em] text-slate-500 mb-3">Lab Info</h3>
        <dl className="space-y-2 text-[10px] font-mono">
          <div className="flex justify-between">
            <dt className="text-slate-600">Lab ID</dt>
            <dd className="text-slate-400">{lab.id}</dd>
          </div>
          <div className="flex justify-between">
            <dt className="text-slate-600">Category</dt>
            <dd className="text-slate-400">{lab.category}</dd>
          </div>
          <div className="flex justify-between">
            <dt className="text-slate-600">Output Files</dt>
            <dd className="text-slate-400">{lab.images.length > 0 ? lab.images.join(', ') : 'None'}</dd>
          </div>
        </dl>
      </div>
    </div>
  );
}

interface LengthContractionBarProps {
  gamma: number;
  realDistM: number;
  contractedDistM: number;
}

export function LengthContractionBar({ gamma, realDistM, contractedDistM }: LengthContractionBarProps) {
  if (gamma <= 1) return null;
  const ratio = Math.max(0.05, 1 / gamma);

  return (
    <div className="card-accent p-5" style={{ '--accent': '#a855f7' } as React.CSSProperties}>
      <div className="flex items-center gap-2 mb-3">
        <span className="w-1.5 h-1.5 rounded-full bg-purple-500" />
        <h2 className="font-bold text-[10px] uppercase tracking-[0.2em] text-slate-400">Length Contraction</h2>
      </div>
      <div className="space-y-3">
        <div>
          <div className="flex justify-between text-[8px] text-slate-600 mb-1">
            <span>Classical</span>
            <span className="font-mono text-slate-400">{(realDistM / 1000).toFixed(1)} km</span>
          </div>
          <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden">
            <div className="h-full bg-slate-600/50 rounded-full" style={{ width: '100%' }} />
          </div>
        </div>
        <div>
          <div className="flex justify-between text-[8px] text-slate-600 mb-1">
            <span className="text-purple-400/80">Relativistic</span>
            <span className="font-mono text-purple-400">{(contractedDistM / 1000).toFixed(3)} km</span>
          </div>
          <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-purple-600 to-purple-400 rounded-full transition-all duration-500"
              style={{ width: `${ratio * 100}%` }}
            />
          </div>
        </div>
      </div>
      <p className="text-[7px] text-slate-700 text-center mt-2 uppercase tracking-[0.15em]">
        Space contracts ×{ratio.toFixed(4)} along travel axis
      </p>
    </div>
  );
}


interface LogbookPanelProps {
  logbook: any[];
}

export function LogbookPanel({ logbook }: LogbookPanelProps) {
  const [open, setOpen] = useState(false);
  const recent = logbook.slice(-20).reverse();

  return (
    <div className="card overflow-hidden" style={{ '--accent': '#f59e0b' } as React.CSSProperties}>
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between px-5 py-3 hover:bg-white/[0.02] transition-colors"
      >
        <div className="flex items-center gap-2">
          <span className="w-1.5 h-1.5 rounded-full bg-amber-500" />
          <h2 className="font-bold text-[10px] uppercase tracking-[0.2em] text-slate-400">
            Journey Log
          </h2>
          <span className="text-[8px] font-mono text-slate-700">({logbook.length})</span>
        </div>
        {open ? <ChevronUp size={14} className="text-slate-600" /> : <ChevronDown size={14} className="text-slate-600" />}
      </button>
      {open && (
        <div className="max-h-48 overflow-y-auto border-t border-slate-800/50">
          {recent.length === 0 ? (
            <p className="text-[9px] text-slate-700 text-center py-8 italic tracking-wider">No entries yet. Start moving!</p>
          ) : (
            recent.map((entry, i) => (
              <div key={entry.timestamp ?? i} className="flex items-center justify-between px-5 py-1.5 text-[9px] border-b border-slate-800/30 hover:bg-white/[0.01]">
                <span className="font-mono text-slate-600 w-16">
                  {new Date(entry.timestamp).toLocaleTimeString()}
                </span>
                <span className="font-mono text-blue-400/80 w-14 text-right">
                  {(entry.speed_kmh || 0).toFixed(0)} km/h
                </span>
                <span className="font-mono text-emerald-400/80 w-12 text-right">
                  γ={entry.gamma?.toFixed(2) || '1.00'}
                </span>
                <span className="font-mono text-pink-400/80 w-16 text-right">
                  {entry.time_dilation_ns?.toFixed(1) || '0'} ns
                </span>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}


delete (L.Icon.Default.prototype as unknown as Record<string, unknown>)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

interface MapSectionProps {
  userPos: Position | null;
  destPos: DestPosition | null;
  onPinDestination: (pos: DestPosition) => void;
  gamma: number;
  bearing: number;
  route: RouteData | null;
}

function MapEvents({ onPin }: { onPin: (pos: DestPosition) => void }) {
  useMapEvents({
    click(e) {
      const label = prompt('Destination label:', 'Pin');
      if (label) onPin({ lat: e.latlng.lat, lon: e.latlng.lng, label });
    },
  });
  return null;
}

function RecenterMap({ pos }: { pos: Pick<Position, 'lat' | 'lon'> }) {
  const map = useMap();
  useEffect(() => {
    map.setView([pos.lat, pos.lon]);
  }, [pos, map]);
  return null;
}

function FitRoute({ route }: { route: RouteData | null }) {
  const map = useMap();
  useEffect(() => {
    if (route?.coordinates.length) {
      const bounds = L.latLngBounds(route.coordinates.map(c => L.latLng(c[0], c[1])));
      map.fitBounds(bounds, { padding: [40, 40] });
    }
  }, [route, map]);
  return null;
}

export function MapSection({ userPos, destPos, onPinDestination, gamma, bearing, route }: MapSectionProps) {
  const contractionStyle: React.CSSProperties = {
    transform: `rotate(${bearing}deg) scaleX(${1 / gamma}) rotate(-${bearing}deg)`,
    transition: 'transform 0.5s cubic-bezier(0.4, 0, 0.2, 1)',
  };

  return (
    <div className="bg-slate-900 border border-slate-800 p-2 rounded-2xl shadow-xl overflow-hidden relative group">
      <h2 className="absolute top-4 left-4 z-[1000] text-[9px] font-bold uppercase tracking-widest bg-slate-900/80 p-2 rounded border border-slate-700">
        Navigation Map
      </h2>
      {route && (
        <div className="absolute top-4 right-4 z-[1000] text-[7px] font-mono bg-slate-900/80 p-2 rounded border border-slate-700 text-slate-400 space-y-0.5">
          <div>{route.steps.length} turns</div>
          <div>{(route.distance / 1000).toFixed(1)} km</div>
          <div>{Math.floor(route.duration / 60)} min</div>
        </div>
      )}
      <div className="h-64 w-full rounded-xl overflow-hidden" style={contractionStyle}>
        <MapContainer center={[0, 0]} zoom={13} style={{ height: '100%', width: '100%' }} zoomControl={false}>
          <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
          <MapEvents onPin={onPinDestination} />
          {userPos && <RecenterMap pos={userPos} />}
          {route && <FitRoute route={route} />}
          {route && (
            <Polyline
              positions={route.coordinates}
              pathOptions={{ color: '#3b82f6', weight: 3, opacity: 0.7, dashArray: '8, 12' }}
            />
          )}
          {userPos && (
            <>
              <Marker position={[userPos.lat, userPos.lon]}>
                <Popup>Current position</Popup>
              </Marker>
              <Circle
                center={[userPos.lat, userPos.lon]}
                radius={userPos.acc}
                pathOptions={{ color: 'cyan', fillColor: 'cyan', fillOpacity: 0.1, weight: 1 }}
              />
            </>
          )}
          {destPos && (
            <Marker position={[destPos.lat, destPos.lon]}>
              <Popup>{destPos.label}</Popup>
            </Marker>
          )}
        </MapContainer>
      </div>
      {route && route.steps.length > 0 && (
        <div className="p-2 max-h-16 overflow-y-auto space-y-0.5">
          {route.steps.slice(0, 5).map((s, i) => (
            <p key={i} className="text-[6px] font-mono text-slate-600 truncate">
              <span className="text-blue-400">▸</span> {s.instruction}
              <span className="text-slate-700 ml-1">({(s.distance).toFixed(0)}m)</span>
            </p>
          ))}
          {route.steps.length > 5 && (
            <p className="text-[5px] text-slate-700 text-center">+{route.steps.length - 5} more turns</p>
          )}
        </div>
      )}
    </div>
  );
}


interface MetricCardsProps {
  metrics: Metrics | null;
  cumulativeDilation: number;
  userPos: Position | null;
  onResetClock: () => void;
}

function Card({ icon: Icon, label, accent, children, value, unit }: any) {
  return (
    <div className="card-accent" style={{ '--accent': accent } as React.CSSProperties}>
      <div className="p-5 h-full flex flex-col justify-between">
        <div>
          <div className="flex items-center gap-2 mb-3" style={{ color: accent }}>
            <Icon size={16} />
            <span className="font-bold uppercase tracking-[0.2em] text-[10px]" style={{ color: accent }}>{label}</span>
          </div>
          {value !== undefined
            ? <AnimatedValue value={value} unit={unit} color={accent} decimals={4} si={false} />
            : <div className="h-6 w-24 rounded bg-slate-800/50 animate-pulse" />
          }
        </div>
        <div className="mt-3">
          {children}
        </div>
      </div>
      <div className="absolute top-2 left-2 w-3 h-3 border-t border-l opacity-15" style={{ borderColor: accent }} />
      <div className="absolute bottom-2 right-2 w-3 h-3 border-b border-r opacity-15" style={{ borderColor: accent }} />
    </div>
  );
}

export function MetricCards({ metrics, cumulativeDilation, userPos, onResetClock }: MetricCardsProps) {
  const dopplerLeft = Math.min(100, Math.max(0, ((metrics?.doppler_factor ?? 1) - 1) * 500 + 50));
  const netTimeFlow = metrics
    ? (1 - (metrics.time_dilation_ns + metrics.grav_dilation_ns) / 1e9)
    : 1;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5 stagger-fade">
      <Card
        icon={Timer}
        label="Age Divergence"
        value={cumulativeDilation}
        unit="ns"
        accent="#ec4899"
      >
        <p className="text-[8px] opacity-40 tracking-wider italic mb-2">Younger than station observer</p>
        <button onClick={onResetClock} className="text-[7px] uppercase tracking-[0.3em] opacity-30 hover:opacity-70 transition-opacity">
          [ Reset ]
        </button>
      </Card>

      <Card
        icon={Zap}
        label="Doppler Shift"
        accent="#f97316"
      >
        <div className="h-3 w-full rounded-full bg-gradient-to-r from-red-600 via-green-400 to-blue-600 relative overflow-hidden mt-1">
          <div
            className="absolute top-0 bottom-0 w-0.5 bg-white shadow-[0_0_8px_rgba(255,255,255,0.9)] transition-all duration-300"
            style={{ left: `${dopplerLeft}%` }}
          />
        </div>
        <div className="flex justify-between text-[7px] mt-1.5 uppercase tracking-tighter opacity-40">
          <span style={{ color: '#f87171' }}>Redshift</span>
          <span className="font-mono text-white/60 text-[9px]">{(metrics?.doppler_factor ?? 1).toFixed(4)}x</span>
          <span style={{ color: '#60a5fa' }}>Blueshift</span>
        </div>
      </Card>

      <Card
        icon={Ruler}
        label="Altitude GR"
        value={metrics?.grav_dilation_ns ?? undefined}
        unit="ns/s"
        accent="#818cf8"
      >
        <p className="text-[8px] opacity-40 tracking-wider mt-1">Alt: {userPos ? userPos.alt.toFixed(1) : '0'}m</p>
      </Card>

      <Card
        icon={Timer}
        label="Net Time Flow"
        value={netTimeFlow}
        unit="τ/t"
        accent="#10b981"
      >
        <div className="mt-2 h-1 w-full rounded-full bg-slate-800 overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-emerald-500 to-emerald-300 rounded-full transition-all duration-500"
            style={{ width: `${Math.min(100, netTimeFlow * 100)}%` }}
          />
        </div>
      </Card>
    </div>
  );
}


interface MetricHistoryProps {
  data: { gamma: number; speed: number; dilation: number }[];
}

export function MetricHistory({ data }: MetricHistoryProps) {
  const gammaRef = useRef<HTMLCanvasElement>(null);
  const speedRef = useRef<HTMLCanvasElement>(null);
  const dilationRef = useRef<HTMLCanvasElement>(null);

  const drawChart = (canvas: HTMLCanvasElement | null, values: number[], color: string, label: string) => {
    if (!canvas || values.length < 2) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const W = canvas.width, H = canvas.height;
    ctx.clearRect(0, 0, W, H);

    const max = Math.max(...values, 0.001);
    const min = Math.min(...values, 0);
    const range = max - min || 1;
    const steps = values.length;

    // Gradient fill
    ctx.beginPath();
    for (let i = 0; i < steps; i++) {
      const x = (i / (steps - 1)) * (W - 4) + 2;
      const y = H - 4 - ((values[i] - min) / range) * (H - 8);
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.lineTo((steps - 1) / (steps - 1) * (W - 4) + 2, H - 4);
    ctx.lineTo(2, H - 4);
    ctx.closePath();
    const grad = ctx.createLinearGradient(0, 0, 0, H);
    grad.addColorStop(0, `${color}40`);
    grad.addColorStop(1, `${color}05`);
    ctx.fillStyle = grad;
    ctx.fill();

    // Line
    ctx.beginPath();
    for (let i = 0; i < steps; i++) {
      const x = (i / (steps - 1)) * (W - 4) + 2;
      const y = H - 4 - ((values[i] - min) / range) * (H - 8);
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.strokeStyle = color;
    ctx.lineWidth = 1.5;
    ctx.shadowColor = color;
    ctx.shadowBlur = 4;
    ctx.stroke();
    ctx.shadowBlur = 0;

    // Label
    ctx.fillStyle = 'rgba(148, 163, 184, 0.4)';
    ctx.font = '6px monospace';
    ctx.textAlign = 'left';
    ctx.fillText(label, 3, 8);
  };

  useEffect(() => {
    if (data.length < 2) return;
    drawChart(gammaRef.current, data.map(d => d.gamma), '#10b981', 'γ');
    drawChart(speedRef.current, data.map(d => Math.log10(d.speed + 1)), '#3b82f6', 'log km/h');
    drawChart(dilationRef.current, data.map(d => d.dilation * 1e9), '#ec4899', 'ns/s');
  }, [data]);

  return (
    <div className="grid grid-cols-3 gap-2">
      <canvas ref={gammaRef} width={100} height={32} className="w-full h-8 rounded" />
      <canvas ref={speedRef} width={100} height={32} className="w-full h-8 rounded" />
      <canvas ref={dilationRef} width={100} height={32} className="w-full h-8 rounded" />
    </div>
  );
}


interface MinkowskiDiagramProps {
  simultaneityTilt: number;
}

const lightCone = [
  { x: -1.2, t: 1.2 },
  { x: 0, t: 0 },
  { x: 1.2, t: 1.2 },
];

export function MinkowskiDiagram({ simultaneityTilt }: MinkowskiDiagramProps) {
  const worldLine = [
    { x: 0, t: 0 },
    { x: simultaneityTilt, t: 1 },
  ];

  return (
    <div className="card p-5" style={{ '--accent': '#3b82f6' } as React.CSSProperties}>
      <div className="flex items-center gap-2 mb-4">
        <span className="w-1.5 h-1.5 rounded-full bg-blue-500" />
        <h2 className="font-bold text-[10px] uppercase tracking-[0.2em] text-slate-400">
          Minkowski Space-Time
        </h2>
      </div>
      <div className="h-[220px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="x" type="number" domain={[-1.2, 1.2]} hide />
            <YAxis dataKey="t" type="number" domain={[0, 1.2]} hide />
            <Tooltip content={() => null} />
            <Line data={lightCone} dataKey="t" stroke="#334155" strokeDasharray="5 5" dot={false} isAnimationActive={false} />
            <Line data={worldLine} dataKey="t" stroke="#3b82f6" strokeWidth={3} dot={false} isAnimationActive={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
      <p className="text-[7px] text-slate-700 text-center uppercase tracking-[0.2em] mt-2">
        Blue line = Your worldline · Dashed = Light cone (c)
      </p>
    </div>
  );
}


export function MouseGlow() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resize();
    window.addEventListener('resize', resize);

    let mx = -200, my = -200;
    let frame: number;

    const handleMouse = (e: MouseEvent) => {
      mx = e.clientX;
      my = e.clientY;
    };
    window.addEventListener('mousemove', handleMouse);

    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      const grad = ctx.createRadialGradient(mx, my, 0, mx, my, 200);
      grad.addColorStop(0, 'rgba(100, 180, 255, 0.04)');
      grad.addColorStop(0.5, 'rgba(100, 180, 255, 0.015)');
      grad.addColorStop(1, 'transparent');
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      frame = requestAnimationFrame(animate);
    };
    animate();

    return () => {
      cancelAnimationFrame(frame);
      window.removeEventListener('resize', resize);
      window.removeEventListener('mousemove', handleMouse);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 pointer-events-none z-[3]"
    />
  );
}


interface ParallaxCardProps {
  children: ReactNode;
  className?: string;
  style?: React.CSSProperties;
  maxTilt?: number;
}

export function ParallaxCard({ children, className = '', style, maxTilt = 8 }: ParallaxCardProps) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    const handleMouseMove = (e: MouseEvent) => {
      const rect = el.getBoundingClientRect();
      const x = (e.clientX - rect.left) / rect.width;
      const y = (e.clientY - rect.top) / rect.height;
      const tiltX = (y - 0.5) * maxTilt;
      const tiltY = (0.5 - x) * maxTilt;
      el.style.transform = `perspective(600px) rotateX(${tiltX}deg) rotateY(${tiltY}deg) scale3d(1.02, 1.02, 1.02)`;
    };

    const handleMouseLeave = () => {
      el.style.transform = 'perspective(600px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)';
    };

    el.addEventListener('mousemove', handleMouseMove);
    el.addEventListener('mouseleave', handleMouseLeave);

    return () => {
      el.removeEventListener('mousemove', handleMouseMove);
      el.removeEventListener('mouseleave', handleMouseLeave);
    };
  }, [maxTilt]);

  return (
    <div
      ref={ref}
      className={`transition-transform duration-200 ease-out ${className}`}
      style={{ transformStyle: 'preserve-3d', ...style }}
    >
      {children}
    </div>
  );
}


interface Star {
  x: number; y: number; z: number;
  r: number; a: number; speed: number; hue: number;
}

interface ParticleBackgroundProps {
  warpMode?: boolean;
  speed?: number;
}

export function ParticleBackground({ warpMode = false, speed = 0 }: ParticleBackgroundProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resize();
    window.addEventListener('resize', resize);

    // Normal stars
    const stars: Star[] = [];
    const count = Math.min(200, Math.floor((canvas.width * canvas.height) / 8000));
    for (let i = 0; i < count; i++) {
      stars.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        z: Math.random() * 3 + 0.5,
        r: Math.random() * 2 + 0.3,
        a: Math.random() * 0.6 + 0.05,
        speed: Math.random() * 0.3 + 0.05,
        hue: Math.random() * 60 + 200,
      });
    }

    let frame: number;
    let time = 0;
    let glitchTimer = 0;
    let glitchActive = false;

    const animate = () => {
      time += 0.002;
      glitchTimer -= 1;
      if (glitchTimer <= 0) {
        glitchActive = Math.random() < 0.008;
        glitchTimer = 200 + Math.random() * 600;
      }

      ctx.save();

      // Glitch offset
      if (glitchActive) {
        const gx = (Math.random() - 0.5) * 6;
        const gy = (Math.random() - 0.5) * 3;
        ctx.translate(gx, gy);
      }

      ctx.clearRect(-10, -10, canvas.width + 20, canvas.height + 20);

      // Nebula glow patches
      for (let i = 0; i < 3; i++) {
        const gx = canvas.width * (0.3 + 0.4 * Math.sin(time * 0.3 + i * 2));
        const gy = canvas.height * (0.3 + 0.4 * Math.cos(time * 0.4 + i * 2));
        const grad = ctx.createRadialGradient(gx, gy, 0, gx, gy, canvas.height * 0.6);
        const hues = [210, 180, 240];
        grad.addColorStop(0, `hsla(${hues[i]}, 60%, 30%, 0.03)`);
        grad.addColorStop(1, 'transparent');
        ctx.fillStyle = grad;
        ctx.fillRect(-10, -10, canvas.width + 20, canvas.height + 20);
      }

      if (warpMode) {
        // ---- Hyperspace warp tunnel ----
        const cx = canvas.width / 2 + (Math.random() - 0.5) * 30 * (glitchActive ? 1 : 0);
        const cy = canvas.height / 2 + (Math.random() - 0.5) * 20 * (glitchActive ? 1 : 0);
        const maxZ = 8;
        const tunnelStars = 120;

        // Perspective star field centered on vanishing point
        for (let i = 0; i < tunnelStars; i++) {
          const angle = Math.random() * Math.PI * 2;
          const rad = Math.random() * Math.max(canvas.width, canvas.height) * 0.6;
          let z = Math.random() * maxZ + 0.1;
          const speed = 0.03 + Math.random() * 0.07;

          z -= speed * 2.5;
          if (z <= 0.1) {
            // Reset to outer edge
            z = maxZ;
          }

          const px = cx + (rad * (0.3 + 0.7 * (1 - z / maxZ))) * Math.cos(angle);
          const py = cy + (rad * (0.3 + 0.7 * (1 - z / maxZ))) * Math.sin(angle);
          const brightness = 0.15 + 0.85 * (1 - z / maxZ);
          const size = 0.5 + 3 * (1 - z / maxZ);

          // Trail behind the star (motion blur)
          const trailLen = 4 + 8 * (1 - z / maxZ);
          const tAngle = Math.atan2(py - cy, px - cx);
          ctx.beginPath();
          ctx.moveTo(px, py);
          ctx.lineTo(
            px - trailLen * Math.cos(tAngle),
            py - trailLen * Math.sin(tAngle)
          );

          const hueShift = (angle * 180 / Math.PI + time * 20) % 360;
          ctx.strokeStyle = `hsla(${210 + hueShift * 0.05}, 80%, ${60 + 30 * brightness}%, ${brightness * 0.6})`;
          ctx.lineWidth = size * 0.4;
          ctx.stroke();

          // Head glow
          const headGlow = ctx.createRadialGradient(px, py, 0, px, py, size * 2);
          headGlow.addColorStop(0, `hsla(210, 100%, 90%, ${brightness * 0.5})`);
          headGlow.addColorStop(1, 'transparent');
          ctx.fillStyle = headGlow;
          ctx.beginPath();
          ctx.arc(px, py, size * 2, 0, Math.PI * 2);
          ctx.fill();

          // Core
          ctx.beginPath();
          ctx.arc(px, py, size * 0.3, 0, Math.PI * 2);
          ctx.fillStyle = `hsla(210, 100%, 95%, ${brightness})`;
          ctx.fill();
        }

        // Additional fast warp streaks
        ctx.strokeStyle = `rgba(100, 160, 255, ${0.04 + 0.04 * Math.sin(time * 8)})`;
        ctx.lineWidth = 1;
        for (let i = 0; i < 20; i++) {
          const sx = Math.random() * canvas.width;
          const sy = Math.random() * canvas.height;
          const len = 60 + Math.random() * 150;
          const dx = sx - cx, dy = sy - cy;
          const dist = Math.sqrt(dx * dx + dy * dy) || 1;
          ctx.beginPath();
          ctx.moveTo(sx, sy);
          ctx.lineTo(sx + (dx / dist) * len, sy + (dy / dist) * len);
          ctx.stroke();
        }
      } else {
        // ---- Normal star field ----
        const cx = canvas.width / 2, cy = canvas.height * 0.7;

        // Perspective grid
        ctx.strokeStyle = 'rgba(51, 65, 85, 0.12)';
        ctx.lineWidth = 1;
        const gridSpeed = time * 60;
        for (let i = -6; i <= 6; i++) {
          ctx.beginPath();
          ctx.moveTo(cx + i * 120 - gridSpeed, cy);
          ctx.lineTo(cx + i * 300 - gridSpeed, cy - canvas.height);
          ctx.stroke();
        }
        for (let j = 1; j < 5; j++) {
          const yy = cy - j * canvas.height * 0.15;
          ctx.beginPath();
          ctx.moveTo(cx - j * 200 - gridSpeed, yy);
          ctx.lineTo(cx + j * 200 - gridSpeed, yy);
          ctx.stroke();
        }

        // Stars
        for (const s of stars) {
          const speedBoost = warpMode ? 1 : Math.min(3, Math.log10((speed || 1) + 1) / 2);
          s.x += (Math.random() - 0.5) * s.speed * 0.3 * speedBoost;
          s.y += s.speed * 0.2 * speedBoost;

          if (s.x > canvas.width + 10) s.x = -10;
          if (s.x < -10) s.x = canvas.width + 10;
          if (s.y > canvas.height + 10) s.y = -10;
          if (s.y < -10) s.y = canvas.height + 10;

          if (s.r > 1.5) {
            const glow = ctx.createRadialGradient(s.x, s.y, 0, s.x, s.y, s.r * 6);
            glow.addColorStop(0, `hsla(${s.hue}, 80%, 80%, ${s.a * 0.3})`);
            glow.addColorStop(1, 'transparent');
            ctx.fillStyle = glow;
            ctx.beginPath();
            ctx.arc(s.x, s.y, s.r * 6, 0, Math.PI * 2);
            ctx.fill();
          }

          ctx.beginPath();
          ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
          ctx.fillStyle = `hsla(${s.hue}, 60%, 85%, ${s.a})`;
          ctx.fill();
        }

        // Shooting stars (rare)
        if (Math.random() < 0.002) {
          const sx = Math.random() * canvas.width;
          const sy = Math.random() * canvas.height * 0.3;
          const slen = 60 + Math.random() * 80;
          ctx.strokeStyle = 'rgba(255, 255, 255, 0.4)';
          ctx.lineWidth = 1.5;
          ctx.beginPath();
          ctx.moveTo(sx, sy);
          ctx.lineTo(sx - slen, sy + slen * 0.3);
          ctx.stroke();
        }
      }

      // Glitch color bars
      if (glitchActive) {
        ctx.restore();
        ctx.save();
        for (let i = 0; i < 3; i++) {
          const gy = Math.random() * canvas.height;
          const gh = 2 + Math.random() * 6;
          ctx.fillStyle = `rgba(0, ${150 + Math.random() * 105}, 255, ${0.03 + Math.random() * 0.05})`;
          ctx.fillRect(0, gy, canvas.width, gh);
        }
      }

      ctx.restore();

      frame = requestAnimationFrame(animate);
    };
    animate();

    return () => {
      cancelAnimationFrame(frame);
      window.removeEventListener('resize', resize);
    };
  }, [warpMode]);

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 pointer-events-none z-0"
    />
  );
}

interface PhysicsReferenceProps {
  beta: number;
  gamma: number;
  speedKmh: number;
  dopplerFactor: number;
  timeDilationNs: number;
  gravDilationNs: number;
}

const C = 299_792_458;

const roundSig = (n: number, digits = 4) => {
  if (n === 0) return '0';
  if (Math.abs(n) < 0.0001) return n.toExponential(2);
  return n.toFixed(digits);
};

export function PhysicsReference({
  beta, gamma, speedKmh, dopplerFactor, timeDilationNs, gravDilationNs,
}: PhysicsReferenceProps) {
  const formulas = [
    {
      name: 'Lorentz Factor γ',
      expr: '1 / √(1 - β²)',
      val: `γ = 1 / √(1 - ${roundSig(beta)}²) = ${gamma.toFixed(6)}`,
    },
    {
      name: 'Time Dilation',
      expr: "Δt' = γ · Δt",
      val: `Δt' = ${gamma.toFixed(4)} · Δt → ${roundSig(timeDilationNs)} ns/s lost`,
    },
    {
      name: 'Length Contraction',
      expr: "L' = L / γ",
      val: `L' = L / ${gamma.toFixed(4)} = ${roundSig(1 / gamma)} × L`,
    },
    {
      name: 'Relativistic Doppler',
      expr: 'f₂ / f₁ = √((1+β)/(1-β))',
      val: `f₂/f₁ = √((1+${roundSig(beta)})/(1-${roundSig(beta)})) = ${dopplerFactor.toFixed(4)}`,
    },
    {
      name: 'Relativistic Mass',
      expr: 'm = γ · m₀',
      val: `m = ${gamma.toFixed(4)} · m₀`,
    },
    {
      name: 'Gravitational Dilation',
      expr: "Δt' = Δt · √(1 - 2GM/rc²)",
      val: `Δt' → ${roundSig(gravDilationNs)} ns/s (altitude-dependent)`,
    },
  ];

  return (
    <div className="card-accent" style={{ '--accent': '#818cf8' } as React.CSSProperties}>
      <div className="p-4 space-y-3">
        <div className="flex items-center gap-2" style={{ color: '#818cf8' }}>
          <span className="text-[8px]">∑</span>
          <span className="font-bold uppercase tracking-[0.2em] text-[10px]" style={{ color: '#818cf8' }}>Relativity Reference</span>
          <span className="text-[6px] font-mono text-slate-600 ml-auto">β = {roundSig(beta)}</span>
        </div>

        <div className="space-y-2">
          {formulas.map(f => (
            <div key={f.name} className="text-[8px] font-mono leading-relaxed">
              <span className="text-indigo-400">{f.name}</span>
              <br />
              <span className="text-slate-600">{f.expr}</span>
              <br />
              <span className="text-slate-400">{f.val}</span>
            </div>
          ))}
        </div>

        <div className="pt-2 border-t border-slate-800/50 text-[6px] font-mono text-slate-700 text-center">
          c = 299,792,458 m/s · Speed: {speedKmh.toFixed(1)} km/h
        </div>
      </div>
      <div className="absolute top-2 left-2 w-2.5 h-2.5 border-t border-l opacity-15" style={{ borderColor: '#818cf8' }} />
      <div className="absolute bottom-2 right-2 w-2.5 h-2.5 border-b border-r opacity-15" style={{ borderColor: '#818cf8' }} />
    </div>
  );
}


interface ProperTimeClockProps {
  gamma: number;
}

function ClockFace({ label, time, color, gamma }: { label: string; time: Date; color: string; gamma: number }) {
  const cx = 50, cy = 50, r = 42;
  const hours = time.getHours() % 12;
  const mins = time.getMinutes();
  const secs = time.getSeconds();

  const hAngle = (hours * 30 + mins * 0.5 - 90) * Math.PI / 180;
  const mAngle = (mins * 6 + secs * 0.1 - 90) * Math.PI / 180;
  const sAngle = (secs * 6 - 90) * Math.PI / 180;

  return (
    <div className="flex flex-col items-center">
      <svg width="90" height="102" viewBox="0 0 100 112">
        <circle cx={cx} cy={cy} r={r} fill="rgba(15,23,42,0.6)" stroke={color} strokeWidth="1.2" />
        {[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11].map((h) => {
          const a = (h * 30 - 90) * Math.PI / 180;
          const inner = h % 3 === 0 ? 32 : 36;
          return (
            <line
              key={h}
              x1={cx + inner * Math.cos(a)}
              y1={cy + inner * Math.sin(a)}
              x2={cx + r * 0.92 * Math.cos(a)}
              y2={cy + r * 0.92 * Math.sin(a)}
              stroke={h % 3 === 0 ? color : '#334155'}
              strokeWidth={h % 3 === 0 ? 2 : 0.8}
            />
          );
        })}
        <line x1={cx} y1={cy} x2={cx + 18 * Math.cos(hAngle)} y2={cy + 18 * Math.sin(hAngle)} stroke={color} strokeWidth="2.5" strokeLinecap="round" />
        <line x1={cx} y1={cy} x2={cx + 26 * Math.cos(mAngle)} y2={cy + 26 * Math.sin(mAngle)} stroke={color} strokeWidth="1.5" strokeLinecap="round" />
        <line x1={cx} y1={cy} x2={cx + 32 * Math.cos(sAngle)} y2={cy + 32 * Math.sin(sAngle)} stroke={gamma > 1.05 ? '#f472b6' : '#475569'} strokeWidth="0.8" strokeLinecap="round" />
        <circle cx={cx} cy={cy} r="2" fill={color} />
        <text x={cx} y={cy + r + 14} textAnchor="middle" fill="#64748b" fontSize="6.5" fontFamily="monospace" letterSpacing="0.2em">{label}</text>
      </svg>
    </div>
  );
}

export function ProperTimeClock({ gamma }: ProperTimeClockProps) {
  const [now, setNow] = useState(new Date());
  const properRef = useRef(0);
  const lastRealRef = useRef(Date.now());

  useEffect(() => {
    const tick = () => {
      const real = Date.now();
      const dt = (real - lastRealRef.current) / 1000;
      if (dt > 0 && dt < 2) {
        properRef.current += dt / gamma;
      }
      lastRealRef.current = real;
      setNow(new Date());
    };
    const id = setInterval(tick, 100);
    return () => clearInterval(id);
  }, [gamma]);

  const properMs = properRef.current * 1000;
  const properDate = new Date(now.getTime() - (Date.now() - lastRealRef.current) + properMs);

  return (
    <div className="card-accent p-5" style={{ '--accent': '#ec4899' } as React.CSSProperties}>
      <div className="flex items-center gap-2 mb-3">
        <span className="w-1.5 h-1.5 rounded-full bg-pink-500" />
        <h2 className="font-bold text-[10px] uppercase tracking-[0.2em] text-slate-400">Proper Time</h2>
      </div>
      <div className="flex justify-center gap-4">
        <ClockFace label="Coordinate" time={now} color="#3b82f6" gamma={1} />
        <ClockFace label={`γ=${gamma.toFixed(2)}`} time={properDate} color="#f472b6" gamma={gamma} />
      </div>
      <p className="text-[7px] text-slate-700 text-center mt-1.5 uppercase tracking-[0.2em]">
        {gamma > 1.02 ? 'Proper clock ticks slower' : 'No significant dilation'}
      </p>
    </div>
  );
}


interface RadarSweepProps {
  speed: number;
}

export function RadarSweep({ speed }: RadarSweepProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const W = 160, H = 160;
    canvas.width = W;
    canvas.height = H;
    const cx = W / 2, cy = H / 2, r = 68;

    let frame: number;
    let angle = 0;

    const blips: { a: number; d: number; life: number }[] = [];
    for (let i = 0; i < 4; i++) {
      blips.push({
        a: Math.random() * Math.PI * 2,
        d: 15 + Math.random() * (r - 20),
        life: 0.3 + Math.random() * 0.7,
      });
    }

    const animate = () => {
      const sweepSpeed = 0.015 * (1 + speed / 100);
      angle += sweepSpeed;
      ctx.clearRect(0, 0, W, H);

      // Outer ring
      ctx.beginPath();
      ctx.arc(cx, cy, r, 0, Math.PI * 2);
      ctx.strokeStyle = 'rgba(51, 65, 85, 0.6)';
      ctx.lineWidth = 1;
      ctx.stroke();

      // Inner rings
      for (let i = 1; i <= 3; i++) {
        ctx.beginPath();
        ctx.arc(cx, cy, r * i / 3, 0, Math.PI * 2);
        ctx.strokeStyle = 'rgba(51, 65, 85, 0.2)';
        ctx.lineWidth = 0.5;
        ctx.stroke();
      }

      // Crosshairs
      ctx.strokeStyle = 'rgba(51, 65, 85, 0.15)';
      ctx.lineWidth = 0.5;
      ctx.beginPath();
      ctx.moveTo(cx - r, cy);
      ctx.lineTo(cx + r, cy);
      ctx.moveTo(cx, cy - r);
      ctx.lineTo(cx, cy + r);
      ctx.stroke();

      // Sweep wedge
      ctx.beginPath();
      ctx.moveTo(cx, cy);
      ctx.arc(cx, cy, r, angle - 0.4, angle);
      ctx.closePath();
      const sweepGrad = ctx.createRadialGradient(cx, cy, 0, cx, cy, r);
      sweepGrad.addColorStop(0, 'rgba(100, 200, 255, 0.15)');
      sweepGrad.addColorStop(0.5, 'rgba(100, 200, 255, 0.05)');
      sweepGrad.addColorStop(1, 'transparent');
      ctx.fillStyle = sweepGrad;
      ctx.fill();

      // Sweep line
      ctx.beginPath();
      ctx.moveTo(cx, cy);
      ctx.lineTo(cx + r * Math.cos(angle), cy + r * Math.sin(angle));
      ctx.strokeStyle = 'rgba(100, 200, 255, 0.5)';
      ctx.lineWidth = 1;
      ctx.shadowColor = '#64c8ff';
      ctx.shadowBlur = 6;
      ctx.stroke();
      ctx.shadowBlur = 0;

      // Sweep head
      ctx.beginPath();
      ctx.arc(cx + r * Math.cos(angle), cy + r * Math.sin(angle), 3, 0, Math.PI * 2);
      ctx.fillStyle = 'rgba(100, 200, 255, 0.8)';
      ctx.shadowColor = '#64c8ff';
      ctx.shadowBlur = 10;
      ctx.fill();
      ctx.shadowBlur = 0;

      // Blips
      for (const b of blips) {
        b.a += 0.002;
        b.life -= 0.002;
        if (b.life <= 0) {
          b.a = Math.random() * Math.PI * 2;
          b.d = 15 + Math.random() * (r - 20);
          b.life = 0.5 + Math.random() * 1;
        }
        const bx = cx + b.d * Math.cos(b.a);
        const by = cy + b.d * Math.sin(b.a);
        const blink = 0.3 + 0.7 * (1 - Math.abs(b.life - 0.5) * 2);

        ctx.beginPath();
        ctx.arc(bx, by, 2, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(100, 255, 150, ${blink * 0.6})`;
        ctx.fill();

        // Blip glow
        ctx.beginPath();
        ctx.arc(bx, by, 5, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(100, 255, 150, ${blink * 0.1})`;
        ctx.fill();
      }

      // Center dot
      ctx.beginPath();
      ctx.arc(cx, cy, 2.5, 0, Math.PI * 2);
      ctx.fillStyle = 'rgba(100, 200, 255, 0.6)';
      ctx.fill();

      frame = requestAnimationFrame(animate);
    };
    animate();

    return () => cancelAnimationFrame(frame);
  }, [speed]);

  return (
    <div className="card p-2 flex items-center justify-center">
      <canvas
        ref={canvasRef}
        className="w-[160px] h-[160px]"
        style={{ background: 'transparent' }}
      />
    </div>
  );
}


interface Raindrop {
  x: number; y: number; len: number; speed: number; opacity: number;
}

interface RainOverlayProps {
  intensity?: number;
}

export function RainOverlay({ intensity = 0.15 }: RainOverlayProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resize();
    window.addEventListener('resize', resize);

    const drops: Raindrop[] = [];
    const count = Math.floor(intensity * 300);

    for (let i = 0; i < count; i++) {
      drops.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        len: 10 + Math.random() * 25,
        speed: 4 + Math.random() * 8,
        opacity: 0.05 + Math.random() * 0.12,
      });
    }

    let frame: number;
    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      for (const d of drops) {
        d.y += d.speed;
        d.x += 0.5;
        if (d.y > canvas.height + d.len) {
          d.y = -d.len;
          d.x = Math.random() * canvas.width;
        }
        if (d.x > canvas.width + 10) d.x = -10;

        ctx.beginPath();
        ctx.moveTo(d.x, d.y);
        ctx.lineTo(d.x + 0.5, d.y + d.len);
        ctx.strokeStyle = `rgba(150, 180, 255, ${d.opacity})`;
        ctx.lineWidth = 0.5;
        ctx.stroke();
      }

      // Mist layer at bottom
      const mistGrad = ctx.createLinearGradient(0, canvas.height * 0.85, 0, canvas.height);
      mistGrad.addColorStop(0, 'transparent');
      mistGrad.addColorStop(1, 'rgba(100, 140, 200, 0.03)');
      ctx.fillStyle = mistGrad;
      ctx.fillRect(0, canvas.height * 0.85, canvas.width, canvas.height * 0.15);

      frame = requestAnimationFrame(animate);
    };
    animate();

    return () => {
      cancelAnimationFrame(frame);
      window.removeEventListener('resize', resize);
    };
  }, [intensity]);

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 pointer-events-none z-[2]"
    />
  );
}


interface RecordsTrackerProps {
  metrics: Metrics | null;
}

interface Records {
  maxSpeed: number;
  maxGamma: number;
  maxDilation: number;
}

export function RecordsTracker({ metrics }: RecordsTrackerProps) {
  const [records, setRecords] = useState<Records>({ maxSpeed: 0, maxGamma: 0, maxDilation: 0 });

  useEffect(() => {
    if (!metrics) return;
    setRecords(prev => ({
      maxSpeed: Math.max(prev.maxSpeed, metrics.speed_kmh),
      maxGamma: Math.max(prev.maxGamma, metrics.gamma),
      maxDilation: Math.max(prev.maxDilation, metrics.time_dilation_ns),
    }));
  }, [metrics]);

  const rows: [string, number, string][] = [
    ['Top Speed', records.maxSpeed, 'km/h'],
    ['Peak γ', records.maxGamma, ''],
    ['Max Dilation', records.maxDilation, 'ns/s'],
  ];

  return (
    <div className="card p-3">
      <div className="flex items-center gap-2 mb-2">
        <span className="text-[8px]">🏆</span>
        <span className="font-bold text-[7px] uppercase tracking-[0.2em] text-slate-600">Session Records</span>
      </div>
      <div className="space-y-1">
        {rows.map(([label, val, unit]) => (
          <div key={label} className="flex justify-between items-center text-[8px] font-mono">
            <span className="text-slate-500">{label}</span>
            <span className="text-slate-300 tabular-nums">
              {val === 0 ? '--' : unit === 'ns/s' ? val.toFixed(2) : val >= 1e6 ? `${(val / 1e6).toFixed(2)}M` : val.toFixed(1)}
              {val > 0 && unit && <span className="text-slate-700 ml-0.5">{unit}</span>}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}


interface RoadInfoProps {
  lat: number;
  lon: number;
  speedMs: number;
}

interface RoadData {
  name: string;
  maxspeed: number | null;
  highway: string;
  surface: string;
  trafficSignals: number;
}

export function RoadInfo({ lat, lon, speedMs }: RoadInfoProps) {
  const [road, setRoad] = useState<RoadData | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    let cancelled = false;
    const query = `
      [out:json][timeout:5];
      way(around:30,${lat},${lon})["highway"];
      out body;
      node(around:100,${lat},${lon})["highway"="traffic_signals"];
      out count;
    `;
    fetch('https://overpass-api.de/api/interpreter', {
      method: 'POST',
      body: `data=${encodeURIComponent(query)}`,
    })
      .then(r => r.json())
      .then(data => {
        if (cancelled) return;
        const ways = data.elements?.filter((e: any) => e.type === 'way') || [];
        const signals = data.elements?.filter((e: any) => e.type === 'node') || [];
        if (ways.length > 0) {
          const w = ways[0];
          const maxspeed = w.tags?.maxspeed ? parseInt(w.tags.maxspeed, 10) : null;
          setRoad({
            name: w.tags?.name || w.tags?.ref || 'Unnamed road',
            maxspeed: maxspeed ? maxspeed * (1000 / 3600) : null,
            highway: w.tags?.highway || 'unknown',
            surface: w.tags?.surface || 'unknown',
            trafficSignals: signals.length,
          });
        } else {
          setRoad(null);
        }
      })
      .catch(() => { if (!cancelled) setError(true); });
    return () => { cancelled = true; };
  }, [lat, lon]);

  const speedKmh = speedMs * 3.6;
  const limitKmh = road?.maxspeed != null ? road.maxspeed * 3.6 : null;
  const congestion = limitKmh ? Math.min(1, speedKmh / limitKmh) : null;
  const congested = congestion != null && congestion > 0.8;

  if (!road && !error) return null;

  const highwayLabel: Record<string, string> = {
    motorway: 'Motorway', trunk: 'Trunk', primary: 'Primary',
    secondary: 'Secondary', tertiary: 'Tertiary', residential: 'Residential',
    service: 'Service', unclassified: 'Unclassified',
  };

  return (
    <div className="card-accent" style={{ '--accent': congested ? '#ef4444' : '#10b981' } as React.CSSProperties}>
      <div className="p-3 space-y-2">
        <div className="flex items-center gap-2">
          <span className="text-[8px]">⊞</span>
          <span className="font-bold uppercase tracking-[0.2em] text-[8px]" style={{ color: congested ? '#ef4444' : '#10b981' }}>
            Road Data
          </span>
          {congestion != null && (
            <span className={`text-[7px] font-mono ml-auto ${congested ? 'text-red-400' : 'text-emerald-400'}`}>
              {congested ? 'HEAVY' : 'CLEAR'}
            </span>
          )}
        </div>

        {error ? (
          <p className="text-[8px] text-slate-600 font-mono">Road data unavailable</p>
        ) : road ? (
          <>
            <div className="grid grid-cols-2 gap-x-3 gap-y-1 text-[8px] font-mono">
              <span className="text-slate-600">Road</span>
              <span className="text-slate-300 text-right truncate">{road.name}</span>
              <span className="text-slate-600">Type</span>
              <span className="text-slate-400 text-right">{highwayLabel[road.highway] || road.highway}</span>
              {limitKmh && (
                <>
                  <span className="text-slate-600">Speed Limit</span>
                  <span className={`text-right ${speedKmh > limitKmh ? 'text-red-400' : 'text-slate-300'}`}>
                    {limitKmh.toFixed(0)} km/h
                  </span>
                </>
              )}
              <span className="text-slate-600">Your Speed</span>
              <span className={`text-right ${speedKmh > (limitKmh || Infinity) ? 'text-red-400' : 'text-emerald-400'}`}>
                {speedKmh.toFixed(0)} km/h
              </span>
              {road.trafficSignals > 0 && (
                <>
                  <span className="text-slate-600">Signals</span>
                  <span className="text-yellow-400 text-right">{road.trafficSignals} ahead</span>
                </>
              )}
            </div>

            {congestion != null && (
              <div className="h-1 w-full rounded-full bg-slate-800 overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${congested ? 'bg-red-500' : 'bg-emerald-500'}`}
                  style={{ width: `${Math.min(100, congestion * 100)}%` }}
                />
              </div>
            )}
          </>
        ) : (
          <p className="text-[8px] text-slate-600 font-mono">No road data nearby</p>
        )}
      </div>
      <div className="absolute top-2 left-2 w-2 h-2 border-t border-l opacity-15" style={{ borderColor: congested ? '#ef4444' : '#10b981' }} />
    </div>
  );
}


export interface Settings {
  accentColor: string;
  speedUnit: 'kmh' | 'ms' | 'c';
  rainIntensity: number;
  cardParallax: boolean;
}

const DEFAULT: Settings = {
  accentColor: '#3b82f6',
  speedUnit: 'kmh',
  rainIntensity: 0.15,
  cardParallax: true,
};

const ACCENTS = [
  { label: 'Blue', value: '#3b82f6' },
  { label: 'Cyan', value: '#06b6d4' },
  { label: 'Green', value: '#10b981' },
  { label: 'Purple', value: '#a855f7' },
  { label: 'Orange', value: '#f97316' },
  { label: 'Red', value: '#ef4444' },
];

interface SettingsPanelProps {
  open: boolean;
  onClose: () => void;
  settings: Settings;
  onSettingsChange: (s: Settings) => void;
}

const STORAGE_KEY = 'chronos-settings';

export function loadSettings(): Settings {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) return { ...DEFAULT, ...JSON.parse(raw) };
  } catch {}
  return DEFAULT;
}

export function SettingsPanel({ open, onClose, settings, onSettingsChange }: SettingsPanelProps) {
  if (!open) return null;

  const update = useCallback((patch: Partial<Settings>) => {
    const next = { ...settings, ...patch };
    onSettingsChange(next);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
  }, [settings, onSettingsChange]);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center" onClick={onClose}>
      <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" />
      <div
        className="relative card p-6 max-w-sm w-full mx-4 space-y-5"
        onClick={e => e.stopPropagation()}
      >
        <div className="flex items-center justify-between">
          <h2 className="font-bold text-[10px] uppercase tracking-[0.2em] text-blue-400">Dashboard Settings</h2>
          <button onClick={onClose} className="text-[10px] text-slate-500 hover:text-slate-300 font-mono">✕</button>
        </div>

        <div className="space-y-4">
          <div>
            <p className="text-[8px] uppercase tracking-[0.2em] text-slate-600 mb-2">Accent Color</p>
            <div className="flex gap-2">
              {ACCENTS.map(a => (
                <button
                  key={a.value}
                  onClick={() => update({ accentColor: a.value })}
                  className={`w-7 h-7 rounded-full transition-all ${
                    settings.accentColor === a.value ? 'ring-2 ring-white scale-110' : 'opacity-50 hover:opacity-80'
                  }`}
                  style={{ background: a.value }}
                  title={a.label}
                />
              ))}
            </div>
          </div>

          <div>
            <p className="text-[8px] uppercase tracking-[0.2em] text-slate-600 mb-2">Speed Unit</p>
            <div className="flex gap-1">
              {(['kmh', 'ms', 'c'] as const).map(u => (
                <button
                  key={u}
                  onClick={() => update({ speedUnit: u })}
                  className={`flex-1 px-2 py-1.5 text-[9px] font-mono rounded border transition-all ${
                    settings.speedUnit === u
                      ? 'bg-blue-500/20 border-blue-500/40 text-blue-400'
                      : 'bg-white/5 border-white/10 text-slate-500 hover:text-slate-300'
                  }`}
                >
                  {u === 'kmh' ? 'km/h' : u === 'ms' ? 'm/s' : '% c'}
                </button>
              ))}
            </div>
          </div>

          <div>
            <div className="flex items-center justify-between mb-2">
              <p className="text-[8px] uppercase tracking-[0.2em] text-slate-600">Rain Effect</p>
              <span className="text-[8px] font-mono text-slate-500">{(settings.rainIntensity * 100).toFixed(0)}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="0.4"
              step="0.05"
              value={settings.rainIntensity}
              onChange={(e) => update({ rainIntensity: parseFloat(e.target.value) })}
              className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-blue-500"
            />
          </div>

          <div className="flex items-center justify-between">
            <p className="text-[8px] uppercase tracking-[0.2em] text-slate-600">Card Parallax</p>
            <input
              type="checkbox"
              checked={settings.cardParallax}
              onChange={(e) => update({ cardParallax: e.target.checked })}
              className="w-4 h-4 accent-blue-500"
            />
          </div>
        </div>
      </div>
    </div>
  );
}

interface ShortcutsModalProps {
  open: boolean;
  onClose: () => void;
}

const SHORTCUTS = [
  { key: '1', desc: 'Dashboard tab' },
  { key: '2', desc: 'Labs tab' },
  { key: 'W', desc: 'Toggle warp drive' },
  { key: 'B', desc: 'Toggle black hole mode' },
  { key: 'M', desc: 'Toggle manual override' },
  { key: 'A', desc: 'Toggle audio timeline' },
  { key: 'F', desc: 'Toggle full-screen' },
  { key: '?', desc: 'Toggle this panel' },
];

export function ShortcutsModal({ open, onClose }: ShortcutsModalProps) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center" onClick={onClose}>
      <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" />
      <div
        className="relative card p-6 max-w-sm w-full mx-4 space-y-4"
        onClick={e => e.stopPropagation()}
        style={{ '--accent': '#3b82f6' } as React.CSSProperties}
      >
        <div className="flex items-center justify-between">
          <h2 className="font-bold text-[10px] uppercase tracking-[0.2em] text-blue-400">Keyboard Shortcuts</h2>
          <button onClick={onClose} className="text-[10px] text-slate-500 hover:text-slate-300 font-mono">ESC</button>
        </div>
        <div className="space-y-1.5">
          {SHORTCUTS.map(s => (
            <div key={s.key} className="flex items-center gap-3 text-[10px] font-mono">
              <kbd className="px-2 py-0.5 bg-white/5 border border-white/10 rounded text-slate-300 min-w-[24px] text-center text-[9px]">
                {s.key}
              </kbd>
              <span className="text-slate-500">{s.desc}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export function SkeletonCard({ className = '' }: { className?: string }) {
  return (
    <div className={`card p-5 animate-pulse ${className}`}>
      <div className="flex items-center gap-2 mb-4">
        <div className="w-4 h-4 rounded bg-slate-800" />
        <div className="h-2.5 w-24 rounded bg-slate-800" />
      </div>
      <div className="h-6 w-32 rounded bg-slate-800 mb-2" />
      <div className="h-2 w-full rounded bg-slate-800/50" />
    </div>
  );
}

export function SkeletonRow({ count = 4 }: { count?: number }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
      {Array.from({ length: count }).map((_, i) => (
        <SkeletonCard key={i} />
      ))}
    </div>
  );
}

interface SpeedContextProps {
  speedKmh: number;
  beta: number;
  gamma: number;
}

const REFERENCES = [
  { speed: 5, label: 'Walking speed', unit: 'km/h' },
  { speed: 100, label: 'Car on highway', unit: 'km/h' },
  { speed: 900, label: 'Commercial jet', unit: 'km/h' },
  { speed: 28000, label: 'ISS orbit', unit: 'km/h' },
  { speed: 40000, label: 'Earth orbit escape', unit: 'km/h' },
  { speed: 58000, label: 'Voyager 1', unit: 'km/h' },
  { speed: 700000, label: 'Solar orbital', unit: 'km/h' },
  { speed: 1_079_252_849, label: 'Speed of light', unit: 'km/h' },
];

export function SpeedContext({ speedKmh, beta, gamma }: SpeedContextProps) {
  if (speedKmh < 1) return null;

  // Find closest reference
  let closest = REFERENCES[0];
  let closestRatio = 1;
  for (const ref of REFERENCES) {
    const ratio = speedKmh / ref.speed;
    if (ratio >= 0.8 && ratio < closestRatio) {
      closest = ref;
      closestRatio = ratio;
    }
  }

  // Build context string
  const parts: string[] = [];

  if (beta > 0.01) {
    parts.push(`${(beta * 100).toFixed(1)}% of c`);
  }

  if (closestRatio >= 0.8 && closestRatio < 3) {
    parts.push(`${closestRatio.toFixed(1)}× ${closest.label}`);
  } else if (speedKmh > 1000) {
    const ref = REFERENCES.filter(r => r.speed < speedKmh).pop() || REFERENCES[0];
    const ratio = speedKmh / ref.speed;
    parts.push(`${ratio.toFixed(0)}× ${ref.label}`);
  }

  if (gamma > 1.01) {
    parts.push(`γ = ${gamma.toFixed(3)}`);
  }

  return (
    <div className="flex flex-wrap gap-x-3 gap-y-0.5 text-[8px] text-slate-600 font-mono mt-1 justify-center">
      {parts.map((p, i) => (
        <span key={i} className="text-blue-400/60">{p}</span>
      ))}
    </div>
  );
}

interface SpeedGaugeProps {
  speedKmh: number;
  maxSpeed: number;
  label: string;
  color?: string;
}

export function SpeedGauge({ speedKmh, maxSpeed, label, color = "#3b82f6" }: SpeedGaugeProps) {
  const fraction = Math.min(speedKmh / maxSpeed, 1);
  const angle = -120 + fraction * 240;
  const rad = (angle * Math.PI) / 180;
  const cx = 80, cy = 80, r = 60;

  const x = cx + r * Math.cos(rad - Math.PI / 2);
  const y = cy + r * Math.sin(rad - Math.PI / 2);

  const endX = cx + (r - 4) * Math.cos((240 * fraction - 120) * Math.PI / 180);
  const endY = cy + (r - 4) * Math.sin((240 * fraction - 120) * Math.PI / 180);

  const largeArc = fraction > 0.5 ? 1 : 0;

  return (
    <div className="flex flex-col items-center">
      <svg width="160" height="130" viewBox="0 0 160 140">
        {/* Background arc */}
        <path
          d={`M ${cx - r * Math.cos(Math.PI / 6)} ${cy - r * Math.sin(Math.PI / 6)}
              A ${r} ${r} 0 0 1 ${cx + r * Math.cos(Math.PI / 6)} ${cy - r * Math.sin(Math.PI / 6)}`}
          fill="none"
          stroke="#1e293b"
          strokeWidth="10"
          strokeLinecap="round"
        />
        {/* Colored arc */}
        <path
          d={`M ${cx - r * Math.cos(Math.PI / 6)} ${cy - r * Math.sin(Math.PI / 6)}
              A ${r} ${r} 0 ${largeArc} 1 ${endX} ${endY}`}
          fill="none"
          stroke={color}
          strokeWidth="10"
          strokeLinecap="round"
          className="transition-all duration-500"
        />
        {/* Tick marks */}
        {[0, 0.25, 0.5, 0.75, 1].map((f) => {
          const a = (-120 + f * 240) * Math.PI / 180;
          const x1 = cx + (r - 4) * Math.cos(a - Math.PI / 2);
          const y1 = cy + (r - 4) * Math.sin(a - Math.PI / 2);
          const x2 = cx + (r - 12) * Math.cos(a - Math.PI / 2);
          const y2 = cy + (r - 12) * Math.sin(a - Math.PI / 2);
          return <line key={f} x1={x1} y1={y1} x2={x2} y2={y2} stroke="#475569" strokeWidth="2" />;
        })}
        {/* Needle */}
        <line x1={cx} y1={cy} x2={x} y2={y} stroke={color} strokeWidth="2.5" strokeLinecap="round"
              className="transition-all duration-500" />
        <circle cx={cx} cy={cy} r="4" fill={color} />
        {/* Speed text */}
        <text x={cx} y={cy + 24} textAnchor="middle" fill="white" fontSize="20" fontFamily="monospace" fontWeight="bold">
          {speedKmh.toFixed(0)}
        </text>
        <text x={cx} y={cy + 38} textAnchor="middle" fill="#64748b" fontSize="9" fontFamily="monospace" fontWeight="bold">
          km/h
        </text>
      </svg>
      <span className="text-[10px] uppercase tracking-widest text-slate-500 -mt-1">{label}</span>
    </div>
  );
}


interface SystemBarProps {
  connected: boolean;
  speed: number;
  metrics: any;
}

export function SystemBar({ connected, speed, metrics }: SystemBarProps) {
  const [latency, setLatency] = useState<number | null>(null);
  const [dataAge, setDataAge] = useState(0);
  const lastTimestamp = useRef(Date.now());

  useEffect(() => {
    const id = setInterval(() => {
      if (connected) {
        const start = performance.now();
        fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/labs/status`)
          .then(r => r.ok && setLatency(Math.round(performance.now() - start)))
          .catch(() => setLatency(null));
      }
    }, 5000);
    return () => clearInterval(id);
  }, [connected]);

  useEffect(() => {
    if (metrics?.timestamp) lastTimestamp.current = metrics.timestamp;
    const id = setInterval(() => {
      setDataAge(Math.round((Date.now() - lastTimestamp.current) / 1000));
    }, 1000);
    return () => clearInterval(id);
  }, [metrics]);

  useEffect(() => {
    lastTimestamp.current = Date.now();
  }, [metrics]);

  return (
    <div className="fixed bottom-0 left-0 right-0 z-50">
      <div className="h-6 px-5 flex items-center justify-between text-[8px] font-mono tracking-wider"
        style={{
          background: 'rgba(15,23,42,0.85)',
          backdropFilter: 'blur(12px)',
          WebkitBackdropFilter: 'blur(12px)',
          borderTop: '1px solid rgba(51,65,85,0.3)',
        }}
      >
        <div className="flex items-center gap-4">
          <span className="flex items-center gap-1.5">
            <span className={`w-1.5 h-1.5 rounded-full ${connected ? 'bg-emerald-500' : 'bg-red-500'}`}
                  style={{ boxShadow: connected ? '0 0 6px rgba(16,185,129,0.6)' : 'none' }} />
            <span className="text-slate-600">{connected ? 'LINK ESTABLISHED' : 'NO LINK'}</span>
          </span>
          {latency !== null && <span className="text-slate-600">{latency}ms</span>}
          <span className="text-slate-700">|</span>
          <span className="text-slate-600">DATA: {dataAge}s ago</span>
          <span className="text-slate-700">|</span>
          <span className="text-slate-600">
            {speed > 0 ? `${(speed * 3.6).toFixed(0)} km/h` : 'STATIONARY'}
          </span>
        </div>
        <div className="flex items-center gap-3 text-slate-700">
          <span>CHRONOS-X v1.0</span>
          <span className="hidden sm:inline">[1]DASH [2]LABS [W]WARP [B]BH [M]MANUAL [A]AUDIO</span>
        </div>
      </div>
    </div>
  );
}


export function TesseractVisual() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const W = 200, H = 200;
    canvas.width = W;
    canvas.height = H;
    const cx = W / 2, cy = H / 2;

    const project4D = (x: number, y: number, z: number, w: number, angle: number) => {
      const cosA = Math.cos(angle), sinA = Math.sin(angle);
      const x1 = x * cosA - w * sinA;
      const w1 = x * sinA + w * cosA;
      const z1 = z * cosA - w1 * sinA;
      const w2 = z * sinA + w1 * cosA;
      const scale = 40;
      const perspective = 2.5;
      const dist = perspective + w2 * 0.1;
      return {
        sx: cx + (x1 * scale) / dist,
        sy: cy + (y * scale * Math.cos(angle * 0.7) - z1 * scale * Math.sin(angle * 0.7)) / dist,
      };
    };

    const vertices = [
      [-1, -1, -1, -1], [1, -1, -1, -1], [1, 1, -1, -1], [-1, 1, -1, -1],
      [-1, -1, 1, -1], [1, -1, 1, -1], [1, 1, 1, -1], [-1, 1, 1, -1],
      [-1, -1, -1, 1], [1, -1, -1, 1], [1, 1, -1, 1], [-1, 1, -1, 1],
      [-1, -1, 1, 1], [1, -1, 1, 1], [1, 1, 1, 1], [-1, 1, 1, 1],
    ];

    const edges = [
      [0,1],[1,2],[2,3],[3,0],[4,5],[5,6],[6,7],[7,4],
      [0,4],[1,5],[2,6],[3,7],[8,9],[9,10],[10,11],[11,8],
      [12,13],[13,14],[14,15],[15,12],[8,12],[9,13],[10,14],[11,15],
      [0,8],[1,9],[2,10],[3,11],[4,12],[5,13],[6,14],[7,15],
    ];

    let frame: number;
    let angle = 0;

    const animate = () => {
      angle += 0.008;
      ctx.clearRect(0, 0, W, H);

      // Center glow
      const glow = ctx.createRadialGradient(cx, cy, 0, cx, cy, 40);
      glow.addColorStop(0, 'rgba(100, 150, 255, 0.05)');
      glow.addColorStop(1, 'transparent');
      ctx.fillStyle = glow;
      ctx.beginPath();
      ctx.arc(cx, cy, 40, 0, Math.PI * 2);
      ctx.fill();

      const projected = vertices.map(v => project4D(v[0], v[1], v[2], v[3], angle));

      for (const [i, j] of edges) {
        const p1 = projected[i], p2 = projected[j];
        const dist = Math.sqrt((p1.sx - p2.sx) ** 2 + (p1.sy - p2.sy) ** 2);
        const alpha = Math.min(0.6, Math.max(0.05, (dist / 80)));
        ctx.beginPath();
        ctx.moveTo(p1.sx, p1.sy);
        ctx.lineTo(p2.sx, p2.sy);
        ctx.strokeStyle = `rgba(100, 180, 255, ${alpha})`;
        ctx.lineWidth = 0.8;
        ctx.stroke();
      }

      // Vertex dots
      for (const p of projected) {
        ctx.beginPath();
        ctx.arc(p.sx, p.sy, 1.5, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(150, 200, 255, 0.6)';
        ctx.fill();
      }

      frame = requestAnimationFrame(animate);
    };
    animate();
    return () => cancelAnimationFrame(frame);
  }, []);

  return (
    <div className="card p-2 flex items-center justify-center">
      <canvas
        ref={canvasRef}
        className="w-[200px] h-[200px]"
        style={{ background: 'transparent' }}
      />
    </div>
  );
}


interface Toast {
  id: number;
  message: string;
  type: 'info' | 'warn' | 'event';
}

interface ToastCtx {
  toast: (message: string, type?: Toast['type']) => void;
}

const Ctx = createContext<ToastCtx>({ toast: () => {} });

export const useToast = () => useContext(Ctx);

let nextId = 0;

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const toast = useCallback((message: string, type: Toast['type'] = 'info') => {
    const id = nextId++;
    setToasts(prev => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id));
    }, 3000);
  }, []);

  const dismiss = (id: number) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  };

  return (
    <Ctx.Provider value={{ toast }}>
      {children}
      <div className="fixed bottom-10 right-4 z-50 flex flex-col gap-2 items-end pointer-events-none">
        {toasts.map(t => (
          <div
            key={t.id}
            onClick={() => dismiss(t.id)}
            className={`
              pointer-events-auto cursor-pointer
              px-4 py-2 rounded-lg backdrop-blur-xl border text-[10px] font-mono
              animate-[fade-slide-up_0.3s_ease-out]
              transition-all hover:scale-105
              ${t.type === 'warn'
                ? 'bg-red-900/40 border-red-500/30 text-red-200'
                : t.type === 'event'
                ? 'bg-emerald-900/40 border-emerald-500/30 text-emerald-200'
                : 'bg-blue-900/40 border-blue-500/30 text-blue-200'
              }
            `}
          >
            <span className="mr-2">
              {t.type === 'warn' ? '⚠' : t.type === 'event' ? '◆' : '▸'}
            </span>
            {t.message}
          </div>
        ))}
      </div>
    </Ctx.Provider>
  );
}


interface TripComputerProps {
  speedMs: number;
  gamma: number;
  destPos: { lat: number; lon: number; label: string } | null;
  userPos: { lat: number; lon: number } | null;
}

function haversine(lat1: number, lon1: number, lat2: number, lon2: number) {
  const R = 6371000;
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const a = Math.sin(dLat / 2) ** 2 +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
    Math.sin(dLon / 2) ** 2;
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

export function TripComputer({ speedMs, gamma, destPos, userPos }: TripComputerProps) {
  const [elapsed, setElapsed] = useState(0);
  const [distTraveled, setDistTraveled] = useState(0);
  const startRef = useRef(Date.now());
  const lastPosRef = useRef<{ lat: number; lon: number } | null>(null);

  useEffect(() => {
    startRef.current = Date.now();
    setElapsed(0);
    setDistTraveled(0);
  }, [speedMs]);

  useEffect(() => {
    if (!userPos) return;
    if (lastPosRef.current) {
      const d = haversine(lastPosRef.current.lat, lastPosRef.current.lon, userPos.lat, userPos.lon);
      if (d < 1000) setDistTraveled(prev => prev + d);
    }
    lastPosRef.current = userPos;
  }, [userPos]);

  useEffect(() => {
    const interval = setInterval(() => {
      setElapsed((Date.now() - startRef.current) / 1000);
    }, 200);
    return () => clearInterval(interval);
  }, []);

  const distToDest = destPos && userPos
    ? haversine(userPos.lat, userPos.lon, destPos.lat, destPos.lon)
    : null;

  const eta = (distToDest != null && speedMs > 0.1)
    ? distToDest / speedMs
    : null;

  const properElapsed = elapsed / Math.max(gamma, 1);

  const fmt = (s: number) => {
    if (s < 60) return `${s.toFixed(1)}s`;
    if (s < 3600) return `${Math.floor(s / 60)}m ${Math.floor(s % 60)}s`;
    return `${Math.floor(s / 3600)}h ${Math.floor((s % 3600) / 60)}m`;
  };

  const fmtDist = (m: number) => {
    if (m < 1000) return `${m.toFixed(0)}m`;
    if (m < 1e5) return `${(m / 1000).toFixed(2)}km`;
    return `${(m / 1000).toFixed(0)}km`;
  };

  return (
    <div className="card-accent" style={{ '--accent': '#10b981' } as React.CSSProperties}>
      <div className="p-4 space-y-3">
        <div className="flex items-center gap-2" style={{ color: '#10b981' }}>
          <span className="text-[8px]">⊞</span>
          <span className="font-bold uppercase tracking-[0.2em] text-[10px]" style={{ color: '#10b981' }}>Trip Computer</span>
        </div>

        <div className="grid grid-cols-2 gap-x-4 gap-y-2 text-[10px] font-mono">
          <span className="text-slate-600">Journey</span>
          <span className="text-slate-300 text-right">{fmt(elapsed)}</span>

          <span className="text-slate-600">Proper</span>
          <span className="text-emerald-400 text-right">{fmt(properElapsed)}</span>

          <span className="text-slate-600">Traveled</span>
          <span className="text-slate-300 text-right">{fmtDist(distTraveled)}</span>

          {destPos && (
            <>
              <span className="text-slate-600">Remaining</span>
              <span className="text-slate-300 text-right">{distToDest != null ? fmtDist(distToDest) : '--'}</span>

              <span className="text-slate-600">ETA</span>
              <span className="text-blue-400 text-right">{eta != null ? fmt(eta) : '--'}</span>

              <span className="text-slate-600">Destination</span>
              <span className="text-slate-400 text-right truncate max-w-[100px]">{destPos.label}</span>
            </>
          )}
        </div>
      </div>
      <div className="absolute top-2 left-2 w-2.5 h-2.5 border-t border-l opacity-15" style={{ borderColor: '#10b981' }} />
      <div className="absolute bottom-2 right-2 w-2.5 h-2.5 border-b border-r opacity-15" style={{ borderColor: '#10b981' }} />
    </div>
  );
}


interface WarpJumpAnimationProps {
  active: boolean;
  onComplete: () => void;
}

export function WarpJumpAnimation({ active, onComplete }: WarpJumpAnimationProps) {
  const [phase, setPhase] = useState<'idle' | 'countdown' | 'flash' | 'tunnel'>('idle');
  const [count, setCount] = useState(3);

  useEffect(() => {
    if (!active) {
      setPhase('idle');
      setCount(3);
      return;
    }

    setPhase('countdown');
    setCount(3);

    const t1 = setTimeout(() => setCount(2), 600);
    const t2 = setTimeout(() => setCount(1), 1200);
    const t3 = setTimeout(() => {
      setPhase('flash');
      setCount(0);
    }, 1800);
    const t4 = setTimeout(() => {
      setPhase('tunnel');
    }, 2100);
    const t5 = setTimeout(() => {
      onComplete();
    }, 2800);

    return () => {
      clearTimeout(t1); clearTimeout(t2); clearTimeout(t3);
      clearTimeout(t4); clearTimeout(t5);
    };
  }, [active, onComplete]);

  if (phase === 'idle') return null;

  return (
    <div className="fixed inset-0 z-[60] pointer-events-none flex items-center justify-center">
      {/* Countdown */}
      {phase === 'countdown' && count > 0 && (
        <div className="text-center">
          <p className="text-[200px] font-bold font-mono text-blue-400 animate-pulse"
             style={{ textShadow: '0 0 60px rgba(59,130,246,0.6), 0 0 120px rgba(59,130,246,0.3)' }}>
            {count}
          </p>
          <p className="text-[10px] uppercase tracking-[0.5em] text-blue-500/60 -mt-8">
            to warp
          </p>
        </div>
      )}

      {/* White flash */}
      {phase === 'flash' && (
        <div className="absolute inset-0 bg-white animate-[fade_0.6s_ease-out]" style={{ animation: 'fade 0.6s ease-out' }} />
      )}

      {/* Tunnel stretch */}
      {phase === 'tunnel' && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-32 h-32 border-2 border-blue-400 rounded-full animate-ping opacity-30" />
          <div className="absolute w-16 h-16 border border-cyan-300 rounded-full animate-ping opacity-50" style={{ animationDelay: '0.15s' }} />
          <div className="absolute w-8 h-8 border border-blue-200 rounded-full animate-ping opacity-70" style={{ animationDelay: '0.3s' }} />
        </div>
      )}

      <style>{`
        @keyframes fade {
          0% { opacity: 1; }
          100% { opacity: 0; }
        }
      `}</style>
    </div>
  );
}

