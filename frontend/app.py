import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from optimizer import DrivingEfficiencyOptimizer

app = FastAPI(title="AI-Powered Driving Efficiency Optimizer", version="1.0.0")

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")
optimizer = DrivingEfficiencyOptimizer()

@app.get("/", response_class=HTMLResponse)
async def index():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        html = f.read()
    return HTMLResponse(content=html)

@app.post("/api/optimize")
async def optimize_telemetry(request: Request):
    data = await request.json()
    results = optimizer.analyze_and_optimize(data)
    return JSONResponse(results)

@app.post("/api/predict-quick")
async def predict_quick(request: Request):
    data = await request.json()
    pred = optimizer.predict_energy(data)
    return JSONResponse({"energy_kwh": pred})

@app.get("/api/model-info")
async def get_model_info():
    return JSONResponse(optimizer.metadata)

@app.get("/api/simulate-route")
async def simulate_route():
    route_segments = [
        {"segment": "1. City Center", "km": 3.0, "speed": 35.0, "accel": 0.8, "slope": 0.0, "road": 2},
        {"segment": "2. Signal Jam", "km": 2.0, "speed": 22.0, "accel": -2.2, "slope": 0.5, "road": 2},
        {"segment": "3. Ring Road", "km": 5.0, "speed": 60.0, "accel": 1.2, "slope": 1.0, "road": 1},
        {"segment": "4. Highway Cruising", "km": 10.0, "speed": 95.0, "accel": 0.1, "slope": 0.0, "road": 1},
        {"segment": "5. High-Speed Strip", "km": 12.0, "speed": 120.0, "accel": 0.4, "slope": -0.5, "road": 1},
        {"segment": "6. Foothills Ascent", "km": 6.0, "speed": 70.0, "accel": 1.5, "slope": 6.5, "road": 3},
        {"segment": "7. Steep Mountain Pass", "km": 4.0, "speed": 50.0, "accel": 0.8, "slope": 9.0, "road": 3},
        {"segment": "8. Mountain Descent", "km": 5.0, "speed": 55.0, "accel": -1.2, "slope": -4.5, "road": 3},
        {"segment": "9. Suburban Access", "km": 4.0, "speed": 50.0, "accel": -0.4, "slope": 0.0, "road": 2},
        {"segment": "10. Destination Arrival", "km": 2.0, "speed": 30.0, "accel": -0.6, "slope": 0.0, "road": 2}
    ]

    base_payload = {
        'Battery_State_%': 65.0,
        'Battery_Voltage_V': 350.0,
        'Battery_Temperature_C': 28.0,
        'Driving_Mode': 2,
        'Weather_Condition': 1,
        'Temperature_C': 20.0,
        'Humidity_%': 55.0,
        'Wind_Speed_ms': 6.0,
        'Tire_Pressure_psi': 31.5,
        'Vehicle_Weight_kg': 1850.0
    }

    results = []
    cum_km = 0.0
    cum_current = 0.0
    cum_opt = 0.0

    for seg in route_segments:
        p = base_payload.copy()
        p['Distance_Travelled_km'] = seg['km']
        p['Speed_kmh'] = seg['speed']
        p['Acceleration_ms2'] = seg['accel']
        p['Slope_%'] = seg['slope']
        p['Road_Type'] = seg['road']

        res = optimizer.analyze_and_optimize(p)
        cum_km += seg['km']
        c_kwh = res['current_profile']['predicted_energy_kwh']
        o_kwh = res['optimized_profile']['predicted_energy_kwh']
        cum_current += c_kwh
        cum_opt += o_kwh

        results.append({
            "segment": seg['segment'],
            "distance_km": seg['km'],
            "speed_kmh": seg['speed'],
            "slope_pct": seg['slope'],
            "current_kwh": c_kwh,
            "opt_kwh": o_kwh,
            "cum_km": round(cum_km, 1),
            "cum_current_kwh": round(cum_current, 2),
            "cum_opt_kwh": round(cum_opt, 2)
        })

    return JSONResponse(results)

if __name__ == "__main__":
    print("Starting AI Driving Efficiency Optimizer Web Server on http://localhost:8000 ...")
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=False)
