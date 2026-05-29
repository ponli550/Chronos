import { useState, useEffect, useRef, useCallback, lazy, Suspense } from 'react';
import type { Metrics, Position, DestPosition } from './types';
import {
  Header, ErrorBanner, EnergeticsPanel, MetricCards, MinkowskiDiagram,
  SpeedGauge, DopplerShiftPreview, ProperTimeClock, LengthContractionBar,
  LogbookPanel, SystemBar, SkeletonRow, BlackHoleVisual, AudioVisualizer,
  TripComputer, GlitchOverlay, CurvatureVisual, RadarSweep,
  ToastProvider, useToast, MetricHistory, ShortcutsModal, TesseractVisual,
  AuroraBackground, DualClock, SpeedContext, ParallaxCard, RainOverlay,
  MouseGlow, SettingsPanel, loadSettings, WarpJumpAnimation,
  PhysicsReference, CompassIndicator, DataAgeIndicator, FpsMonitor,
  AboutPanel, EnvironmentData, RoadInfo, JourneyTimeline, RecordsTracker,
  DestinationSearch, DeviceStatus, ParticleBackground,
} from './components';
import type { Settings, TimelineEvent } from './components';
import { useRoute, useKeyboard } from './hooks';

const LOG_KEY = 'chronos-logbook';
const HISTORY_KEY = 'chronos-history';

const MapSection = lazy(() => import('./components').then(m => ({ default: m.MapSection })));
const LabsPage = lazy(() => import('./components').then(m => ({ default: m.LabsPage })));

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const VEHICLES = [
  { id: 'car',    label: 'Car',     maxKmh: 200,   color: '#3b82f6' },
  { id: 'jet',    label: 'Jet',     maxKmh: 3000,  color: '#f59e0b' },
  { id: 'rocket', label: 'Rocket',  maxKmh: 30000, color: '#ef4444' },
  { id: 'warp',   label: 'Warp',    maxKmh: 1e9,   color: '#a855f7' },
];

const haversine = (lat1: number, lon1: number, lat2: number, lon2: number) => {
  const R = 6371000;
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const a = Math.sin(dLat / 2) ** 2 +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
    Math.sin(dLon / 2) ** 2;
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
};

const computeBearing = (lat1: number, lon1: number, lat2: number, lon2: number) => {
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const y = Math.sin(dLon) * Math.cos(lat2 * Math.PI / 180);
  const x = Math.cos(lat1 * Math.PI / 180) * Math.sin(lat2 * Math.PI / 180) -
    Math.sin(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * Math.cos(dLon);
  return (Math.atan2(y, x) * 180 / Math.PI + 360) % 360;
};

const hexToRgb = (hex: string) => {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `${r}, ${g}, ${b}`;
};

function DashboardInner() {
  const [tab, setTab] = useState<'dashboard' | 'labs'>('dashboard');
  const [speed, setSpeed] = useState(0);
  const [userPos, setUserPos] = useState<Position | null>(null);
  const [destPos, setDestPos] = useState<DestPosition | null>(null);
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [warpMode, setWarpMode] = useState(false);
  const [manualOverride, setManualOverride] = useState(false);
  const [bhMode, setBhMode] = useState(false);
  const [bhProx, setBhProx] = useState(1.0);
  const [cumulativeDilation, setCumulativeDilation] = useState(0);
  const [bearing, setBearing] = useState(0);
  const [activeVehicle, setActiveVehicle] = useState('car');
  const [speedLimitKmh, setSpeedLimitKmh] = useState(200);
  const [logbook, setLogbook] = useState<any[]>(() => {
    try { return JSON.parse(localStorage.getItem(LOG_KEY) || '[]'); } catch { return []; }
  });
  const [audioEnabled, setAudioEnabled] = useState(false);
  const [metricHistory, setMetricHistory] = useState<{ gamma: number; speed: number; dilation: number }[]>(() => {
    try { return JSON.parse(localStorage.getItem(HISTORY_KEY) || '[]'); } catch { return []; }
  });
  const [showShortcuts, setShowShortcuts] = useState(false);
  const [fullscreen, setFullscreen] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [settings, setSettings] = useState<Settings>(loadSettings);
  const [realMode, setRealMode] = useState(false);
  const [boost, setBoost] = useState(1);
  const [gpsSpeed, setGpsSpeed] = useState(0);
  const [warpJumpActive, setWarpJumpActive] = useState(false);
  const [showAbout, setShowAbout] = useState(false);
  const [tabTransition, setTabTransition] = useState<'enter' | 'exit' | null>(null);
  const [timelineEvents, setTimelineEvents] = useState<TimelineEvent[]>([]);
  const [timelineCollapsed, setTimelineCollapsed] = useState(true);
  const [alertThresholds] = useState({ maxSpeed: 1e9, maxGamma: 100 });
  const sessionStart = useRef(Date.now());
  const [totalDistance, setTotalDistance] = useState(0);
  const [tripStarted, setTripStarted] = useState(false);
  const [speechEnabled, setSpeechEnabled] = useState(false);
  const [laps, setLaps] = useState<{ time: number; label: string }[]>([]);
  const wakeLockRef = useRef<any>(null);
  const { route } = useRoute(userPos, destPos);

  const prevPosRef = useRef<{ lat: number; lon: number; time: number } | null>(null);
  const lastUpdateRef = useRef<number>(Date.now());
  const [connected, setConnected] = useState(false);
  const [dataVersion, setDataVersion] = useState(0);
  const { toast } = useToast();

  // Persist logbook + history across sessions
  useEffect(() => { localStorage.setItem(LOG_KEY, JSON.stringify(logbook.slice(-200))); }, [logbook]);
  useEffect(() => { localStorage.setItem(HISTORY_KEY, JSON.stringify(metricHistory.slice(-200))); }, [metricHistory]);

  // Geolocation tracking
  useEffect(() => {
    if (!('geolocation' in navigator)) {
      setError('Geolocation not supported.');
      return;
    }

    const watchId = navigator.geolocation.watchPosition(
      (pos) => {
        const { latitude: lat, longitude: lon, altitude, accuracy, speed: gpsRawSpeed } = pos.coords;
        const alt = altitude || 0;
        setUserPos({ lat, lon, alt, acc: accuracy || 10 });

        // Track total distance from GPS
        if (prevPosRef.current) {
          const segDist = haversine(prevPosRef.current.lat, prevPosRef.current.lon, lat, lon);
          if (segDist < 500) {
            setTotalDistance(prev => prev + segDist);
          }
        }
        if (gpsRawSpeed && gpsRawSpeed > 0.5) setTripStarted(true);

        if (!warpMode && !manualOverride && !realMode) {
          let currentSpeed = pos.coords.speed;
          if (currentSpeed === null || currentSpeed === 0) {
            if (prevPosRef.current) {
              const dist = haversine(prevPosRef.current.lat, prevPosRef.current.lon, lat, lon);
              const dt = (pos.timestamp - prevPosRef.current.time) / 1000;
              if (dt > 0 && dist / dt < 100) {
                currentSpeed = dist / dt;
              }
            }
          }
          const raw = currentSpeed || 0;
          setGpsSpeed(raw);
          setSpeed(raw);
        } else if (realMode) {
          // In real mode, always track GPS speed
          let currentSpeed = pos.coords.speed;
          if (currentSpeed === null || currentSpeed === 0) {
            if (prevPosRef.current) {
              const dist = haversine(prevPosRef.current.lat, prevPosRef.current.lon, lat, lon);
              const dt = (pos.timestamp - prevPosRef.current.time) / 1000;
              if (dt > 0 && dist / dt < 100) {
                currentSpeed = dist / dt;
              }
            }
          }
          const raw = currentSpeed || 0;
          setGpsSpeed(raw);
          setSpeed(raw * boost);
        }

        if (prevPosRef.current) {
          setBearing(computeBearing(prevPosRef.current.lat, prevPosRef.current.lon, lat, lon));
        }
        prevPosRef.current = { lat, lon, time: pos.timestamp };
      },
      (err) => setError(`GPS Error: ${err.message}`),
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 },
    );

    return () => navigator.geolocation.clearWatch(watchId);
  }, [warpMode, manualOverride, realMode, boost]);

  // API polling
  useEffect(() => {
    const fetchData = async () => {
      try {
        let url = `${API_URL}/compute?speed=${speed}&bh=${bhMode}&prox=${bhProx}`;
        if (userPos) url += `&ulat=${userPos.lat}&ulon=${userPos.lon}&alt=${userPos.alt}`;
        if (destPos) url += `&dlat=${destPos.lat}&dlon=${destPos.lon}`;

        const res = await fetch(url);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        setMetrics(data);
        setConnected(true);
        setDataVersion(v => v + 1);
        if (speed > 1) {
          setLogbook(prev => [...prev, { ...data, timestamp: Date.now() }].slice(-100));
          setMetricHistory(prev => [...prev, { gamma: data.gamma, speed: data.speed_kmh, dilation: data.time_dilation_ns }].slice(-60));
        }
      } catch (err) {
        console.error('Backend unreachable', err);
      }
    };

    const interval = setInterval(fetchData, 500);
    return () => clearInterval(interval);
  }, [speed, userPos, destPos, bhMode, bhProx]);

  // Cumulative time dilation
  useEffect(() => {
    if (!metrics) return;
    const now = Date.now();
    const dt = (now - lastUpdateRef.current) / 1000;
    if (dt > 0 && dt < 2) {
      setCumulativeDilation(prev => prev + metrics.time_dilation_ns * dt);
    }
    lastUpdateRef.current = now;
  }, [metrics]);

  // Auditory time dilation effect (reuses AudioContext)
  const audioCtxRef = useRef<AudioContext | null>(null);
  useEffect(() => {
    if (audioEnabled && !audioCtxRef.current) {
      audioCtxRef.current = new (window.AudioContext || (window as any).webkitAudioContext)();
    }
    if (!audioEnabled && audioCtxRef.current) {
      audioCtxRef.current.close();
      audioCtxRef.current = null;
    }
  }, [audioEnabled]);

  useEffect(() => {
    if (!audioEnabled || !metrics || !audioCtxRef.current) return;
    const ctx = audioCtxRef.current;
    const playTick = () => {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.frequency.setValueAtTime(880, ctx.currentTime);
      gain.gain.setValueAtTime(0.1, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.05);
      osc.start();
      osc.stop(ctx.currentTime + 0.05);
    };
    const interval = setInterval(playTick, 1000 * metrics.gamma);
    return () => clearInterval(interval);
  }, [audioEnabled, metrics]);

  // Timeline helper — must be defined before any useCallback that references it
  const pushEvent = useCallback((type: TimelineEvent['type'], label: string, value?: string) => {
    setTimelineEvents(prev => [...prev, { time: Date.now(), type, label, value }]);
  }, []);

  // Speech announcements
  const announce = useCallback((text: string) => {
    if (!speechEnabled) return;
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 1.2;
      utterance.pitch = 0.9;
      utterance.volume = 0.5;
      window.speechSynthesis.speak(utterance);
    }
  }, [speechEnabled]);

  // Wake lock
  useEffect(() => {
    const acquire = async () => {
      try {
        if ('wakeLock' in navigator && tripStarted) {
          wakeLockRef.current = await (navigator as any).wakeLock.request('screen');
        }
      } catch {}
    };
    const release = () => {
      if (wakeLockRef.current) { wakeLockRef.current.release(); wakeLockRef.current = null; }
    };
    if (tripStarted) acquire();
    else release();
    return release;
  }, [tripStarted]);

  const handlePinDestination = useCallback((pos: DestPosition) => {
    setDestPos(pos);
    toast(`Destination pinned: ${pos.label}`, 'event');
    pushEvent('dest', `Destination: ${pos.label}`, `${pos.lat.toFixed(4)}, ${pos.lon.toFixed(4)}`);
  }, [toast, pushEvent]);

  const handleToggleWarp = useCallback(() => {
    if (warpMode) {
      setWarpMode(false);
      setSpeed(0);
      toast('Warp disengaged', 'event');
      pushEvent('warp', 'Warp disengaged', '');
      announce('Warp disengaged');
    } else {
      setWarpJumpActive(true);
    }
  }, [warpMode, toast, pushEvent, announce]);

  const handleWarpJumpComplete = useCallback(() => {
    setWarpJumpActive(false);
    setWarpMode(true);
    setSpeed(284802835);
    toast('Warp engaged', 'event');
    pushEvent('warp', 'Warp engaged', '284,802,835 m/s');
    announce('Warp engaged. All systems nominal.');
  }, [toast, pushEvent, announce]);

  const handleToggleBh = useCallback(() => {
    setBhMode(prev => {
      toast(!prev ? 'Black hole mode active' : 'Black hole mode off', 'warn');
      pushEvent('bh', !prev ? 'Black hole mode ON' : 'Black hole mode OFF', '');
      announce(!prev ? 'Black hole mode active' : 'Black hole mode off');
      return !prev;
    });
  }, [toast, pushEvent, announce]);

  const handleToggleAudio = useCallback(() => {
    setAudioEnabled(prev => {
      toast(!prev ? 'Audio timeline active' : 'Audio muted', 'info');
      return !prev;
    });
  }, [toast]);

  // Fullscreen
  useEffect(() => {
    if (fullscreen) {
      document.documentElement.requestFullscreen?.();
    } else {
      document.exitFullscreen?.();
    }
  }, [fullscreen]);

  const handleToggleFullscreen = useCallback(() => {
    setFullscreen(prev => !prev);
  }, []);

  // Vehicle color theming
  useEffect(() => {
    const v = VEHICLES.find(x => x.id === activeVehicle);
    if (v) {
      document.documentElement.style.setProperty('--theme-color', v.color);
      document.documentElement.style.setProperty('--theme-rgb', hexToRgb(v.color));
    }
  }, [activeVehicle]);

  // Tab transition handler
  const switchTab = useCallback((t: 'dashboard' | 'labs') => {
    if (t === tab) return;
    setTabTransition('exit');
    setTimeout(() => {
      setTab(t);
      setTabTransition('enter');
    }, 200);
    setTimeout(() => setTabTransition(null), 550);
  }, [tab]);

  // When realMode toggles, use theme color
  useEffect(() => {
    if (realMode) {
      document.documentElement.style.setProperty('--theme-color', '#10b981');
      document.documentElement.style.setProperty('--theme-rgb', '16, 185, 129');
    }
  }, [realMode]);

  // When boost changes in real mode, recompute speed
  useEffect(() => {
    if (realMode) {
      setSpeed(gpsSpeed * boost);
    }
  }, [boost, realMode, gpsSpeed]);

  // BH proximity alert
  useEffect(() => {
    if (bhMode && bhProx < 0.25) {
      toast('⚠️ Approaching event horizon!', 'warn');
    }
  }, [bhProx, bhMode, toast]);

  const handleToggleRealMode = useCallback(() => {
    setRealMode(prev => {
      const next = !prev;
      if (next) {
        setManualOverride(false);
        setWarpMode(false);
        setSpeed(gpsSpeed * boost);
        toast('Real mode — GPS data live, boost active', 'info');
        pushEvent('real', 'Real mode ON', `${boost}× boost`);
        announce(`Real mode active. Boost factor ${boost}`);
      } else {
        setSpeed(gpsSpeed);
        toast('Simulation mode restored', 'info');
        pushEvent('real', 'Simulation mode restored', '');
        announce('Simulation mode restored');
      }
      return next;
    });
  }, [gpsSpeed, boost, toast, pushEvent, announce]);

  // Auto vehicle detection from GPS speed
  useEffect(() => {
    if (manualOverride || warpMode || realMode) return;
    const kmh = speed * 3.6;
    let vehicle = 'car';
    if (kmh < 1) return;
    if (kmh > 10000) vehicle = 'rocket';
    else if (kmh > 500) vehicle = 'jet';
    if (vehicle !== activeVehicle) {
      setActiveVehicle(vehicle);
      pushEvent('speed', `Auto-detected: ${vehicle}`, `${kmh.toFixed(0)} km/h`);
    }
  }, [speed, manualOverride, warpMode, realMode, activeVehicle, pushEvent]);

  // Threshold alerts
  useEffect(() => {
    if (!metrics) return;
    if (metrics.gamma > alertThresholds.maxGamma) {
      pushEvent('alert', `γ = ${metrics.gamma.toFixed(2)} exceeds threshold`, '');
    }
    if (metrics.speed_kmh > alertThresholds.maxSpeed / 3.6) {
      pushEvent('alert', `Speed threshold exceeded`, `${metrics.speed_kmh.toFixed(0)} km/h`);
    }
  }, [metrics, alertThresholds, pushEvent]);

  useKeyboard({
    '1': () => setTab('dashboard'),
    '2': () => setTab('labs'),
    'w': () => {
      if (realMode) { toast('Disable Real Mode first', 'warn'); return; }
      if (warpMode) {
        setWarpMode(false);
        setSpeed(0);
        toast('Warp disengaged', 'event');
      } else {
        setWarpJumpActive(true);
      }
    },
    'b': () => {
      if (realMode) { toast('Disable Real Mode first', 'warn'); return; }
      setBhMode(prev => {
        toast(!prev ? 'Black hole mode active' : 'Black hole mode off', 'warn');
        return !prev;
      });
    },
    'm': () => {
      if (realMode) { toast('Disable Real Mode first', 'warn'); return; }
      setManualOverride(prev => !prev);
    },
    'a': () => {
      setAudioEnabled(prev => {
        toast(!prev ? 'Audio timeline active' : 'Audio muted', 'info');
        return !prev;
      });
    },
    'f': () => setFullscreen(prev => !prev),
    '?': () => setShowShortcuts(prev => !prev),
    's': () => setShowSettings(prev => !prev),
    'r': () => handleToggleRealMode(),
    'i': () => setShowAbout(prev => !prev),
    'v': () => {
      setSpeechEnabled(prev => { toast(!prev ? 'Voice announcements on' : 'Voice announcements off', 'info'); return !prev; });
    },
    'l': () => {
      setLaps(prev => {
        const elapsed = Math.floor((Date.now() - sessionStart.current) / 1000);
        const label = `Split ${prev.length + 1}`;
        toast(`${label}: ${Math.floor(elapsed / 60)}m ${elapsed % 60}s`, 'event');
        announce(label);
        pushEvent('speed', label, `${Math.floor(elapsed / 60)}m ${elapsed % 60}s`);
        return [...prev, { time: elapsed, label: `L${prev.length + 1}` }];
      });
    },
    '3': () => {
      if (realMode) return;
      setActiveVehicle('car');
      setManualOverride(true);
      setSpeed(200 / 4 / 3.6);
      setSpeedLimitKmh(200);
      toast('Car preset', 'info');
    },
    '4': () => {
      if (realMode) return;
      setActiveVehicle('jet');
      setManualOverride(true);
      setSpeed(3000 / 4 / 3.6);
      setSpeedLimitKmh(3000);
      toast('Jet preset', 'info');
    },
    '5': () => {
      if (realMode) return;
      setActiveVehicle('rocket');
      setManualOverride(true);
      setSpeed(30000 / 4 / 3.6);
      setSpeedLimitKmh(30000);
      toast('Rocket preset', 'info');
    },
    '6': () => {
      if (realMode) return;
      setActiveVehicle('warp');
      setManualOverride(true);
      setSpeed(284802835);
      setSpeedLimitKmh(1e9);
      toast('Warp preset', 'event');
    },
    'Escape': () => { setShowShortcuts(false); setShowSettings(false); setShowAbout(false); },
  });

  const exportLog = () => {
    const blob = new Blob([JSON.stringify(logbook, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `chronos-log-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const exportImage = useCallback(() => {
    const el = document.getElementById('dashboard-capture');
    if (!el) return;
    const canvas = document.createElement('canvas');
    const scale = 2;
    canvas.width = el.scrollWidth * scale;
    canvas.height = el.scrollHeight * scale;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    const data = `<svg xmlns="http://www.w3.org/2000/svg" width="${canvas.width}" height="${canvas.height}">
      <foreignObject width="100%" height="100%">
        <div xmlns="http://www.w3.org/1999/xhtml">
          <style>${Array.from(document.styleSheets).map(s => {
            try { return Array.from(s.cssRules || []).map(r => r.cssText).join(''); }
            catch { return ''; }
          }).join('')}</style>
          ${el.outerHTML}
        </div>
      </foreignObject>
    </svg>`;
    const blob = new Blob([data], { type: 'image/svg+xml;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const img = new Image();
    img.onload = () => {
      ctx.drawImage(img, 0, 0);
      URL.revokeObjectURL(url);
      canvas.toBlob(b => {
        if (!b) return;
        const a = document.createElement('a');
        a.href = URL.createObjectURL(b);
        a.download = `chronos-dash-${Date.now()}.png`;
        a.click();
      });
    };
    img.src = url;
    toast('Dashboard exported as PNG', 'event');
  }, [toast]);

  return (
    <>
      <ParticleBackground warpMode={warpMode} speed={speed} />
      <AuroraBackground />
      <RainOverlay intensity={settings.rainIntensity} />
      <MouseGlow />
      <div className="scanlines" />
      <GlitchOverlay />
      <WarpJumpAnimation active={warpJumpActive} onComplete={handleWarpJumpComplete} />
      <div id="dashboard-capture" className="relative z-10 min-h-screen p-4 md:p-8 space-y-6 max-w-6xl mx-auto">
        <Header
        audioEnabled={audioEnabled}
        bhMode={bhMode}
        warpMode={warpMode}
        onToggleAudio={handleToggleAudio}
        onToggleBh={handleToggleBh}
        onExportLog={exportLog}
        onToggleWarp={handleToggleWarp}
      />

      {/* Tab Navigation */}
      <div className="flex gap-1">
        {['dashboard' as const, 'labs' as const].map(t => (
          <button
            key={t}
            onClick={() => switchTab(t)}
            className={`px-5 py-2 text-[10px] font-bold uppercase tracking-[0.2em] rounded-t-lg transition-all border-b-2 ${
              tab === t
                ? 'text-blue-400 border-blue-500 bg-white/[0.03]'
                : 'text-slate-600 border-transparent hover:text-slate-400'
            }`}
          >
            {t === 'dashboard' ? '≡ Dashboard' : '⚗ Labs'}
          </button>
        ))}
        <div className="flex-1" />
        <button onClick={exportImage} className="px-2 py-1 text-[7px] font-mono text-slate-600 hover:text-slate-400 uppercase tracking-wider transition-colors" title="Export dashboard as PNG">
          📷
        </button>
        <FpsMonitor />
      </div>

      <div className={tabTransition === 'exit' ? 'tab-exit' : tabTransition === 'enter' ? 'tab-enter' : ''}>

      {tab === 'dashboard' ? (
        <>
          {!connected && (
            <div className="flex items-center gap-3 text-xs text-slate-500 card px-4 py-3">
              <span className="w-3 h-3 border-2 border-slate-600 border-t-blue-400 rounded-full animate-spin" />
              Establishing link to backend...
            </div>
          )}

          {connected && (
            <DataAgeIndicator connected={connected} version={dataVersion} />
          )}

          <ErrorBanner error={error} />

          {!connected ? (
            <>
              <SkeletonRow count={3} />
              <SkeletonRow count={4} />
            </>
          ) : (
            <>
              <EnergeticsPanel metrics={metrics} />

              <MetricCards
                metrics={metrics}
                cumulativeDilation={cumulativeDilation}
                userPos={userPos}
                onResetClock={() => setCumulativeDilation(0)}
              />

              {/* Trip Info Strip */}
              <ParallaxCard>
              <div className="card p-4" style={{ '--accent': '#3b82f6' } as React.CSSProperties}>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div>
                    <p className="text-[9px] uppercase tracking-widest text-slate-500">Speed</p>
                    <p className="text-lg font-mono font-bold text-blue-400">
                      {metrics ? (metrics.speed_kmh > 1e5 ? `${(metrics.beta * 100).toFixed(2)}% c` : `${metrics.speed_kmh.toFixed(0)} km/h`) : '--'}
                    </p>
                  </div>
                  <div>
                    <p className="text-[9px] uppercase tracking-widest text-slate-500">Gamma</p>
                    <p className="text-lg font-mono font-bold text-emerald-400">γ = {metrics ? metrics.gamma.toFixed(4) : '1.0000'}</p>
                  </div>
                  <div>
                    <p className="text-[9px] uppercase tracking-widest text-slate-500">Real Distance</p>
                    <p className="text-lg font-mono font-bold text-slate-300">{metrics ? (metrics.real_dist_m / 1000).toFixed(1) : '0.0'} km</p>
                  </div>
                  <div>
                    <p className="text-[9px] uppercase tracking-widest text-slate-500">Contracted</p>
                    <p className="text-lg font-mono font-bold text-purple-400">{metrics ? (metrics.contracted_dist_m / 1000).toFixed(3) : '0.000'} km</p>
                  </div>
                </div>
                {metrics && (
                  <div className="mt-3 pt-2 border-t border-slate-800/50 flex gap-3 text-[7px] font-mono">
                    {[
                      { label: 'β', val: metrics.beta, warn: metrics.beta > 0.9 },
                      { label: 'γ', val: metrics.gamma - 1, warn: metrics.gamma > 10 },
                      { label: 'δt', val: metrics.time_dilation_ns, warn: metrics.time_dilation_ns > 1e6 },
                    ].map(({ label, val, warn }) => (
                      <span key={label} className={`tabular-nums ${warn ? 'text-yellow-400' : 'text-slate-600'}`}>
                        {label}: {val >= 1e6 ? `${(val / 1e6).toFixed(2)}M` : val.toFixed(4)}
                        {warn && <span className="ml-1 text-[6px]">⚠</span>}
                      </span>
                    ))}
                  </div>
                )}
              </div>
              </ParallaxCard>

              {/* Metric History Sparklines */}
              {metricHistory.length >= 2 && (
                <div className="card p-3">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="w-1 h-1 rounded-full bg-emerald-500" />
                    <span className="font-bold text-[7px] uppercase tracking-[0.2em] text-slate-600">Trends (γ · log km/h · ns/s)</span>
                  </div>
                  <MetricHistory data={metricHistory} />
                </div>
              )}

              {metrics && (
                <PhysicsReference
                  beta={metrics.beta}
                  gamma={metrics.gamma}
                  speedKmh={metrics.speed_kmh}
                  dopplerFactor={metrics.doppler_factor}
                  timeDilationNs={metrics.time_dilation_ns}
                  gravDilationNs={metrics.grav_dilation_ns}
                />
              )}

              {/* Relativistic Effects Row */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <ParallaxCard><DopplerShiftPreview dopplerFactor={metrics?.doppler_factor ?? 1} /></ParallaxCard>
                <ParallaxCard><ProperTimeClock gamma={metrics?.gamma ?? 1} /></ParallaxCard>
                <ParallaxCard><LengthContractionBar
                  gamma={metrics?.gamma ?? 1}
                  realDistM={metrics?.real_dist_m ?? 0}
                  contractedDistM={metrics?.contracted_dist_m ?? 0}
                /></ParallaxCard>
              </div>

              {/* Logbook */}
              <LogbookPanel logbook={logbook} />
            </>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2 space-y-6">
              <MinkowskiDiagram simultaneityTilt={metrics?.simultaneity_tilt ?? 0} />
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <CurvatureVisual
                  gamma={metrics?.gamma ?? 1}
                  gravDilation={metrics?.grav_dilation_ns ?? 0}
                />
                <TesseractVisual />
              </div>
            </div>
            <div className="space-y-6 stagger-fade">
              <TripComputer
                speedMs={speed}
                gamma={metrics?.gamma ?? 1}
                destPos={destPos}
                userPos={userPos}
              />

              {metrics && <RecordsTracker metrics={metrics} />}

              {userPos && (<div className="card p-3">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-[8px]">📍</span>
                  <span className="font-bold text-[7px] uppercase tracking-[0.2em] text-slate-600">Pin Destination</span>
                </div>
                <DestinationSearch onSelect={handlePinDestination} />
              </div>)}

              {/* Trip Summary */}
              <div className="card p-3">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-[8px]">📊</span>
                  <span className="font-bold text-[7px] uppercase tracking-[0.2em] text-slate-600">Trip Summary</span>
                </div>
                <div className="space-y-1 text-[8px] font-mono">
                  <div className="flex justify-between"><span className="text-slate-500">Session</span><span className="text-slate-400">{Math.floor((Date.now() - sessionStart.current) / 60000)}m {(Math.floor((Date.now() - sessionStart.current) / 1000)) % 60}s</span></div>
                  <div className="flex justify-between"><span className="text-slate-500">GPS Distance</span><span className="text-slate-400">{tripStarted ? `${(totalDistance / 1000).toFixed(2)} km` : '--'}</span></div>
                  <div className="flex justify-between"><span className="text-slate-500">Events Logged</span><span className="text-slate-400">{timelineEvents.length}</span></div>
                </div>
              </div>

              <DeviceStatus />

              {/* Voice toggle + Lap controls */}
              <div className="flex gap-2">
                <button
                  onClick={() => setSpeechEnabled(prev => { toast(!prev ? 'Voice announcements on' : 'Voice announcements off', 'info'); return !prev; })}
                  className={`flex-1 px-2 py-1.5 text-[7px] font-bold uppercase tracking-[0.2em] rounded-lg border transition-all ${
                    speechEnabled ? 'bg-purple-500/20 border-purple-500/40 text-purple-400' : 'bg-white/5 border-white/10 text-slate-500'
                  }`}
                >
                  {speechEnabled ? 'Voice ON' : 'Voice OFF'}
                </button>
                <button
                  onClick={() => {
                    const elapsed = Math.floor((Date.now() - sessionStart.current) / 1000);
                    const label = `L${laps.length + 1}`;
                    toast(`Split: ${Math.floor(elapsed / 60)}m ${elapsed % 60}s`, 'event');
                    announce(`Split ${laps.length + 1}`);
                    pushEvent('speed', `Split ${laps.length + 1}`, `${Math.floor(elapsed / 60)}m ${elapsed % 60}s`);
                    setLaps(prev => [...prev, { time: elapsed, label }]);
                  }}
                  className="px-2 py-1.5 text-[7px] font-bold uppercase tracking-[0.2em] rounded-lg border border-white/10 text-slate-500 hover:text-slate-300"
                >
                  ◷ Split
                </button>
              </div>

              {laps.length > 0 && (
                <div className="card p-3">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-[8px]">⏱</span>
                    <span className="font-bold text-[7px] uppercase tracking-[0.2em] text-slate-600">Splits</span>
                  </div>
                  <div className="space-y-0.5 text-[8px] font-mono">
                    {laps.map((l, i) => (
                      <div key={i} className="flex justify-between">
                        <span className="text-slate-500">{l.label}</span>
                        <span className="text-slate-400">{Math.floor(l.time / 60)}m {l.time % 60}s</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <JourneyTimeline
                events={timelineEvents}
                collapsed={timelineCollapsed}
                onToggle={() => setTimelineCollapsed(prev => !prev)}
              />

              {userPos && (
                <RoadInfo lat={userPos.lat} lon={userPos.lon} speedMs={speed} />
              )}

              {audioEnabled && (
                <div className="card p-3">
                  <div className="flex items-center gap-2 mb-2">
                    <span className={`w-1.5 h-1.5 rounded-full ${audioEnabled ? 'bg-emerald-500 animate-pulse' : 'bg-slate-600'}`} />
                    <span className="font-bold text-[8px] uppercase tracking-[0.2em] text-slate-500">Sonic Timeline</span>
                    <span className="text-[7px] font-mono text-slate-600 ml-auto">γ={metrics?.gamma.toFixed(2) ?? '1.00'}</span>
                  </div>
                  <AudioVisualizer active={audioEnabled} gamma={metrics?.gamma ?? 1} />
                </div>
              )}

              <div className="card p-6">
                {/* Real Mode Bar */}
                <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-800/50">
                  <div className="flex items-center gap-2">
                    <button
                      onClick={handleToggleRealMode}
                      className={`px-3 py-1 rounded text-[8px] font-bold uppercase tracking-[0.2em] border transition-all ${
                        realMode
                          ? 'bg-emerald-500/20 border-emerald-500/40 text-emerald-400 shadow-[0_0_12px_-4px_#10b981]'
                          : 'bg-white/5 border-white/10 text-slate-500 hover:text-slate-300'
                      }`}
                    >
                      Real Mode
                    </button>
                    {realMode && (
                      <span className="text-[7px] font-mono text-emerald-600/60">
                        GPS × {boost.toLocaleString()}
                      </span>
                    )}
                  </div>
                  {realMode && (
                    <span className="text-[7px] font-mono text-slate-600">
                      GPS: {gpsSpeed.toFixed(1)} m/s
                    </span>
                  )}
                </div>

                {/* Boost Slider (real mode only) */}
                {realMode && (
                  <div className="mb-4 space-y-1">
                    <div className="flex justify-between items-center">
                      <span className="text-[7px] uppercase tracking-[0.2em] text-slate-600">Boost Factor</span>
                      <span className="text-[8px] font-mono text-emerald-400">{boost.toLocaleString()}×</span>
                    </div>
                    <input
                      type="range"
                      min="0"
                      max="8"
                      step="0.1"
                      value={Math.log10(boost)}
                      onChange={(e) => setBoost(Math.round(Math.pow(10, parseFloat(e.target.value))))}
                      className="w-full h-1 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-emerald-500"
                    />
                    <div className="flex justify-between text-[6px] text-slate-700 font-mono">
                      <span>1×</span>
                      <span>10⁸×</span>
                    </div>
                  </div>
                )}

                {/* Speed Gauge */}
                <div className="flex flex-col items-center mb-4">
                  <SpeedGauge
                    speedKmh={speed * 3.6}
                    maxSpeed={realMode ? Math.max(speedLimitKmh, speed * 3.6) : speedLimitKmh}
                    label={realMode ? 'GPS' : (VEHICLES.find(v => v.id === activeVehicle)?.label || 'Manual')}
                    color={realMode ? '#10b981' : (VEHICLES.find(v => v.id === activeVehicle)?.color || '#3b82f6')}
                  />
                  {metrics && (
                    <SpeedContext
                      speedKmh={metrics.speed_kmh}
                      beta={metrics.beta}
                      gamma={metrics.gamma}
                    />
                  )}
                </div>

                {/* Radar Sweep + Vehicle Presets row */}
                <div className="flex gap-4 items-start mb-5">
                  <div className="flex-shrink-0">
                    <RadarSweep speed={speed} />
                  </div>
                  <div className="flex-1 grid grid-cols-2 gap-2">
                    {VEHICLES.map(v => (
                    <button
                      key={v.id}
                      disabled={realMode}
                      onClick={() => {
                        setActiveVehicle(v.id);
                        setManualOverride(true);
                        const speedMs = v.id === 'warp' ? 284802835 : (v.maxKmh / 4) / 3.6;
                        setSpeed(speedMs);
                        setSpeedLimitKmh(v.maxKmh);
                      }}
                      className={`flex-1 px-2 py-1.5 text-[10px] uppercase tracking-widest font-bold rounded-lg border transition-all ${
                        realMode
                          ? 'bg-slate-900/30 border-slate-800 text-slate-700 cursor-not-allowed'
                          : activeVehicle === v.id && manualOverride
                          ? 'bg-slate-800 border-blue-500 text-blue-400 shadow-[0_0_12px_-4px_#3b82f6]'
                          : 'bg-slate-800/50 border-slate-700 text-slate-500 hover:text-slate-300'
                      }`}
                      style={!realMode && activeVehicle === v.id && manualOverride ? { borderColor: v.color, color: v.color } : {}}
                    >
                      {v.label}
                    </button>
                  ))}
                </div>
              </div>

                {/* Manual Override Toggle */}
                <div className={`flex justify-between items-center mb-4 ${realMode ? 'opacity-30' : ''}`}>
                  <h2 className="font-bold text-xs uppercase tracking-wider text-slate-400">Manual Override</h2>
                  <input
                    type="checkbox"
                    checked={manualOverride}
                    disabled={realMode}
                    onChange={(e) => setManualOverride(e.target.checked)}
                    className="w-4 h-4 accent-blue-500"
                  />
                </div>

                {/* Speed Slider */}
                <input
                  type="range"
                  min="0"
                  max={speedLimitKmh}
                  step="1"
                  value={manualOverride ? speed * 3.6 : 0}
                  disabled={!manualOverride}
                  onChange={(e) => setSpeed(parseFloat(e.target.value) / 3.6)}
                  className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-blue-500 disabled:opacity-30"
                />
                <div className="flex justify-between text-[10px] text-slate-500 mt-2">
                  <span>0</span>
                  <span className="font-bold text-blue-400">
                    {manualOverride ? (speed * 3.6).toFixed(0) : '--'}
                  </span>
                  <span>{speedLimitKmh.toLocaleString()}</span>
                </div>
                <p className="text-[8px] text-slate-600 text-center mt-1">km/h</p>

                {bhMode && (
                  <div className="mt-6 pt-5 border-t border-slate-800/50 space-y-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="w-1.5 h-1.5 rounded-full bg-red-500 animate-ping" />
                        <h2 className="font-bold text-[10px] uppercase tracking-[0.2em] text-red-400">
                          Singularity Proximity
                        </h2>
                      </div>
                      <span className="text-[9px] font-mono text-slate-500">
                        R = {metrics ? (metrics.current_radius / metrics.schwarzschild_radius).toFixed(2) : '--'} R<sub>s</sub>
                      </span>
                    </div>

                    <BlackHoleVisual proximity={bhProx} />

                    <input
                      type="range"
                      min="0"
                      max="1"
                      step="0.01"
                      value={bhProx}
                      onChange={(e) => setBhProx(parseFloat(e.target.value))}
                      className="w-full h-1.5 bg-red-900/30 rounded-lg appearance-none cursor-pointer accent-red-600"
                    />
                    <div className="flex justify-between text-[7px] text-slate-700 uppercase font-bold tracking-tight">
                      <span className="text-red-500/60">Event Horizon</span>
                      <span>Deep Orbit</span>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </>
      ) : (
        <Suspense fallback={<div className="h-96 bg-slate-900 rounded-2xl animate-pulse" />}>
          <LabsPage />
        </Suspense>
      )}
      </div>

      </div>

      <SystemBar connected={connected} speed={speed} metrics={metrics} />
      <ShortcutsModal open={showShortcuts} onClose={() => setShowShortcuts(false)} />
      <SettingsPanel
        open={showSettings}
        onClose={() => setShowSettings(false)}
        settings={settings}
        onSettingsChange={setSettings}
      />
      <AboutPanel open={showAbout} onClose={() => setShowAbout(false)} />
    </>
  );
}

export default function App() {
  return (
    <ToastProvider>
      <DashboardInner />
    </ToastProvider>
  );
}
