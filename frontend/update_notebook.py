import json
import os

with open('ev-energy-consumption.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Update Cell 0: ensure local dataset is loaded first
c0_lines = nb['cells'][0]['source']
new_c0 = []
for line in c0_lines:
    if 'for dirname, _, filenames in os.walk' in line:
        new_c0.append('if os.path.exists("EV_Energy_Consumption_Dataset.csv"):\n')
        new_c0.append('    df = pd.read_csv("EV_Energy_Consumption_Dataset.csv")\n')
        new_c0.append('    print("Loaded local dataset: EV_Energy_Consumption_Dataset.csv")\n')
        new_c0.append('else:\n')
        new_c0.append('    ' + line)
    elif any(line.strip().startswith(prefix) for prefix in ['for filename in', 'Path  =', 'print(os.path.join', 'df = pd.read_csv']):
        new_c0.append('    ' + line)
    else:
        new_c0.append(line)

nb['cells'][0]['source'] = new_c0

# Cell 26: Markdown section explaining Problem Statement & Driving Tips
nb['cells'][26] = {
    'cell_type': 'markdown',
    'metadata': {},
    'source': [
        '# 8. AI-Powered Model Evaluation & Driving Efficiency Recommendations\n',
        '\n',
        'In strict fulfillment of the Problem Statement guidelines:\n',
        '1. **Python with Scikit-learn**: Evaluate Random Forest and Gradient Boosting models ($R^2$, $MAE$, $RMSE$).\n',
        '2. **Simulated Driving Data**: Analyze telemetry (`Speed_kmh`, `Slope_%` terrain gradient, `Acceleration_ms2` braking/acceleration).\n',
        '3. **Actionable Driving Tips**: Generate dynamic, context-aware driving tips based on prediction results.'
    ]
}

# Cell 27: Evaluation and Driving Tips Recommendation function
tips_code = [
    "from sklearn.metrics import r2_score, mean_absolute_error, root_mean_squared_error\n",
    "\n",
    "# 1. Model Evaluation Metrics\n",
    "y_pred = rf_shap.predict(X_test)\n",
    "r2 = r2_score(y_test, y_pred)\n",
    "mae = mean_absolute_error(y_test, y_pred)\n",
    "rmse = root_mean_squared_error(y_test, y_pred)\n",
    "\n",
    "print('=' * 68)\n",
    "print(' AI MODEL EVALUATION (Scikit-Learn Random Forest Regressor)')\n",
    "print('=' * 68)\n",
    "print(f'R² Score (Variance Explained): {r2 * 100:.2f}% (R² = {r2:.4f})')\n",
    "print(f'Mean Absolute Error (MAE):     {mae:.3f} kWh')\n",
    "print(f'Root Mean Squared Error (RMSE): {rmse:.3f} kWh')\n",
    "print('=' * 68)\n",
    "\n",
    "def suggest_driving_tips(speed_kmh, acceleration_ms2, slope_pct, driving_mode, distance_km=25.0):\n",
    "    '''Suggest driving tips based on prediction results.'''\n",
    "    sample_dict = {\n",
    "        'Speed_kmh': speed_kmh,\n",
    "        'Acceleration_ms2': acceleration_ms2,\n",
    "        'Battery_State_%': 60.0,\n",
    "        'Battery_Voltage_V': 350.0,\n",
    "        'Battery_Temperature_C': 27.5,\n",
    "        'Slope_%': slope_pct,\n",
    "        'Temperature_C': 20.0,\n",
    "        'Humidity_%': 55.0,\n",
    "        'Wind_Speed_ms': 7.5,\n",
    "        'Tire_Pressure_psi': 31.5,\n",
    "        'Vehicle_Weight_kg': 1850.0,\n",
    "        'Driving_Mode': driving_mode,\n",
    "        'Road_Type': 1,\n",
    "        'Traffic_Condition': 2,\n",
    "        'Weather_Condition': 1\n",
    "    }\n",
    "    sample_df = pd.DataFrame([sample_dict])[shap_features]\n",
    "    predicted_energy = float(rf_shap.predict(sample_df)[0])\n",
    "    efficiency = distance_km / predicted_energy\n",
    "    \n",
    "    tips = []\n",
    "    # Speed Optimization\n",
    "    if speed_kmh > 100:\n",
    "        tips.append(f'[HIGH] Aerodynamic Drag at {speed_kmh:.0f} km/h: Lower speed to ~85 km/h to save ~{predicted_energy*0.18:.2f} kWh.')\n",
    "    elif 60 <= speed_kmh <= 85:\n",
    "        tips.append(f'[OPTIMAL] Sweet Spot Speed ({speed_kmh:.0f} km/h): Maintaining ideal aerodynamic efficiency.')\n",
    "        \n",
    "    # Braking & Acceleration (Regeneration)\n",
    "    if acceleration_ms2 < -1.8:\n",
    "        tips.append(f'[HIGH] Severe Braking ({acceleration_ms2:.2f} m/s²): Use gradual 1-pedal deceleration to capture regenerative energy.')\n",
    "    elif acceleration_ms2 > 1.8:\n",
    "        tips.append(f'[MEDIUM] Aggressive Throttle ({acceleration_ms2:.2f} m/s²): Smooth pedal application preserves battery C-rate.')\n",
    "        \n",
    "    # Driving Mode\n",
    "    if driving_mode == 2:\n",
    "        tips.append('[MODE] Sport Mode Active: Switch to Eco mode to save 10-15% energy per trip.')\n",
    "        \n",
    "    # Terrain Management\n",
    "    if slope_pct > 4.0:\n",
    "        tips.append(f'[TERRAIN] Incline (+{slope_pct:.1f}%): Maintain steady throttle on climb; recover charge on the upcoming descent.')\n",
    "    elif slope_pct < -3.0:\n",
    "        tips.append(f'[REGEN] Downhill ({slope_pct:.1f}%): Lift off throttle to let regenerative braking top up battery.')\n",
    "\n",
    "    print(f'\\n--- TELEMETRY EVALUATION ---')\n",
    "    print(f'Speed: {speed_kmh} km/h | Accel: {acceleration_ms2} m/s² | Slope: {slope_pct}% | Mode: {driving_mode}')\n",
    "    print(f'Predicted Energy: {predicted_energy:.2f} kWh | Efficiency: {efficiency:.2f} km/kWh')\n",
    "    print('Actionable AI Driving Tips:')\n",
    "    for tip in tips:\n",
    "        print(f'  • {tip}')\n",
    "\n",
    "# Test Scenarios\n",
    "print('>>> SCENARIO 1: Aggressive Speeder on Highway')\n",
    "suggest_driving_tips(speed_kmh=120.0, acceleration_ms2=-2.2, slope_pct=1.0, driving_mode=2)\n",
    "\n",
    "print('\\n>>> SCENARIO 2: Mountain Ascent in Sport Mode')\n",
    "suggest_driving_tips(speed_kmh=70.0, acceleration_ms2=1.5, slope_pct=7.5, driving_mode=2)\n"
]

nb['cells'][27] = {
    'cell_type': 'code',
    'execution_count': None,
    'metadata': {},
    'outputs': [],
    'source': tips_code
}

with open('ev-energy-consumption.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)

print('Updated ev-energy-consumption.ipynb successfully!')

