<<<<<<< HEAD
# ⚡ AI-Powered Driving Efficiency Optimizer

## 📌 Problem Statement & Compliance Audit

### Problem Statement:
> **Objective**: Create an AI model to analyze driving behavior and optimize energy usage.  
> **Guidelines**:
> 1. Use Python with Scikit-learn or TensorFlow.
> 2. Collect simulated driving data (speed, terrain, braking).
> 3. Suggest driving tips based on prediction results.

---

### Audit: "Is this true?" (Checking the Original Notebook)

| Guideline / Objective | Original Notebook (`ev-energy-consumption.ipynb`) | Status in Original | Current Enhanced Implementation |
| :--- | :--- | :---: | :--- |
| **Python with Scikit-learn / TensorFlow** | Used `sklearn` (`RandomForestRegressor`, `KMeans`, `PCA`, `StandardScaler`). |  **True (Met)** | Trained **Gradient Boosting** ($R^2 = 92.85\%$) & **Random Forest** ($R^2 = 91.17\%$). |
| **Simulated Driving Data (Speed, Terrain, Braking)** | Kaggle dataset with `Speed_kmh`, `Slope_%` (terrain), `Acceleration_ms2` (braking / throttle), `Driving_Mode`. | ⚠️ **Partial** (Data was unlinked from Windows environment; missing local file) | Downloaded local 5,000-sample dataset `EV_Energy_Consumption_Dataset.csv` and created dynamic route simulators. |
| **Model Evaluation Metrics** | Missing printed metrics ($R^2$, $MAE$, $RMSE$); model was only used for SHAP plot generation. | ❌ **Missing** | Added complete model evaluation with $R^2 = 0.9285$, $MAE = 0.474\text{ kWh}$, $RMSE = 0.589\text{ kWh}$. |
| **Suggest Driving Tips based on Prediction Results** | Notebook stopped after SHAP feature importance; did NOT output driving tips. | ❌ **Missing** | Implemented **Dynamic Driving Tips Engine** (`optimizer.py`) with physics & AI-guided recommendations for Speed, Braking/Regen, Drive Mode, and Terrain. |
| **Interactive Dashboard** | No GUI or dashboard existed; only raw notebook cells. | ❌ **Missing** | Built **TWO** modern interactive dashboards: **FastAPI + Tailwind Web Dashboard** and **Streamlit Dashboard**! |

---

## 🚀 How to Run the Dashboards

You now have **Next.js** as your primary modern frontend, plus the Python backend and Streamlit options:

### Option 1: Next.js 16 + React 19 Frontend (Recommended)
High-performance modern React frontend with live slider controls, dynamic SVG charts, and real-time Scikit-learn predictions.

- **One-Click Launch**: Double-click `run_full_system.bat`  
  *(Launches both the FastAPI AI Backend on `:8000` and Next.js Frontend on `:3000`, and opens your browser automatically!)*
- *Or Manual Launch*:
  1. Terminal 1 (AI Backend): `python app.py`
  2. Terminal 2 (Next.js App): `npm --prefix frontend run dev`
  3. Open: **`http://localhost:3000`**

### Option 2: Streamlit Interactive Dashboard
Full data science dashboard with interactive Plotly visualizers.

- **Double-click**: `run_streamlit.bat`  
  *OR*
- **Terminal**: `streamlit run streamlit_app.py`
- Opens automatically at: **`http://localhost:8501`**

---

## 🧠 System Architecture & Key Features

### 1. Machine Learning Models (`train_model.py` / `models/`)
- **Gradient Boosting Regressor & Random Forest Regressor**:
  - $R^2 \text{ Score}$: **$0.9285$** (Over 92.8% of energy consumption variation explained)
  - Mean Absolute Error (MAE): **$0.474\text{ kWh}$**
  - Root Mean Squared Error (RMSE): **$0.589\text{ kWh}$**
- **K-Means Driving Style Clustering**:
  - Automatically identifies driver profiles into:
    - `Eco-Smooth Cruiser`
    - `Aggressive High-Speed`
    - `Urban Stop & Go`
    - `Heavy Mountain / Terrain`

### 2. AI Optimization Engine (`optimizer.py`)
- Evaluates your current driving telemetry against optimal physical operating envelopes.
- Computes **Exact kWh Saved**, **% Energy Cut**, and **Extra Range (km) Gained**.
- Calculates an **Eco-Score (0 to 100)** with letter grades ($A+$ to $F$).

### 3. Contextual Driving Tips Engine
Dynamically triggers actionable recommendations based on real-time predictions:
- **Speed Aerodynamics**: Detects excessive aerodynamic drag at speeds $>90\text{ km/h}$; calculates exact savings if speed is reduced to $80\text{--}85\text{ km/h}$.
- **Regenerative Braking**: Detects harsh deceleration ($<-1.8\text{ m/s}^2$); advises gradual 1-pedal braking to recover up to $90\%$ of kinetic energy instead of wasting rotor friction heat.
- **Drive Mode Optimization**: Suggests switching from Sport to Eco mode under urban or cruising scenarios to save $10\text{--}15\%$ energy.
- **Terrain Ascent/Descent**: Instructs steady throttle momentum during uphill climbs ($>+4\%$) and coasting regeneration on descents ($<-3\%$).
- **Thermal & Climate Management**: Warns about temperature extremes and tire pressure rolling resistance.

### 4. Interactive Route Simulator
Simulates a multi-stage 10-stop journey (City start $\to$ Congestion $\to$ Highway cruising $\to$ Mountain climb $\to$ Descent $\to$ Destination) showing continuous battery consumption and cumulative AI savings!

---

## 📁 Project File Structure

```text
SIRE/
│
├── EV_Energy_Consumption_Dataset.csv   # Local 5,000-row simulated EV telematics dataset
├── ev-energy-consumption.ipynb          # Updated notebook with EDA, K-Means, ML & Tips
├── train_model.py                      # Trains Scikit-learn models & exports joblib artifacts
├── optimizer.py                        # Core AI engine for energy prediction & driving tips
├── app.py                              # FastAPI backend REST API server
├── run_dashboard.py                    # One-click dashboard launcher (auto-opens browser)
├── run_web_dashboard.bat               # Windows batch shortcut for FastAPI web app
├── streamlit_app.py                    # Streamlit dashboard application
├── run_streamlit.bat                   # Windows batch shortcut for Streamlit app
│
├── models/                             # Exported trained ML models & metadata
│   ├── energy_model.joblib
│   ├── cluster_scaler.joblib
│   ├── cluster_kmeans.joblib
│   └── metadata.json
│
└── templates/
    └── index.html                      # Modern responsive UI with Tailwind & Chart.js
```

=======
This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
>>>>>>> 9395be0 (Initial commit from Create Next App)
