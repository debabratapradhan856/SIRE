import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

def train_and_export():
    dataset_path = 'EV_Energy_Consumption_Dataset.csv'
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset {dataset_path} not found!")

    df = pd.read_csv(dataset_path)
    print(f"Loaded dataset: {df.shape[0]} rows, {df.shape[1]} columns")

    # Features used for energy consumption prediction
    feature_cols = [
        'Speed_kmh',
        'Acceleration_ms2',
        'Battery_State_%',
        'Battery_Voltage_V',
        'Battery_Temperature_C',
        'Driving_Mode',
        'Road_Type',
        'Traffic_Condition',
        'Slope_%',
        'Weather_Condition',
        'Temperature_C',
        'Humidity_%',
        'Wind_Speed_ms',
        'Tire_Pressure_psi',
        'Vehicle_Weight_kg',
        'Distance_Travelled_km'
    ]

    X = df[feature_cols].copy()
    y = df['Energy_Consumption_kWh'].values

    # Train / Test Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # 1. Train Random Forest Regressor
    print("Training Random Forest Regressor...")
    rf_model = RandomForestRegressor(
        n_estimators=120,
        max_depth=14,
        min_samples_split=4,
        random_state=42,
        n_jobs=-1
    )
    rf_model.fit(X_train, y_train)

    rf_preds = rf_model.predict(X_test)
    rf_r2 = float(r2_score(y_test, rf_preds))
    rf_mae = float(mean_absolute_error(y_test, rf_preds))
    rf_rmse = float(np.sqrt(mean_squared_error(y_test, rf_preds)))

    print(f"Random Forest Performance -> R2: {rf_r2:.4f}, MAE: {rf_mae:.4f} kWh, RMSE: {rf_rmse:.4f} kWh")

    # 2. Train Gradient Boosting Regressor (for comparison & fast inference)
    print("Training Gradient Boosting Regressor...")
    gb_model = GradientBoostingRegressor(
        n_estimators=150,
        learning_rate=0.08,
        max_depth=6,
        random_state=42
    )
    gb_model.fit(X_train, y_train)

    gb_preds = gb_model.predict(X_test)
    gb_r2 = float(r2_score(y_test, gb_preds))
    gb_mae = float(mean_absolute_error(y_test, gb_preds))
    gb_rmse = float(np.sqrt(mean_squared_error(y_test, gb_preds)))

    print(f"Gradient Boosting Performance -> R2: {gb_r2:.4f}, MAE: {gb_mae:.4f} kWh, RMSE: {gb_rmse:.4f} kWh")

    # Select best model
    best_model = rf_model if rf_r2 >= gb_r2 else gb_model
    best_name = "RandomForest" if rf_r2 >= gb_r2 else "GradientBoosting"

    # Feature Importances
    importances = rf_model.feature_importances_
    feat_imp = sorted(
        [{"feature": col, "importance": round(float(imp), 4)} for col, imp in zip(feature_cols, importances)],
        key=lambda x: x["importance"],
        reverse=True
    )

    # 3. Train Driving Behavior Clustering (K-Means)
    print("Training Driving Behavior Clusterer (K-Means)...")
    cluster_features = ['Speed_kmh', 'Acceleration_ms2', 'Slope_%', 'Energy_Consumption_kWh']
    scaler_cluster = StandardScaler()
    X_cluster_scaled = scaler_cluster.fit_transform(df[cluster_features])

    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
    df['Cluster'] = kmeans.fit_predict(X_cluster_scaled)

    # Compute cluster profiles
    cluster_profiles = {}
    cluster_names = {
        0: "Eco-Smooth Cruiser",
        1: "Aggressive High-Speed",
        2: "Urban Stop & Go",
        3: "Heavy Mountain / Terrain"
    }

    for c in range(4):
        sub = df[df['Cluster'] == c]
        cluster_profiles[c] = {
            "name": cluster_names.get(c, f"Profile {c}"),
            "count": int(len(sub)),
            "pct": round(len(sub) / len(df) * 100, 1),
            "avg_speed": round(float(sub['Speed_kmh'].mean()), 2),
            "avg_acceleration": round(float(sub['Acceleration_ms2'].mean()), 3),
            "avg_energy": round(float(sub['Energy_Consumption_kWh'].mean()), 2),
            "avg_slope": round(float(sub['Slope_%'].mean()), 2)
        }

    # Save artifacts
    os.makedirs('models', exist_ok=True)
    joblib.dump(best_model, 'models/energy_model.joblib')
    joblib.dump(scaler_cluster, 'models/cluster_scaler.joblib')
    joblib.dump(kmeans, 'models/cluster_kmeans.joblib')

    metadata = {
        "best_model": best_name,
        "feature_cols": feature_cols,
        "metrics": {
            "random_forest": {"r2": rf_r2, "mae": rf_mae, "rmse": rf_rmse},
            "gradient_boosting": {"r2": gb_r2, "mae": gb_mae, "rmse": gb_rmse}
        },
        "feature_importances": feat_imp,
        "cluster_profiles": cluster_profiles,
        "dataset_stats": {
            "total_samples": len(df),
            "avg_energy_kwh": round(float(df['Energy_Consumption_kWh'].mean()), 2),
            "min_energy_kwh": round(float(df['Energy_Consumption_kWh'].min()), 2),
            "max_energy_kwh": round(float(df['Energy_Consumption_kWh'].max()), 2),
            "avg_speed_kmh": round(float(df['Speed_kmh'].mean()), 2),
            "avg_efficiency_km_kwh": round(float((df['Distance_Travelled_km'] / df['Energy_Consumption_kWh']).mean()), 2)
        }
    }

    with open('models/metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)

    print("Model training & export complete! Artifacts saved to ./models/")
    return metadata

if __name__ == '__main__':
    train_and_export()

