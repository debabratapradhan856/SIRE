import os
import json
import joblib
import numpy as np
import pandas as pd

class DrivingEfficiencyOptimizer:
    def __init__(self, models_dir='models'):
        self.models_dir = models_dir
        self.model = joblib.load(os.path.join(models_dir, 'energy_model.joblib'))
        self.cluster_scaler = joblib.load(os.path.join(models_dir, 'cluster_scaler.joblib'))
        self.cluster_kmeans = joblib.load(os.path.join(models_dir, 'cluster_kmeans.joblib'))
        with open(os.path.join(models_dir, 'metadata.json'), 'r') as f:
            self.metadata = json.load(f)
            
        self.feature_cols = self.metadata['feature_cols']
        self.cluster_profiles = self.metadata['cluster_profiles']
        self.dataset_stats = self.metadata['dataset_stats']

    def predict_energy(self, input_dict):
        """Run ML prediction on input dictionary."""
        # Ensure all columns exist
        df_row = pd.DataFrame([{col: input_dict.get(col, 0.0) for col in self.feature_cols}])
        pred = float(self.model.predict(df_row)[0])
        return max(0.2, round(pred, 3))

    def identify_cluster(self, speed, acceleration, slope, energy):
        """Identify driver behavior cluster."""
        cluster_df = pd.DataFrame([{
            'Speed_kmh': speed,
            'Acceleration_ms2': acceleration,
            'Slope_%': slope,
            'Energy_Consumption_kWh': energy
        }])
        scaled = self.cluster_scaler.transform(cluster_df)
        c_id = int(self.cluster_kmeans.predict(scaled)[0])
        profile = self.cluster_profiles.get(str(c_id), {
            "name": "General Driver",
            "avg_speed": speed,
            "avg_energy": energy
        })
        return c_id, profile

    def analyze_and_optimize(self, inputs):
        """
        Analyze current driving state, predict energy consumption,
        compute optimized parameters, and generate targeted tips.
        """
        speed = float(inputs.get('Speed_kmh', 60.0))
        accel = float(inputs.get('Acceleration_ms2', 0.0))
        slope = float(inputs.get('Slope_%', 0.0))
        dist = float(inputs.get('Distance_Travelled_km', 25.0))
        mode = int(inputs.get('Driving_Mode', 2)) # 1: Eco, 2: Sport, 3: Comfort
        road = int(inputs.get('Road_Type', 1)) # 1: Highway, 2: Urban, 3: Rural
        traffic = int(inputs.get('Traffic_Condition', 2)) # 1: Low, 2: Med, 3: High
        battery_soc = float(inputs.get('Battery_State_%', 60.0))
        tire_psi = float(inputs.get('Tire_Pressure_psi', 31.5))
        temp_c = float(inputs.get('Temperature_C', 20.0))
        weight_kg = float(inputs.get('Vehicle_Weight_kg', 1800.0))
        wind_ms = float(inputs.get('Wind_Speed_ms', 5.0))
        humidity = float(inputs.get('Humidity_%', 50.0))
        batt_temp = float(inputs.get('Battery_Temperature_C', 28.0))
        batt_volt = float(inputs.get('Battery_Voltage_V', 350.0))
        weather = int(inputs.get('Weather_Condition', 1)) # 1: Clear, 2: Rain, 3: Snow, 4: Fog

        # 1. Base Prediction
        base_inputs = {
            'Speed_kmh': speed,
            'Acceleration_ms2': accel,
            'Battery_State_%': battery_soc,
            'Battery_Voltage_V': batt_volt,
            'Battery_Temperature_C': batt_temp,
            'Driving_Mode': mode,
            'Road_Type': road,
            'Traffic_Condition': traffic,
            'Slope_%': slope,
            'Weather_Condition': weather,
            'Temperature_C': temp_c,
            'Humidity_%': humidity,
            'Wind_Speed_ms': wind_ms,
            'Tire_Pressure_psi': tire_psi,
            'Vehicle_Weight_kg': weight_kg,
            'Distance_Travelled_km': dist
        }
        pred_energy = self.predict_energy(base_inputs)

        # Efficiency metrics
        eff_km_kwh = round(dist / pred_energy, 2) if pred_energy > 0 else 0.0
        eff_wh_km = round((pred_energy * 1000.0) / dist, 1) if dist > 0 else 0.0

        # Cluster Identification
        c_id, cluster_info = self.identify_cluster(speed, accel, slope, pred_energy)

        # Eco-Score computation (0 to 100)
        # Optimal benchmark energy for this distance is around dist * 0.18 kWh (5.5 km/kWh)
        baseline_wh_km = 160.0 # ideal EV rating ~160 Wh/km
        raw_score = 100.0 - ((eff_wh_km - baseline_wh_km) / baseline_wh_km) * 60.0
        eco_score = max(10, min(100, round(raw_score, 1)))

        # 2. Compute AI Optimized Driving Profile
        opt_speed = speed
        opt_accel = accel
        opt_mode = mode
        opt_tire_psi = tire_psi

        # Optimize speed based on road type
        if road == 1 and speed > 90.0:  # Highway: aerodynamic drag spikes quadratically
            opt_speed = 85.0
        elif road == 2 and speed > 50.0: # Urban
            opt_speed = 45.0
        elif road == 3 and speed > 70.0: # Rural
            opt_speed = 60.0

        # Optimize acceleration / braking
        if accel > 1.2:  # aggressive acceleration
            opt_accel = 0.5
        elif accel < -1.5:  # hard mechanical braking instead of smooth regen
            opt_accel = -0.7

        # Optimize driving mode: Switch to Eco (1)
        if mode != 1:
            opt_mode = 1

        # Optimize tire pressure
        if tire_psi < 33.0:
            opt_tire_psi = 34.0

        opt_inputs = base_inputs.copy()
        opt_inputs['Speed_kmh'] = opt_speed
        opt_inputs['Acceleration_ms2'] = opt_accel
        opt_inputs['Driving_Mode'] = opt_mode
        opt_inputs['Tire_Pressure_psi'] = opt_tire_psi

        opt_energy = self.predict_energy(opt_inputs)
        # Ensure optimized is at least slightly better or equal
        opt_energy = min(pred_energy, opt_energy)

        energy_saved_kwh = max(0.0, round(pred_energy - opt_energy, 2))
        energy_saved_pct = round((energy_saved_kwh / pred_energy) * 100.0, 1) if pred_energy > 0 else 0.0
        extra_range_km = round((energy_saved_kwh / (pred_energy / dist)), 1) if pred_energy > 0 else 0.0

        opt_eff_km_kwh = round(dist / opt_energy, 2) if opt_energy > 0 else eff_km_kwh

        # 3. Dynamic Driving Tips Engine
        tips = []

        # A. Speed Analysis & Tip
        if speed > 105.0:
            tips.append({
                "category": "Speed Optimization",
                "severity": "high",
                "icon": "zap-off",
                "title": f"High Aerodynamic Drag at {speed:.0f} km/h",
                "description": f"Aerodynamic drag increases quadratically with speed above 90 km/h. Cruising at 85-90 km/h reduces energy drain by up to 25% on highways.",
                "action": "Lower cruising speed to ~85 km/h using Cruise Control.",
                "potential_saving_kwh": round(pred_energy * 0.18, 2)
            })
        elif speed > 80.0 and road == 2:
            tips.append({
                "category": "Speed Optimization",
                "severity": "high",
                "icon": "alert-triangle",
                "title": f"Excessive Speed ({speed:.0f} km/h) for Urban Zone",
                "description": "High city speeds lead to frequent harsh braking at signals and intersections, squandering battery charge.",
                "action": "Cap urban speed at 40-50 km/h for smoother traffic flow.",
                "potential_saving_kwh": round(pred_energy * 0.15, 2)
            })
        elif 50.0 <= speed <= 80.0:
            tips.append({
                "category": "Speed Optimization",
                "severity": "success",
                "icon": "check-circle",
                "title": f"Optimal Speed Window ({speed:.0f} km/h)",
                "description": "Vehicle is cruising within the sweet spot for EV powertrain efficiency and minimal wind resistance.",
                "action": "Maintain steady throttle to sustain current efficiency.",
                "potential_saving_kwh": 0.0
            })

        # B. Braking & Acceleration (Regenerative Braking)
        if accel < -1.8:
            tips.append({
                "category": "Regenerative Braking",
                "severity": "high",
                "icon": "battery-charging",
                "title": f"Severe Friction Braking ({accel:.2f} m/s²)",
                "description": "Hard braking activates hydraulic friction brakes, turning kinetic energy into wasted rotor heat instead of electrical charge.",
                "action": "Anticipate stops 50m earlier; use gentle 1-pedal deceleration to capture up to 90% regen energy.",
                "potential_saving_kwh": round(pred_energy * 0.12, 2)
            })
        elif accel < -0.8:
            tips.append({
                "category": "Regenerative Braking",
                "severity": "medium",
                "icon": "battery-charging",
                "title": "Moderate Braking Event",
                "description": "Smooth regenerative braking is engaged. To maximize recuperation, maintain progressive deceleration.",
                "action": "Avoid sudden pedal presses.",
                "potential_saving_kwh": round(pred_energy * 0.05, 2)
            })
        elif accel > 1.8:
            tips.append({
                "category": "Acceleration Dynamics",
                "severity": "high",
                "icon": "trending-up",
                "title": f"Aggressive Acceleration Surge ({accel:.2f} m/s²)",
                "description": "Sudden torque spikes draw heavy C-rate discharge current from the battery, triggering I²R thermal losses.",
                "action": "Adopt progressive, linear accelerator pedal input.",
                "potential_saving_kwh": round(pred_energy * 0.10, 2)
            })
        elif 0.0 <= accel <= 0.8:
            tips.append({
                "category": "Acceleration Dynamics",
                "severity": "success",
                "icon": "check-circle",
                "title": "Smooth Torque Application",
                "description": "Gentle acceleration profile preserves battery chemistry and avoids wasteful peak draw.",
                "action": "Keep throttle modulation linear.",
                "potential_saving_kwh": 0.0
            })

        # C. Driving Mode
        mode_names = {1: 'Eco', 2: 'Sport', 3: 'Comfort'}
        if mode == 2: # Sport
            tips.append({
                "category": "Drive Mode Management",
                "severity": "medium",
                "icon": "sliders",
                "title": "Sport Mode Active",
                "description": "Sport mode sharpens throttle mapping and reduces regen drag, typically consuming 12-18% more energy per trip.",
                "action": "Toggle to 'Eco' or 'Comfort' mode unless aggressive overtaking is necessary.",
                "potential_saving_kwh": round(pred_energy * 0.08, 2)
            })
        elif mode == 1:
            tips.append({
                "category": "Drive Mode Management",
                "severity": "success",
                "icon": "shield-check",
                "title": "Eco Mode Active",
                "description": "Eco mode limits aggressive power draw and dampens HVAC peak consumption.",
                "action": "Keep Eco mode enabled throughout the route.",
                "potential_saving_kwh": 0.0
            })

        # D. Terrain & Gradient
        if slope > 4.0:
            tips.append({
                "category": "Terrain Management",
                "severity": "medium",
                "icon": "mountain",
                "title": f"Steep Incline (+{slope:.1f}% Slope)",
                "description": f"Vehicle is climbing against gravitational load. Climbing at high speed causes massive battery discharge.",
                "action": "Slightly ease vehicle speed on the ascent; recover gravitational potential on the subsequent downhill slope.",
                "potential_saving_kwh": round(pred_energy * 0.07, 2)
            })
        elif slope < -3.0:
            tips.append({
                "category": "Terrain Management",
                "severity": "success",
                "icon": "arrow-down-right",
                "title": f"Downhill Grade ({slope:.1f}% Slope)",
                "description": "Gravity provides propulsion. Set regenerative braking to Level 2 or 3 to passively top up the high-voltage pack.",
                "action": "Lift off accelerator completely to allow regenerative charging.",
                "potential_saving_kwh": round(pred_energy * 0.09, 2)
            })

        # E. Tire Pressure & Climate
        if tire_psi < 30.0:
            tips.append({
                "category": "Vehicle Pre-Conditioning",
                "severity": "medium",
                "icon": "disc",
                "title": f"Low Tire Pressure ({tire_psi:.1f} psi)",
                "description": "Underinflated tires increase rolling contact resistance by up to 10%, causing higher continuous rolling resistance.",
                "action": "Inflate tires to OEM specification (33-35 psi) at the next stop.",
                "potential_saving_kwh": round(pred_energy * 0.04, 2)
            })

        if temp_c < 5.0:
            tips.append({
                "category": "Thermal & Climate",
                "severity": "medium",
                "icon": "thermometer-snowflake",
                "title": f"Cold Ambient Temperature ({temp_c:.1f}°C)",
                "description": "Cold ambient temperature lowers electrolyte mobility in lithium-ion cells and demands cabin heating.",
                "action": "Pre-condition cabin while plugged in and rely on seat warmers rather than high cabin blower heating.",
                "potential_saving_kwh": round(pred_energy * 0.06, 2)
            })
        elif temp_c > 35.0:
            tips.append({
                "category": "Thermal & Climate",
                "severity": "info",
                "icon": "sun",
                "title": f"High Ambient Temperature ({temp_c:.1f}°C)",
                "description": "High heat activates active battery cooling chiller pumps and AC compressor.",
                "action": "Park in shaded areas when possible and pre-cool the cabin while connected to a charger.",
                "potential_saving_kwh": round(pred_energy * 0.03, 2)
            })

        return {
            "current_profile": {
                "inputs": base_inputs,
                "predicted_energy_kwh": pred_energy,
                "efficiency_km_per_kwh": eff_km_kwh,
                "efficiency_wh_per_km": eff_wh_km,
                "eco_score": eco_score,
                "cluster_id": c_id,
                "cluster_name": cluster_info["name"]
            },
            "optimized_profile": {
                "inputs": opt_inputs,
                "predicted_energy_kwh": opt_energy,
                "efficiency_km_per_kwh": opt_eff_km_kwh,
                "efficiency_wh_per_km": round((opt_energy * 1000.0) / dist, 1) if dist > 0 else 0.0,
                "energy_saved_kwh": energy_saved_kwh,
                "energy_saved_pct": energy_saved_pct,
                "extra_range_km": extra_range_km
            },
            "tips": tips,
            "feature_importances": self.metadata["feature_importances"],
            "cluster_profiles": self.cluster_profiles,
            "dataset_stats": self.dataset_stats
        }

if __name__ == '__main__':
    optimizer = DrivingEfficiencyOptimizer()
    sample = {
        'Speed_kmh': 110.0,
        'Acceleration_ms2': -2.4, # harsh braking
        'Slope_%': 5.0, # uphill
        'Distance_Travelled_km': 30.0,
        'Driving_Mode': 2, # sport
        'Road_Type': 1,
        'Traffic_Condition': 2,
        'Battery_State_%': 45.0,
        'Tire_Pressure_psi': 29.0,
        'Temperature_C': 2.0
    }
    res = optimizer.analyze_and_optimize(sample)
    print("=== CURRENT PROFILE ===")
    print(f"Energy: {res['current_profile']['predicted_energy_kwh']} kWh | Eco Score: {res['current_profile']['eco_score']}/100 | Cluster: {res['current_profile']['cluster_name']}")
    print("=== OPTIMIZED PROFILE ===")
    print(f"Optimized Energy: {res['optimized_profile']['predicted_energy_kwh']} kWh | Saved: {res['optimized_profile']['energy_saved_kwh']} kWh ({res['optimized_profile']['energy_saved_pct']}%) | Extra Range: +{res['optimized_profile']['extra_range_km']} km")
    print(f"\nGenerated {len(res['tips'])} Driving Tips:")
    for t in res['tips']:
        print(f"[{t['severity'].upper()}] {t['title']} -> {t['action']}")
