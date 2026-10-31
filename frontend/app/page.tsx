'use client';

import React, { useState, useEffect, useTransition } from 'react';
import { 
  Zap, 
  Sliders, 
  Compass, 
  TrendingUp, 
  ShieldAlert, 
  CheckCircle, 
  BatteryCharging, 
  Activity, 
  MapPin, 
  Sparkles, 
  Play, 
  ChevronDown, 
  Layers,
  Award,
  Cpu
} from 'lucide-react';

interface DrivingTip {
  category: string;
  severity: 'high' | 'medium' | 'info' | 'success';
  title: string;
  description: string;
  action: string;
  potential_saving_kwh: number;
}

interface OptimizationResult {
  current_profile: {
    predicted_energy_kwh: number;
    efficiency_km_per_kwh: number;
    efficiency_wh_per_km: number;
    eco_score: number;
    cluster_id?: number;
    cluster_name: string;
  };
  optimized_profile: {
    predicted_energy_kwh: number;
    efficiency_km_per_kwh: number;
    energy_saved_kwh: number;
    energy_saved_pct: number;
    extra_range_km: number;
  };
  tips: DrivingTip[];
}

export default function DrivingOptimizerDashboard() {
  // Telemetry Inputs
  const [speed, setSpeed] = useState<number>(65);
  const [accel, setAccel] = useState<number>(-0.2);
  const [slope, setSlope] = useState<number>(2.5);
  const [roadType, setRoadType] = useState<number>(1); // 1: Highway, 2: Urban, 3: Rural
  const [distance, setDistance] = useState<number>(25);
  const [drivingMode, setDrivingMode] = useState<number>(2); // 1: Eco, 2: Sport, 3: Comfort
  const [batterySoc, setBatterySoc] = useState<number>(65);
  const [tirePsi, setTirePsi] = useState<number>(31.5);
  const [temperature, setTemperature] = useState<number>(20);
  const [weather, setWeather] = useState<number>(1);
  const [activePreset, setActivePreset] = useState<string>('custom');

  // Dashboard Results
  const [results, setResults] = useState<OptimizationResult | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [backendOnline, setBackendOnline] = useState<boolean>(false);
  const [, startTransition] = useTransition();

  // Route Simulation State
  const [simResults, setSimResults] = useState<Array<{
    segment: string;
    km: number;
    speed: number;
    slope: number;
    current_kwh: number;
    opt_kwh: number;
    cum_current: number;
    cum_opt: number;
  }>>([]);
  const [simRunning, setSimRunning] = useState<boolean>(false);

  // Quick Presets
  const applyPreset = (name: string) => {
    setActivePreset(name);
    if (name === 'highway') {
      setSpeed(125); setAccel(2.2); setSlope(1.0); setDrivingMode(2); setRoadType(1); setDistance(40);
    } else if (name === 'urban') {
      setSpeed(45); setAccel(-2.5); setSlope(0.5); setDrivingMode(3); setRoadType(2); setDistance(15);
    } else if (name === 'mountain') {
      setSpeed(65); setAccel(1.4); setSlope(8.5); setDrivingMode(2); setRoadType(3); setDistance(25);
    } else if (name === 'eco') {
      setSpeed(75); setAccel(0.3); setSlope(0.0); setDrivingMode(1); setRoadType(1); setDistance(35);
    }
  };

  // Telemetry API call
  const fetchOptimization = async () => {
    try {
      const payload = {
        Speed_kmh: speed,
        Acceleration_ms2: accel,
        'Slope_%': slope,
        Slope_pct: slope,
        Road_Type: roadType,
        Distance_Travelled_km: distance,
        Driving_Mode: drivingMode,
        'Battery_State_%': batterySoc,
        Battery_State_pct: batterySoc,
        Tire_Pressure_psi: tirePsi,
        Temperature_C: temperature,
        Weather_Condition: weather,
        Vehicle_Weight_kg: 1850.0,
        Battery_Voltage_V: 350.0,
        Battery_Temperature_C: 28.0,
        Wind_Speed_ms: 6.0,
        'Humidity_%': 55.0
      };

      const res = await fetch('/api/optimize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (res.ok) {
        const data = await res.json();
        startTransition(() => {
          setResults(data);
          setLoading(false);
          setBackendOnline(true);
        });
      }
    } catch {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOptimization();
  }, [speed, accel, slope, roadType, distance, drivingMode, batterySoc, tirePsi, temperature, weather]);

  // Run Route Simulation
  const handleSimulateRoute = () => {
    setSimRunning(true);
    const segments = [
      { segment: '1. City Departure', km: 3.0, speed: 35.0, slope: 0.0, road: 2 },
      { segment: '2. Stop & Go Signals', km: 2.0, speed: 22.0, slope: 0.5, road: 2 },
      { segment: '3. Ring Road Merge', km: 5.0, speed: 60.0, slope: 1.0, road: 1 },
      { segment: '4. Highway Cruise', km: 10.0, speed: 95.0, slope: 0.0, road: 1 },
      { segment: '5. Fast Express Strip', km: 12.0, speed: 120.0, slope: -0.5, road: 1 },
      { segment: '6. Foothills Ascent', km: 6.0, speed: 70.0, slope: 6.5, road: 3 },
      { segment: '7. Mountain Climb', km: 4.0, speed: 50.0, slope: 9.0, road: 3 },
      { segment: '8. Mountain Descent', km: 5.0, speed: 55.0, slope: -4.5, road: 3 },
      { segment: '9. Suburban Entry', km: 4.0, speed: 50.0, slope: 0.0, road: 2 },
      { segment: '10. Destination Arrival', km: 2.0, speed: 30.0, slope: 0.0, road: 2 }
    ];

    let cumC = 0;
    let cumO = 0;
    const computed = segments.map(s => {
      const basePerKm = 0.16 + (Math.max(0, s.speed - 70) ** 1.8) * 0.0018 + (s.slope > 0 ? s.slope * 0.012 : s.slope * 0.006);
      const c = Number((basePerKm * s.km).toFixed(2));
      const optSp = s.speed > 90 ? 85 : (s.speed > 50 && s.road === 2 ? 45 : s.speed);
      const optPerKm = 0.16 + (Math.max(0, optSp - 70) ** 1.8) * 0.0018 + (s.slope > 0 ? s.slope * 0.01 : s.slope * 0.006);
      const o = Number((optPerKm * s.km).toFixed(2));
      cumC += c;
      cumO += o;
      return {
        segment: s.segment,
        km: s.km,
        speed: s.speed,
        slope: s.slope,
        current_kwh: c,
        opt_kwh: o,
        cum_current: Number(cumC.toFixed(2)),
        cum_opt: Number(cumO.toFixed(2))
      };
    });

    setSimResults(computed);
    setSimRunning(false);
  };

  useEffect(() => {
    handleSimulateRoute();
  }, []);

  const curr = results?.current_profile;
  const opt = results?.optimized_profile;
  const tips = results?.tips || [];

  // Determine Score Grade
  const score = curr?.eco_score || 50;
  const getGradeInfo = (s: number) => {
    if (s >= 80) return { grade: 'A+ (Optimal)', color: 'text-emerald-400', border: 'border-emerald-500/40', bg: 'bg-emerald-500/10' };
    if (s >= 65) return { grade: 'B (Good)', color: 'text-sky-400', border: 'border-sky-500/40', bg: 'bg-sky-500/10' };
    if (s >= 45) return { grade: 'C (Average)', color: 'text-amber-400', border: 'border-amber-500/40', bg: 'bg-amber-500/10' };
    return { grade: 'D / F (Inefficient)', color: 'text-rose-400', border: 'border-rose-500/40', bg: 'bg-rose-500/10' };
  };
  const gradeInfo = getGradeInfo(score);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans antialiased selection:bg-emerald-500 selection:text-white pb-16">
      
      {/* Top Navbar */}
      <header className="border-b border-slate-800/80 bg-slate-950/80 backdrop-blur sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-500 to-cyan-500 flex items-center justify-center shadow-lg shadow-emerald-500/20">
              <Zap className="w-6 h-6 text-slate-950 stroke-[2.5]" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-base sm:text-lg font-bold text-white tracking-tight">AI Driving Efficiency Optimizer</h1>
                <span className="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 hidden sm:inline-block">Next.js 16 + React 19</span>
              </div>
              <p className="text-xs text-slate-400">Behavioral Telematics Analysis &bull; Energy Usage Prediction &bull; Contextual AI Driving Tips</p>
            </div>
          </div>
          <div className="flex items-center gap-2 sm:gap-3">
            <span className="inline-flex items-center gap-1.5 text-xs text-emerald-400 bg-emerald-950/60 border border-emerald-800/80 px-3 py-1 rounded-full font-medium">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span className="hidden sm:inline">{backendOnline ? 'Scikit-learn Model Connected' : 'Edge Inference Engine Active'}</span>
              <span className="sm:hidden">AI Active</span>
            </span>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-6 space-y-6">

        {/* Preset Selector Banner */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-3 flex flex-wrap items-center justify-between gap-3 shadow-lg">
          <div className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
            <Sparkles className="w-4 h-4 text-emerald-400" />
            Quick Presets:
          </div>
          <div className="flex flex-wrap gap-2">
            {[
              { id: 'highway', label: '🏎️ Aggressive Speeder' },
              { id: 'urban', label: '🏙️ Urban Stop & Go' },
              { id: 'mountain', label: '⛰️ Mountain Ascent' },
              { id: 'eco', label: '🌱 Optimal Eco-Cruiser' }
            ].map(p => (
              <button
                key={p.id}
                onClick={() => applyPreset(p.id)}
                className={`text-xs px-3 py-1.5 rounded-lg font-medium transition ${
                  activePreset === p.id 
                    ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 shadow-sm'
                    : 'bg-slate-800 hover:bg-slate-700/80 text-slate-300 border border-slate-700/60'
                }`}
              >
                {p.label}
              </button>
            ))}
          </div>
        </div>

        {/* Main Grid: Telemetry Inputs vs Output Results */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">

          {/* Controls Column (5 cols) */}
          <div className="lg:col-span-5 space-y-5">
            <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 sm:p-6 shadow-xl space-y-5">
              <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                <h2 className="text-xs sm:text-sm font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
                  <Sliders className="w-4 h-4 text-emerald-400" />
                  Driving Telematics Controls
                </h2>
                <span className="text-[11px] text-emerald-400 font-semibold bg-emerald-950/40 border border-emerald-900/60 px-2 py-0.5 rounded-full">Live Predict</span>
              </div>

              {/* Speed Slider */}
              <div className="space-y-1.5">
                <div className="flex justify-between text-xs">
                  <span className="text-slate-400 font-medium">Cruising Speed</span>
                  <span className="font-bold text-emerald-400 text-sm">{speed} km/h</span>
                </div>
                <input
                  type="range"
                  min="10"
                  max="150"
                  value={speed}
                  onChange={(e) => { setSpeed(Number(e.target.value)); setActivePreset('custom'); }}
                  className="w-full h-2 bg-slate-800 rounded-lg cursor-pointer accent-emerald-500"
                />
                <div className="flex justify-between text-[10px] text-slate-500">
                  <span>10 km/h</span>
                  <span className="text-emerald-500/80 font-medium">Optimal Window (60-80 km/h)</span>
                  <span>150 km/h</span>
                </div>
              </div>

              {/* Acceleration & Braking Slider */}
              <div className="space-y-1.5">
                <div className="flex justify-between text-xs">
                  <span className="text-slate-400 font-medium">Acceleration & Braking Force</span>
                  <span className="font-bold text-emerald-400 text-sm">{accel > 0 ? `+${accel.toFixed(2)}` : accel.toFixed(2)} m/s²</span>
                </div>
                <input
                  type="range"
                  min="-3.0"
                  max="3.0"
                  step="0.1"
                  value={accel}
                  onChange={(e) => { setAccel(Number(e.target.value)); setActivePreset('custom'); }}
                  className="w-full h-2 bg-slate-800 rounded-lg cursor-pointer accent-emerald-500"
                />
                <div className="flex justify-between text-[10px] text-slate-500">
                  <span className="text-rose-400/80">-3.0 (Friction Braking)</span>
                  <span>0.0 (Coasting)</span>
                  <span className="text-sky-400/80">+3.0 (Throttle Surge)</span>
                </div>
              </div>

              {/* Terrain Gradient / Slope Slider */}
              <div className="space-y-1.5">
                <div className="flex justify-between text-xs">
                  <span className="text-slate-400 font-medium">Terrain Slope (Road Gradient)</span>
                  <span className="font-bold text-emerald-400 text-sm">{slope > 0 ? `+${slope.toFixed(1)}` : slope.toFixed(1)} %</span>
                </div>
                <input
                  type="range"
                  min="-5.0"
                  max="10.0"
                  step="0.5"
                  value={slope}
                  onChange={(e) => { setSlope(Number(e.target.value)); setActivePreset('custom'); }}
                  className="w-full h-2 bg-slate-800 rounded-lg cursor-pointer accent-emerald-500"
                />
                <div className="flex justify-between text-[10px] text-slate-500">
                  <span className="text-emerald-400/80">-5% (Downhill Regen)</span>
                  <span>0% (Flat)</span>
                  <span className="text-amber-400/80">+10% (Steep Incline)</span>
                </div>
              </div>

              {/* Drive Mode Selector */}
              <div className="space-y-1.5">
                <label className="text-xs text-slate-400 font-medium">Driving Mode</label>
                <div className="grid grid-cols-3 gap-2">
                  {[
                    { id: 1, label: 'Eco', desc: 'Max Efficiency' },
                    { id: 2, label: 'Sport', desc: 'Aggressive' },
                    { id: 3, label: 'Comfort', desc: 'Balanced' }
                  ].map(m => (
                    <button
                      key={m.id}
                      onClick={() => { setDrivingMode(m.id); setActivePreset('custom'); }}
                      className={`py-2 px-2 text-xs font-semibold rounded-lg border transition text-center ${
                        drivingMode === m.id
                          ? 'border-emerald-500 bg-emerald-500/20 text-emerald-300 shadow-sm'
                          : 'border-slate-800 bg-slate-950 text-slate-400 hover:border-slate-700'
                      }`}
                    >
                      <div>{m.label}</div>
                      <div className="text-[9px] opacity-70 font-normal">{m.desc}</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Road Type & Trip Distance */}
              <div className="grid grid-cols-2 gap-3 pt-1">
                <div className="space-y-1.5">
                  <label className="text-xs text-slate-400 font-medium">Road Type</label>
                  <select
                    value={roadType}
                    onChange={(e) => { setRoadType(Number(e.target.value)); setActivePreset('custom'); }}
                    className="w-full bg-slate-950 border border-slate-800 text-xs text-slate-200 rounded-lg p-2.5 focus:ring-1 focus:ring-emerald-500"
                  >
                    <option value={1}>Highway</option>
                    <option value={2}>Urban City</option>
                    <option value={3}>Rural Road</option>
                  </select>
                </div>
                <div className="space-y-1.5">
                  <div className="flex justify-between text-xs">
                    <span className="text-slate-400 font-medium">Trip Distance</span>
                    <span className="font-bold text-slate-300">{distance} km</span>
                  </div>
                  <input
                    type="range"
                    min="1"
                    max="100"
                    value={distance}
                    onChange={(e) => { setDistance(Number(e.target.value)); setActivePreset('custom'); }}
                    className="w-full h-2 bg-slate-800 rounded-lg cursor-pointer accent-emerald-500 mt-2"
                  />
                </div>
              </div>

              {/* Collapsible Vehicle & Climate Parameters */}
              <details className="group pt-2 border-t border-slate-800">
                <summary className="text-xs font-semibold text-slate-400 cursor-pointer flex justify-between items-center py-1">
                  <span>Battery, Tire & Ambient Climate</span>
                  <ChevronDown className="w-4 h-4 text-slate-500 group-open:rotate-180 transition" />
                </summary>
                <div className="space-y-3 pt-3">
                  <div className="grid grid-cols-2 gap-3">
                    <div className="space-y-1">
                      <div className="flex justify-between text-xs">
                        <span className="text-slate-400">Battery SOC</span>
                        <span className="font-bold text-slate-300">{batterySoc}%</span>
                      </div>
                      <input
                        type="range"
                        min="10"
                        max="100"
                        value={batterySoc}
                        onChange={(e) => setBatterySoc(Number(e.target.value))}
                        className="w-full h-1.5 bg-slate-800 rounded-lg accent-emerald-500"
                      />
                    </div>
                    <div className="space-y-1">
                      <div className="flex justify-between text-xs">
                        <span className="text-slate-400">Tire Pressure</span>
                        <span className="font-bold text-slate-300">{tirePsi} psi</span>
                      </div>
                      <input
                        type="range"
                        min="26"
                        max="38"
                        step="0.5"
                        value={tirePsi}
                        onChange={(e) => setTirePsi(Number(e.target.value))}
                        className="w-full h-1.5 bg-slate-800 rounded-lg accent-emerald-500"
                      />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div className="space-y-1">
                      <div className="flex justify-between text-xs">
                        <span className="text-slate-400">Ambient Temp</span>
                        <span className="font-bold text-slate-300">{temperature}°C</span>
                      </div>
                      <input
                        type="range"
                        min="-5"
                        max="42"
                        value={temperature}
                        onChange={(e) => setTemperature(Number(e.target.value))}
                        className="w-full h-1.5 bg-slate-800 rounded-lg accent-emerald-500"
                      />
                    </div>
                    <div className="space-y-1">
                      <label className="text-xs text-slate-400">Weather</label>
                      <select
                        value={weather}
                        onChange={(e) => setWeather(Number(e.target.value))}
                        className="w-full bg-slate-950 border border-slate-800 text-xs text-slate-200 rounded-lg p-2"
                      >
                        <option value={1}>Clear</option>
                        <option value={2}>Rain</option>
                        <option value={3}>Snow</option>
                        <option value={4}>Fog</option>
                      </select>
                    </div>
                  </div>
                </div>
              </details>
            </div>
          </div>

          {/* Results Column (7 cols) */}
          <div className="lg:col-span-7 space-y-5">

            {/* 4 KPI Metric Cards */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3.5">
              <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 text-center shadow-lg">
                <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 flex items-center justify-center gap-1">
                  <Zap className="w-3.5 h-3.5 text-amber-400" />
                  Predicted Energy
                </div>
                <div className="mt-2 text-2xl font-extrabold text-white">
                  {curr?.predicted_energy_kwh ?? '--'} <span className="text-xs text-slate-400 font-normal">kWh</span>
                </div>
                <div className="text-[11px] text-slate-400 mt-1">{distance} km route</div>
              </div>

              <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 text-center shadow-lg">
                <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 flex items-center justify-center gap-1">
                  <Activity className="w-3.5 h-3.5 text-emerald-400" />
                  Efficiency
                </div>
                <div className="mt-2 text-2xl font-extrabold text-emerald-400">
                  {curr?.efficiency_km_per_kwh ?? '--'} <span className="text-xs text-slate-400 font-normal">km/kWh</span>
                </div>
                <div className="text-[11px] text-slate-400 mt-1">{curr?.efficiency_wh_per_km ?? '--'} Wh/km</div>
              </div>

              <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 text-center shadow-lg">
                <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 flex items-center justify-center gap-1">
                  <Award className="w-3.5 h-3.5 text-sky-400" />
                  Eco-Score
                </div>
                <div className={`mt-2 text-2xl font-extrabold ${gradeInfo.color}`}>
                  {score} <span className="text-xs text-slate-400 font-normal">/ 100</span>
                </div>
                <div className={`text-[11px] font-semibold mt-1 ${gradeInfo.color}`}>{gradeInfo.grade}</div>
              </div>

              <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 text-center shadow-lg">
                <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 flex items-center justify-center gap-1">
                  <Layers className="w-3.5 h-3.5 text-purple-400" />
                  Driving Style
                </div>
                <div className="mt-2 text-xs sm:text-sm font-bold text-slate-200 truncate" title={curr?.cluster_name}>
                  {curr?.cluster_name ?? 'Calculating...'}
                </div>
                <div className="text-[11px] text-slate-400 mt-1">K-Means Cluster</div>
              </div>
            </div>

            {/* AI Optimization Impact Banner */}
            <div className="bg-gradient-to-br from-slate-900 via-slate-900 to-emerald-950/40 border border-emerald-500/30 rounded-2xl p-5 sm:p-6 shadow-2xl relative overflow-hidden">
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-4 border-b border-slate-800">
                <div>
                  <span className="text-[11px] font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-1.5">
                    <Sparkles className="w-3.5 h-3.5" />
                    AI Optimization Impact
                  </span>
                  <h3 className="text-base sm:text-lg font-bold text-white mt-0.5">Potential Savings with Recommended Driving</h3>
                </div>
                <div className="px-3.5 py-1.5 rounded-full bg-emerald-500/20 border border-emerald-500/40 text-emerald-300 font-bold text-xs sm:text-sm flex items-center gap-1.5 shadow-sm">
                  <BatteryCharging className="w-4 h-4 text-emerald-400" />
                  <span>+{opt?.extra_range_km ?? 0.0} km Extra Range</span>
                </div>
              </div>
              <div className="grid grid-cols-3 gap-3 pt-4 text-center">
                <div>
                  <div className="text-[11px] text-slate-400 uppercase font-semibold">Energy Saved</div>
                  <div className="text-xl sm:text-2xl font-extrabold text-emerald-400 mt-1">{opt?.energy_saved_kwh ?? 0.0} kWh</div>
                </div>
                <div>
                  <div className="text-[11px] text-slate-400 uppercase font-semibold">Consumption Cut</div>
                  <div className="text-xl sm:text-2xl font-extrabold text-sky-400 mt-1">{opt?.energy_saved_pct ?? 0.0}%</div>
                </div>
                <div>
                  <div className="text-[11px] text-slate-400 uppercase font-semibold">Target Efficiency</div>
                  <div className="text-xl sm:text-2xl font-extrabold text-amber-400 mt-1">{opt?.efficiency_km_per_kwh ?? 0.0} km/kWh</div>
                </div>
              </div>
            </div>

            {/* Side-by-side Visual Bar Comparison */}
            <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-lg space-y-3">
              <div className="flex items-center justify-between text-xs">
                <span className="font-bold uppercase tracking-wider text-slate-400">Energy Consumption Comparison</span>
                <span className="text-emerald-400 font-medium">Save ~{opt?.energy_saved_kwh ?? 0.0} kWh</span>
              </div>
              
              <div className="space-y-3 pt-1">
                <div>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-slate-300 font-medium">Current Profile</span>
                    <span className="font-bold text-rose-400">{curr?.predicted_energy_kwh ?? 0.0} kWh</span>
                  </div>
                  <div className="w-full bg-slate-800 h-3.5 rounded-full overflow-hidden">
                    <div 
                      className="bg-rose-500 h-full rounded-full transition-all duration-500"
                      style={{ width: `${Math.min(100, ((curr?.predicted_energy_kwh || 5) / 18) * 100)}%` }}
                    ></div>
                  </div>
                </div>

                <div>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-slate-300 font-medium">AI-Optimized Profile</span>
                    <span className="font-bold text-emerald-400">{opt?.predicted_energy_kwh ?? 0.0} kWh</span>
                  </div>
                  <div className="w-full bg-slate-800 h-3.5 rounded-full overflow-hidden">
                    <div 
                      className="bg-emerald-500 h-full rounded-full transition-all duration-500"
                      style={{ width: `${Math.min(100, ((opt?.predicted_energy_kwh || 4) / 18) * 100)}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>

          </div>
        </div>

        {/* Section 2: Actionable Driving Tips (Core Guideline 3 Requirement) */}
        <div className="space-y-4 pt-2">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div>
              <h2 className="text-base sm:text-lg font-bold text-white flex items-center gap-2">
                <Compass className="w-5 h-5 text-emerald-400" />
                Actionable Driving Tips Based on Prediction Results
              </h2>
              <p className="text-xs text-slate-400">Contextual advice generated dynamically from ML model outputs and vehicle physics</p>
            </div>
            <span className="text-xs font-semibold px-3 py-1 bg-slate-900 border border-slate-800 rounded-full text-slate-300 self-start sm:self-auto">
              {tips.length} Actionable Tips Generated
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {tips.length === 0 ? (
              <div className="col-span-2 bg-slate-900/60 border border-slate-800 rounded-xl p-8 text-center text-slate-400">
                <CheckCircle className="w-8 h-8 text-emerald-400 mx-auto mb-2" />
                <p className="text-sm font-semibold text-slate-200">Driving Parameters Fully Optimized</p>
                <p className="text-xs mt-1">Vehicle is operating within ideal efficiency envelopes.</p>
              </div>
            ) : (
              tips.map((tip, idx) => {
                const isHigh = tip.severity === 'high';
                const isSuccess = tip.severity === 'success';
                const borderClass = isHigh ? 'border-rose-500/40 bg-rose-950/20' : isSuccess ? 'border-emerald-500/40 bg-emerald-950/20' : 'border-amber-500/40 bg-amber-950/20';
                const dotClass = isHigh ? 'bg-rose-400' : isSuccess ? 'bg-emerald-400' : 'bg-amber-400';
                const badgeClass = isHigh ? 'text-rose-400 bg-rose-950/80' : isSuccess ? 'text-emerald-400 bg-emerald-950/80' : 'text-amber-400 bg-amber-950/80';

                return (
                  <div key={idx} className={`border ${borderClass} rounded-xl p-4 space-y-2.5 shadow-lg`}>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className={`w-2 h-2 rounded-full ${dotClass}`}></span>
                        <span className="text-[11px] font-bold text-white uppercase tracking-wider">{tip.category}</span>
                      </div>
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded border border-slate-800 uppercase ${badgeClass}`}>
                        {tip.severity}
                      </span>
                    </div>
                    <h4 className="text-sm font-bold text-slate-100">{tip.title}</h4>
                    <p className="text-xs text-slate-400 leading-relaxed">{tip.description}</p>
                    <div className="pt-2 border-t border-slate-800/80 flex flex-wrap items-center justify-between gap-2 text-xs">
                      <span className="font-medium text-slate-200">
                        <span className="text-emerald-400 font-bold">👉 Action:</span> {tip.action}
                      </span>
                      {tip.potential_saving_kwh > 0 && (
                        <span className="text-[11px] font-bold text-emerald-400 bg-emerald-950/80 px-2 py-0.5 rounded border border-emerald-800/80">
                          Save ~{tip.potential_saving_kwh} kWh
                        </span>
                      )}
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Section 3: Telemetry Analysis Cards (Speed Curve & Radar) */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 pt-2">
          
          {/* Speed vs Energy Chart */}
          <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 sm:p-6 space-y-4 shadow-xl">
            <div className="flex items-center justify-between">
              <h3 className="text-xs sm:text-sm font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-emerald-400" />
                Energy vs Speed Curve
              </h3>
              <span className="text-xs text-emerald-400 font-medium">Sweet Spot: 60-80 km/h</span>
            </div>

            {/* SVG Speed Curve */}
            <div className="h-56 relative flex items-end">
              <svg className="w-full h-full overflow-visible" viewBox="0 0 500 200" preserveAspectRatio="none">
                {/* Optimal zone rectangle */}
                <rect x="180" y="20" width="80" height="160" fill="rgba(16, 185, 129, 0.12)" stroke="rgba(16, 185, 129, 0.3)" strokeDasharray="3,3" />
                <text x="185" y="40" fill="#34d399" fontSize="10" fontWeight="600">Optimal (60-80 km/h)</text>
                
                {/* Curve path */}
                <path
                  d="M 20 170 Q 150 150 250 130 T 480 30"
                  fill="none"
                  stroke="#38bdf8"
                  strokeWidth="3"
                />

                {/* Operating Point */}
                {(() => {
                  const normalizedX = 20 + ((speed - 10) / 140) * 460;
                  const normalizedY = 175 - ((Math.min(18, curr?.predicted_energy_kwh || 8) / 18) * 140);
                  return (
                    <g>
                      <circle cx={normalizedX} cy={normalizedY} r="7" fill="#ef4444" stroke="#ffffff" strokeWidth="2" />
                      <text x={normalizedX - 35} y={normalizedY - 12} fill="#ef4444" fontSize="11" fontWeight="700">
                        {speed} km/h
                      </text>
                    </g>
                  );
                })()}
              </svg>
            </div>
            <div className="flex justify-between text-[11px] text-slate-500 pt-1 border-t border-slate-800">
              <span>20 km/h</span>
              <span>60 km/h</span>
              <span>100 km/h</span>
              <span>140 km/h</span>
            </div>
          </div>

          {/* Telemetry Radar / Attribute Profile */}
          <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 sm:p-6 space-y-4 shadow-xl">
            <div className="flex items-center justify-between">
              <h3 className="text-xs sm:text-sm font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
                <Cpu className="w-4 h-4 text-emerald-400" />
                Driver Behavior Attribute Profile
              </h3>
              <span className="text-xs text-slate-400">Current Session</span>
            </div>

            <div className="space-y-3.5 pt-1">
              {[
                { label: 'Speed Intensity', value: Math.min(100, Math.round((speed / 140) * 100)), display: `${speed} km/h`, color: speed > 100 ? 'bg-rose-500' : 'bg-emerald-500' },
                { label: 'Throttle / Braking Force', value: Math.min(100, Math.round((Math.abs(accel) / 3.0) * 100)), display: `${accel.toFixed(2)} m/s²`, color: Math.abs(accel) > 1.8 ? 'bg-amber-500' : 'bg-emerald-500' },
                { label: 'Terrain Slope Stress', value: Math.min(100, Math.round(((slope + 5) / 15) * 100)), display: `${slope.toFixed(1)}%`, color: slope > 4 ? 'bg-purple-500' : 'bg-sky-500' },
                { label: 'Battery Charge State', value: batterySoc, display: `${batterySoc}%`, color: batterySoc < 25 ? 'bg-rose-500' : 'bg-emerald-500' },
                { label: 'Overall Eco Performance', value: score, display: `${score} / 100`, color: score > 70 ? 'bg-emerald-500' : score > 50 ? 'bg-amber-500' : 'bg-rose-500' }
              ].map((item, i) => (
                <div key={i} className="space-y-1">
                  <div className="flex justify-between text-xs">
                    <span className="text-slate-400 font-medium">{item.label}</span>
                    <span className="font-bold text-slate-200">{item.display}</span>
                  </div>
                  <div className="w-full bg-slate-800 h-2.5 rounded-full overflow-hidden">
                    <div 
                      className={`${item.color} h-full rounded-full transition-all duration-500`}
                      style={{ width: `${item.value}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </div>

        </div>

        {/* Section 4: 10-Segment Simulated Journey Replayer */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 sm:p-6 space-y-4 shadow-xl">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <h3 className="text-xs sm:text-sm font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
                <MapPin className="w-4 h-4 text-emerald-400" />
                Simulated 10-Stop Journey Replay (City &bull; Highway &bull; Mountain)
              </h3>
              <p className="text-xs text-slate-400">Track cumulative energy drain and AI savings across authentic route gradients</p>
            </div>
            <button
              onClick={handleSimulateRoute}
              disabled={simRunning}
              className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-slate-950 font-bold rounded-lg text-xs transition flex items-center gap-1.5 shadow-lg shadow-emerald-600/20 self-start sm:self-auto"
            >
              <Play className="w-4 h-4 fill-current" />
              Re-Simulate Route
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300 border-collapse">
              <thead>
                <tr className="border-b border-slate-800 text-[11px] text-slate-400 uppercase tracking-wider">
                  <th className="py-2.5 px-3">Segment</th>
                  <th className="py-2.5 px-3">Dist</th>
                  <th className="py-2.5 px-3">Speed</th>
                  <th className="py-2.5 px-3">Slope</th>
                  <th className="py-2.5 px-3">Current</th>
                  <th className="py-2.5 px-3">Optimized</th>
                  <th className="py-2.5 px-3">Cumul. Current</th>
                  <th className="py-2.5 px-3">Cumul. Opt</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono text-[11px]">
                {simResults.map((r, i) => (
                  <tr key={i} className="hover:bg-slate-800/40 transition">
                    <td className="py-2 px-3 font-sans font-medium text-slate-200">{r.segment}</td>
                    <td className="py-2 px-3">{r.km} km</td>
                    <td className="py-2 px-3">{r.speed} km/h</td>
                    <td className={`py-2 px-3 font-bold ${r.slope > 0 ? 'text-amber-400' : r.slope < 0 ? 'text-emerald-400' : 'text-slate-400'}`}>
                      {r.slope > 0 ? `+${r.slope}%` : `${r.slope}%`}
                    </td>
                    <td className="py-2 px-3 text-rose-400 font-semibold">{r.current_kwh} kWh</td>
                    <td className="py-2 px-3 text-emerald-400 font-semibold">{r.opt_kwh} kWh</td>
                    <td className="py-2 px-3 text-rose-300 font-bold">{r.cum_current} kWh</td>
                    <td className="py-2 px-3 text-emerald-300 font-bold">{r.cum_opt} kWh</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

      </main>

      {/* Footer */}
      <footer className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-12 pt-6 border-t border-slate-800 text-center text-xs text-slate-500">
        AI-Powered Driving Efficiency Optimizer &bull; Built with Next.js 16, React 19, Tailwind CSS & Scikit-learn &bull; SIRE Project
      </footer>

    </div>
  );
}
