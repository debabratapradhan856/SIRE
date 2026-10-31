import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from optimizer import DrivingEfficiencyOptimizer

# Page configuration
st.set_page_config(
    page_title="AI-Powered Driving Efficiency Optimizer",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #10b981, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        color: #64748b;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }
    .metric-box {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .metric-val {
        font-size: 1.9rem;
        font-weight: 700;
        color: #0f172a;
    }
    .metric-lbl {
        font-size: 0.85rem;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .tip-card-high {
        border-left: 5px solid #ef4444;
        background-color: #fef2f2;
        padding: 1rem 1.2rem;
        border-radius: 8px;
        margin-bottom: 0.8rem;
    }
    .tip-card-medium {
        border-left: 5px solid #f59e0b;
        background-color: #fffbeb;
        padding: 1rem 1.2rem;
        border-radius: 8px;
        margin-bottom: 0.8rem;
    }
    .tip-card-success {
        border-left: 5px solid #10b981;
        background-color: #f0fdf4;
        padding: 1rem 1.2rem;
        border-radius: 8px;
        margin-bottom: 0.8rem;
    }
    .tip-card-info {
        border-left: 5px solid #3b82f6;
        background-color: #eff6ff;
        padding: 1rem 1.2rem;
        border-radius: 8px;
        margin-bottom: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# Load Optimizer
@st.cache_resource
def load_optimizer():
    return DrivingEfficiencyOptimizer()

optimizer = load_optimizer()

# Header
st.markdown('<div class="main-title">⚡ AI-Powered Driving Efficiency Optimizer</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Intelligent EV Telematics Analysis, Predictive Energy Modeling & Dynamic Driving Recommendations</div>', unsafe_allow_html=True)

# Preset Scenarios
preset_options = {
    "Custom / Manual": None,
    "🏎️ Aggressive Highway Speeder": {
        "speed": 125.0, "accel": 2.2, "slope": 1.0, "mode": 2, "road": 1,
        "dist": 40.0, "battery": 75.0, "traffic": 1, "temp": 22.0, "tire": 31.0
    },
    "🏙️ Urban Stop-and-Go Commute": {
        "speed": 45.0, "accel": -2.5, "slope": 0.5, "mode": 3, "road": 2,
        "dist": 15.0, "battery": 50.0, "traffic": 3, "temp": 28.0, "tire": 30.0
    },
    "⛰️ Steep Mountain Ascent": {
        "speed": 65.0, "accel": 1.4, "slope": 8.5, "mode": 2, "road": 3,
        "dist": 25.0, "battery": 60.0, "traffic": 1, "temp": 8.0, "tire": 32.0
    },
    "🌱 Optimal Eco-Cruiser": {
        "speed": 75.0, "accel": 0.3, "slope": 0.0, "mode": 1, "road": 1,
        "dist": 35.0, "battery": 85.0, "traffic": 1, "temp": 21.0, "tire": 34.0
    }
}

# Sidebar Controls
st.sidebar.header("🕹️ Telemetry Controls & Inputs")
selected_preset = st.sidebar.selectbox("Quick Preset Scenario", list(preset_options.keys()))
preset_data = preset_options[selected_preset]

with st.sidebar.expander("🚗 Driving Behavior", expanded=True):
    speed = st.slider("Speed (km/h)", 0.0, 160.0, float(preset_data["speed"]) if preset_data else 65.0, 1.0)
    accel = st.slider(
        "Acceleration / Braking (m/s²)", -3.0, 3.0,
        float(preset_data["accel"]) if preset_data else -0.2, 0.1,
        help="Negative indicates deceleration / braking; Positive indicates throttle acceleration."
    )
    mode_label = st.radio(
        "Driving Mode", ["Eco", "Sport", "Comfort"],
        index=(preset_data["mode"] - 1) if preset_data else 1,
        horizontal=True
    )
    mode_map = {"Eco": 1, "Sport": 2, "Comfort": 3}
    driving_mode = mode_map[mode_label]

with st.sidebar.expander("🛣️ Route & Terrain", expanded=True):
    slope = st.slider(
        "Terrain Gradient / Slope (%)", -5.0, 10.0,
        float(preset_data["slope"]) if preset_data else 2.5, 0.5,
        help="Negative = Downhill (Regen potential), Positive = Uphill climb"
    )
    road_label = st.selectbox(
        "Road Type", ["Highway", "Urban", "Rural"],
        index=(preset_data["road"] - 1) if preset_data else 0
    )
    road_map = {"Highway": 1, "Urban": 2, "Rural": 3}
    road_type = road_map[road_label]

    distance = st.slider("Trip Distance (km)", 1.0, 100.0, float(preset_data["dist"]) if preset_data else 25.0, 1.0)
    
    traffic_label = st.select_slider(
        "Traffic Density", ["Low", "Medium", "High"],
        value=["Low", "Medium", "High"][(preset_data["traffic"] - 1) if preset_data else 1]
    )
    traffic_map = {"Low": 1, "Medium": 2, "High": 3}
    traffic_condition = traffic_map[traffic_label]

with st.sidebar.expander("🔋 Vehicle & Environmental State", expanded=False):
    battery_soc = st.slider("Battery State of Charge (%)", 10.0, 100.0, float(preset_data["battery"]) if preset_data else 65.0, 1.0)
    tire_psi = st.slider("Tire Pressure (psi)", 26.0, 38.0, float(preset_data["tire"]) if preset_data else 31.5, 0.5)
    temp_c = st.slider("Ambient Temperature (°C)", -5.0, 42.0, float(preset_data["temp"]) if preset_data else 20.0, 1.0)
    vehicle_weight = st.number_input("Vehicle Weight (kg)", 1200, 2500, 1850, 50)
    weather_label = st.selectbox("Weather Condition", ["Clear", "Rain", "Snow", "Fog"])
    weather_map = {"Clear": 1, "Rain": 2, "Snow": 3, "Fog": 4}
    weather_cond = weather_map[weather_label]
    wind_speed = st.slider("Wind Speed (m/s)", 0.0, 18.0, 6.0, 0.5)

# Build Input Dictionary
input_payload = {
    'Speed_kmh': speed,
    'Acceleration_ms2': accel,
    'Battery_State_%': battery_soc,
    'Battery_Voltage_V': 320.0 + (battery_soc * 0.8),
    'Battery_Temperature_C': max(15.0, min(42.0, temp_c + 8.0)),
    'Driving_Mode': driving_mode,
    'Road_Type': road_type,
    'Traffic_Condition': traffic_condition,
    'Slope_%': slope,
    'Weather_Condition': weather_cond,
    'Temperature_C': temp_c,
    'Humidity_%': 55.0,
    'Wind_Speed_ms': wind_speed,
    'Tire_Pressure_psi': tire_psi,
    'Vehicle_Weight_kg': vehicle_weight,
    'Distance_Travelled_km': distance
}

# Run Optimizer & Prediction
results = optimizer.analyze_and_optimize(input_payload)
curr = results["current_profile"]
opt = results["optimized_profile"]
tips = results["tips"]

# Determine Score Color & Grade
score = curr["eco_score"]
if score >= 85:
    grade, grade_color = "A+ (Excellent)", "#10b981"
elif score >= 70:
    grade, grade_color = "B (Good)", "#3b82f6"
elif score >= 50:
    grade, grade_color = "C (Average)", "#f59e0b"
else:
    grade, grade_color = "D / F (Inefficient)", "#ef4444"

# 1. KPI Cards Row
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-lbl">Predicted Energy</div>
        <div class="metric-val">{curr['predicted_energy_kwh']:.2f} <span style="font-size: 1rem; color: #64748b;">kWh</span></div>
        <div style="font-size: 0.85rem; color: #64748b; margin-top: 4px;">For {distance:.0f} km trip</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-lbl">Trip Efficiency</div>
        <div class="metric-val">{curr['efficiency_km_per_kwh']:.2f} <span style="font-size: 1rem; color: #64748b;">km/kWh</span></div>
        <div style="font-size: 0.85rem; color: #64748b; margin-top: 4px;">{curr['efficiency_wh_per_km']:.0f} Wh/km</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-lbl">Eco-Score</div>
        <div class="metric-val" style="color: {grade_color};">{score:.0f} <span style="font-size: 1rem; color: #64748b;">/ 100</span></div>
        <div style="font-size: 0.85rem; font-weight: 600; color: {grade_color}; margin-top: 4px;">{grade}</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-lbl">Driving Behavior Profile</div>
        <div class="metric-val" style="font-size: 1.3rem; margin-top: 6px;">{curr['cluster_name']}</div>
        <div style="font-size: 0.85rem; color: #64748b; margin-top: 6px;">K-Means ML Cluster #{curr['cluster_id']}</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# 2. AI Optimization & Energy Savings Comparison
st.subheader("💡 AI Energy Optimization & Potential Savings")

opt_c1, opt_c2 = st.columns([1.5, 1])

with opt_c1:
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #0f172a, #1e293b); color: white; padding: 1.5rem; border-radius: 12px; margin-bottom: 1rem;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h4 style="margin: 0; color: #38bdf8;">AI Optimization Impact</h4>
                <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 0.95rem;">By applying the recommended driving adjustments:</p>
            </div>
            <div style="background: rgba(16, 185, 129, 0.2); border: 1px solid #10b981; padding: 6px 14px; border-radius: 20px; color: #34d399; font-weight: 700;">
                +{opt['extra_range_km']:.1f} km Extra Range
            </div>
        </div>
        <hr style="border-color: #334155; margin: 1rem 0;">
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; text-align: center;">
            <div>
                <div style="color: #94a3b8; font-size: 0.85rem;">ENERGY SAVED</div>
                <div style="font-size: 1.6rem; font-weight: 700; color: #34d399;">{opt['energy_saved_kwh']:.2f} kWh</div>
            </div>
            <div>
                <div style="color: #94a3b8; font-size: 0.85rem;">CONSUMPTION CUT</div>
                <div style="font-size: 1.6rem; font-weight: 700; color: #38bdf8;">{opt['energy_saved_pct']:.1f}%</div>
            </div>
            <div>
                <div style="color: #94a3b8; font-size: 0.85rem;">OPTIMIZED EFFICIENCY</div>
                <div style="font-size: 1.6rem; font-weight: 700; color: #f59e0b;">{opt['efficiency_km_per_kwh']:.2f} km/kWh</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with opt_c2:
    # Comparison Bar Chart
    comp_df = pd.DataFrame({
        "Profile": ["Current Driving", "AI Optimized"],
        "Energy (kWh)": [curr['predicted_energy_kwh'], opt['predicted_energy_kwh']],
        "Color": ["#ef4444", "#10b981"]
    })
    fig_comp = px.bar(
        comp_df, x="Profile", y="Energy (kWh)", color="Profile",
        color_discrete_map={"Current Driving": "#f43f5e", "AI Optimized": "#10b981"},
        text_auto=".2f", height=230
    )
    fig_comp.update_layout(
        showlegend=False,
        margin=dict(l=10, r=10, t=10, b=10),
        yaxis_title="Energy (kWh)",
        xaxis_title=""
    )
    st.plotly_chart(fig_comp, use_container_width=True)

# 3. Dynamic Driving Tips Section (Problem Statement Core Requirement)
st.subheader("🎯 Actionable Driving Tips Based on Prediction Results")

if not tips:
    st.info("Driving parameters are fully optimized! No immediate corrective actions needed.")
else:
    tip_col1, tip_col2 = st.columns(2)
    for i, tip in enumerate(tips):
        target_col = tip_col1 if i % 2 == 0 else tip_col2
        sev_class = f"tip-card-{tip['severity']}"
        badge_text = tip['severity'].upper()
        
        with target_col:
            st.markdown(f"""
            <div class="{sev_class}">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <span style="font-weight: 700; font-size: 1.05rem; color: #0f172a;">{tip['title']}</span>
                    <span style="font-size: 0.75rem; font-weight: 700; padding: 2px 8px; border-radius: 4px; background: white; border: 1px solid rgba(0,0,0,0.1);">{tip['category']}</span>
                </div>
                <p style="margin: 0 0 8px 0; color: #334155; font-size: 0.92rem; line-height: 1.4;">{tip['description']}</p>
                <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.88rem;">
                    <span style="color: #0f172a; font-weight: 600;">👉 Action: {tip['action']}</span>
                    {f'<span style="color: #10b981; font-weight: 700;">Save ~{tip["potential_saving_kwh"]} kWh</span>' if tip['potential_saving_kwh'] > 0 else ''}
                </div>
            </div>
            """, unsafe_allow_html=True)

st.write("")

# 4. Analytics & Telemetry Deep Dive
st.subheader("📊 Telemetry & Model Analysis")

tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Speed vs Energy Consumption Curve",
    "🕸️ Telemetry Radar Profile",
    "🔍 AI Model Explainability (Feature Importance)",
    "👥 Driving Behavior Cluster Profiles"
])

with tab1:
    # Speed Curve
    speeds_sweep = np.linspace(20, 140, 25)
    curve_rows = []
    for sp in speeds_sweep:
        row = input_payload.copy()
        row['Speed_kmh'] = sp
        e = optimizer.predict_energy(row)
        curve_rows.append({"Speed (km/h)": sp, "Energy (kWh)": e})
    curve_df = pd.DataFrame(curve_rows)

    fig_curve = px.line(
        curve_df, x="Speed (km/h)", y="Energy (kWh)",
        title="EV Energy Consumption vs. Speed Curve (Current Highway/Road Condition)",
        markers=True
    )
    # Highlight current operating point
    fig_curve.add_scatter(
        x=[speed], y=[curr['predicted_energy_kwh']],
        mode="markers", marker=dict(size=14, color="red", symbol="diamond"),
        name="Current Operating Point"
    )
    # Highlight sweet spot (60-80 km/h)
    fig_curve.add_vrect(
        x0=60, x1=80, fillcolor="rgba(16, 185, 129, 0.15)",
        layer="below", line_width=0, annotation_text="Optimal Aero Zone (60-80 km/h)"
    )
    fig_curve.update_layout(height=380, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig_curve, use_container_width=True)

with tab2:
    # Radar Chart
    categories = ['Speed Index', 'Throttle Intensity', 'Terrain Gradient', 'Eco-Score', 'Battery State']
    
    # Normalize features to 0-100 scale for clean radar
    norm_speed = min(100, (speed / 140.0) * 100)
    norm_accel = min(100, (abs(accel) / 3.0) * 100)
    norm_slope = min(100, ((slope + 5.0) / 15.0) * 100)
    norm_score = score
    norm_soc = battery_soc

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=[norm_speed, norm_accel, norm_slope, norm_score, norm_soc],
        theta=categories,
        fill='toself',
        fillcolor='rgba(59, 130, 246, 0.25)',
        line=dict(color='#3b82f6', width=2),
        name='Current Driving Profile'
    ))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=False,
        height=380,
        margin=dict(l=30, r=30, t=30, b=30)
    )
    st.plotly_chart(fig_radar, use_container_width=True)

with tab3:
    # Feature Importances
    fi_list = optimizer.metadata["feature_importances"]
    fi_df = pd.DataFrame(fi_list).head(10)
    fig_fi = px.bar(
        fi_df[::-1], x="importance", y="feature", orientation="h",
        title="Top 10 Factors Influencing EV Energy Consumption (Gradient Boosting Model)",
        color="importance", color_continuous_scale="Viridis", text_auto=".3f"
    )
    fig_fi.update_layout(height=380, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig_fi, use_container_width=True)

with tab4:
    # Cluster Profiles
    clusters_data = []
    for cid, cinfo in optimizer.cluster_profiles.items():
        clusters_data.append({
            "Cluster ID": cid,
            "Driving Style": cinfo["name"],
            "Dataset Share": f"{cinfo['pct']}%",
            "Avg Speed (km/h)": cinfo["avg_speed"],
            "Avg Energy (kWh)": cinfo["avg_energy"],
            "Avg Slope (%)": cinfo["avg_slope"]
        })
    c_df = pd.DataFrame(clusters_data)
    st.dataframe(c_df, use_container_width=True, hide_index=True)

st.write("---")

# 5. Route Simulation Replay
with st.expander("🗺️ Interactive Route Simulator (10-Stop Segment Replay)", expanded=False):
    st.markdown("Simulate an authentic trip with changing terrain gradients, city stop-and-go segments, and highway sections to see real-time energy prediction:")
    
    route_segments = [
        {"segment": "1. City Center Start", "km": 3.0, "speed": 35.0, "accel": 0.8, "slope": 0.0, "road": 2},
        {"segment": "2. Signal Congestion", "km": 2.0, "speed": 22.0, "accel": -2.2, "slope": 0.5, "road": 2},
        {"segment": "3. Ring Road Merge", "km": 5.0, "speed": 60.0, "accel": 1.2, "slope": 1.0, "road": 1},
        {"segment": "4. Highway Cruising A", "km": 10.0, "speed": 95.0, "accel": 0.1, "slope": 0.0, "road": 1},
        {"segment": "5. High-Speed Highway", "km": 12.0, "speed": 120.0, "accel": 0.4, "slope": -0.5, "road": 1},
        {"segment": "6. Foothills Ascent", "km": 6.0, "speed": 70.0, "accel": 1.5, "slope": 6.5, "road": 3},
        {"segment": "7. Steep Mountain Pass", "km": 4.0, "speed": 50.0, "accel": 0.8, "slope": 9.0, "road": 3},
        {"segment": "8. Mountain Descent", "km": 5.0, "speed": 55.0, "accel": -1.2, "slope": -4.5, "road": 3},
        {"segment": "9. Suburban Access", "km": 4.0, "speed": 50.0, "accel": -0.4, "slope": 0.0, "road": 2},
        {"segment": "10. Destination Arrival", "km": 2.0, "speed": 30.0, "accel": -0.6, "slope": 0.0, "road": 2}
    ]

    sim_results = []
    cum_km = 0.0
    cum_energy = 0.0
    cum_opt_energy = 0.0

    for seg in route_segments:
        s_input = input_payload.copy()
        s_input['Distance_Travelled_km'] = seg['km']
        s_input['Speed_kmh'] = seg['speed']
        s_input['Acceleration_ms2'] = seg['accel']
        s_input['Slope_%'] = seg['slope']
        s_input['Road_Type'] = seg['road']

        res = optimizer.analyze_and_optimize(s_input)
        cum_km += seg['km']
        cum_energy += res['current_profile']['predicted_energy_kwh']
        cum_opt_energy += res['optimized_profile']['predicted_energy_kwh']

        sim_results.append({
            "Segment": seg['segment'],
            "Distance (km)": seg['km'],
            "Speed (km/h)": seg['speed'],
            "Slope (%)": seg['slope'],
            "Current Energy (kWh)": res['current_profile']['predicted_energy_kwh'],
            "AI-Optimized (kWh)": res['optimized_profile']['predicted_energy_kwh'],
            "Cumulative Distance": cum_km,
            "Cumulative Current (kWh)": round(cum_energy, 2),
            "Cumulative Optimized (kWh)": round(cum_opt_energy, 2)
        })

    sim_df = pd.DataFrame(sim_results)

    sim_c1, sim_c2 = st.columns([1.6, 1])
    with sim_c1:
        fig_sim = go.Figure()
        fig_sim.add_trace(go.Scatter(
            x=sim_df["Cumulative Distance"], y=sim_df["Cumulative Current (kWh)"],
            mode="lines+markers", name="Standard Driving", line=dict(color="#ef4444", width=3)
        ))
        fig_sim.add_trace(go.Scatter(
            x=sim_df["Cumulative Distance"], y=sim_df["Cumulative Optimized (kWh)"],
            mode="lines+markers", name="AI-Optimized Driving", line=dict(color="#10b981", width=3)
        ))
        fig_sim.update_layout(
            title=f"Cumulative Energy: Saved {cum_energy - cum_opt_energy:.2f} kWh over {cum_km:.0f} km Trip",
            xaxis_title="Trip Distance (km)",
            yaxis_title="Total Energy Consumed (kWh)",
            height=320,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig_sim, use_container_width=True)

    with sim_c2:
        st.dataframe(
            sim_df[["Segment", "Speed (km/h)", "Slope (%)", "Current Energy (kWh)", "AI-Optimized (kWh)"]],
            use_container_width=True, hide_index=True
        )

st.markdown("<div style='text-align: center; color: #94a3b8; font-size: 0.85rem; margin-top: 2rem;'>AI-Powered Driving Efficiency Optimizer • Built with Scikit-learn, Plotly & Streamlit</div>", unsafe_allow_html=True)

