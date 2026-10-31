import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    
    // Attempt proxying to Python FastAPI backend
    try {
      const backendRes = await fetch('http://127.0.0.1:8000/api/optimize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
        // Short timeout if backend is starting
        signal: AbortSignal.timeout(3000)
      });
      
      if (backendRes.ok) {
        const data = await backendRes.json();
        return NextResponse.json(data);
      }
    } catch {
      // Backend not running, proceed to client-side physics fallback
    }

    // Client-side fallback computation
    const speed = Number(body.Speed_kmh || 65);
    const accel = Number(body.Acceleration_ms2 || 0);
    const slope = Number(body.Slope_pct || body['Slope_%'] || 2.5);
    const dist = Number(body.Distance_Travelled_km || 25);
    const mode = Number(body.Driving_Mode || 2);
    const soc = Number(body.Battery_State_pct || body['Battery_State_%'] || 65);
    const tire = Number(body.Tire_Pressure_psi || 31.5);
    const temp = Number(body.Temperature_C || 20);

    // Approximate EV power consumption model (kWh)
    const baseKwhPerKm = 0.16 + (Math.max(0, speed - 70) ** 1.8) * 0.0018 + (slope > 0 ? slope * 0.012 : slope * 0.006) + (mode === 2 ? 0.03 : 0.0);
    const currentKwh = Math.max(0.5, Number((baseKwhPerKm * dist).toFixed(2)));
    const effKmKwh = Number((dist / currentKwh).toFixed(2));
    const whPerKm = Math.round((currentKwh * 1000) / dist);

    // Eco score
    const ecoScore = Math.max(10, Math.min(100, Math.round(100 - (whPerKm - 160) * 0.35)));

    // Optimized
    const optSpeed = speed > 90 ? 85 : (speed > 50 && body.Road_Type === 2 ? 45 : speed);
    const optKwhPerKm = 0.16 + (Math.max(0, optSpeed - 70) ** 1.8) * 0.0018 + (slope > 0 ? slope * 0.01 : slope * 0.006);
    const optKwh = Math.min(currentKwh, Math.max(0.4, Number((optKwhPerKm * dist).toFixed(2))));
    const savedKwh = Number((currentKwh - optKwh).toFixed(2));
    const savedPct = Number(((savedKwh / currentKwh) * 100).toFixed(1));
    const extraRange = Number((savedKwh / (currentKwh / dist)).toFixed(1));

    const tips = [];
    if (speed > 105) {
      tips.push({
        category: 'Speed Aerodynamics',
        severity: 'high',
        title: `Aerodynamic Drag Spike at ${speed} km/h`,
        description: 'Drag increases exponentially above 90 km/h. Cruising between 80-85 km/h drastically reduces continuous powertrain drain.',
        action: 'Lower speed to ~85 km/h with Adaptive Cruise Control.',
        potential_saving_kwh: Number((currentKwh * 0.18).toFixed(2))
      });
    }
    if (accel < -1.8) {
      tips.push({
        category: 'Regenerative Braking',
        severity: 'high',
        title: `Harsh Deceleration (${accel} m/s²)`,
        description: 'Hard braking triggers friction pads, turning kinetic energy into wasted rotor heat instead of electrical charge.',
        action: 'Anticipate stops earlier; use 1-pedal regenerative braking.',
        potential_saving_kwh: Number((currentKwh * 0.14).toFixed(2))
      });
    }
    if (mode === 2) {
      tips.push({
        category: 'Drive Mode',
        severity: 'medium',
        title: 'Sport Mode Active',
        description: 'Sport mode sharpens torque curves and reduces coasting regen drag, consuming ~12% more energy.',
        action: 'Switch to Eco or Comfort mode.',
        potential_saving_kwh: Number((currentKwh * 0.10).toFixed(2))
      });
    }
    if (slope > 4) {
      tips.push({
        category: 'Terrain Management',
        severity: 'medium',
        title: `Uphill Gradient (+${slope}%)`,
        description: 'Gravitational load increases battery C-rate draw. Avoid aggressive bursts on incline.',
        action: 'Maintain smooth momentum; prepare to regen on subsequent descent.',
        potential_saving_kwh: Number((currentKwh * 0.07).toFixed(2))
      });
    }
    if (tire < 30) {
      tips.push({
        category: 'Vehicle State',
        severity: 'medium',
        title: `Low Tire Pressure (${tire} psi)`,
        description: 'Underinflated tires increase rolling friction resistance by up to 10%.',
        action: 'Inflate to OEM recommended 33-35 psi.',
        potential_saving_kwh: Number((currentKwh * 0.04).toFixed(2))
      });
    }

    return NextResponse.json({
      current_profile: {
        predicted_energy_kwh: currentKwh,
        efficiency_km_per_kwh: effKmKwh,
        efficiency_wh_per_km: whPerKm,
        eco_score: ecoScore,
        cluster_name: speed > 85 ? 'Aggressive High-Speed' : (speed < 40 ? 'Urban Stop & Go' : 'Eco-Smooth Cruiser')
      },
      optimized_profile: {
        predicted_energy_kwh: optKwh,
        efficiency_km_per_kwh: Number((dist / optKwh).toFixed(2)),
        energy_saved_kwh: savedKwh,
        energy_saved_pct: savedPct,
        extra_range_km: extraRange
      },
      tips
    });
  } catch (err: unknown) {
    const errorMsg = err instanceof Error ? err.message : 'Unknown error';
    return NextResponse.json({ error: errorMsg }, { status: 500 });
  }
}

