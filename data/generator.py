"""
DisasterLens Data Pipeline & Telemetry Engine
Implements:
1. Multi-zone seeded spatial & demographic structure.
2. Synthetic historical disaster dataset generator (for ML model training).
3. Real-time scenario generator with What-If parametric modifiers.
4. Live Open-Meteo API connector for real-world meteorological telemetry.
"""

import json
import os
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
import requests

SEED_FILE = os.path.join(os.path.dirname(__file__), "zones_seed.json")


def load_seed_zones() -> pd.DataFrame:
    """Loads baseline 15 operational sectors from zones_seed.json."""
    if not os.path.exists(SEED_FILE):
        raise FileNotFoundError(f"Seed file not found at {SEED_FILE}")
    with open(SEED_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return pd.DataFrame(data)


def generate_historical_training_data(n_samples: int = 5000, random_seed: int = 42) -> pd.DataFrame:
    """
    Generates synthetic historical disaster incident telemetry with realistic physical correlations
    to train the XGBoost Expected Damage Severity Model (S_hat in [0, 1]).
    
    Physical logic:
    - Low elevation + high precipitation + low drainage -> rapid flood gauge surge -> structural inundation.
    - High wind gusts + coastal proximity -> roof tearing, utility line damage.
    - Low power grid resilience + structural age -> higher utility failure.
    - Target: composite_damage_severity in [0.0, 1.0].
    """
    np.random.seed(random_seed)
    
    # 1. Environmental & Hazard Drivers
    rainfall_mm_h = np.random.exponential(scale=35.0, size=n_samples).clip(0.0, 180.0)
    wind_gust_kmh = np.random.weibull(a=2.0, size=n_samples) * 35.0 + np.random.uniform(10.0, 40.0, size=n_samples)
    wind_gust_kmh = wind_gust_kmh.clip(15.0, 210.0)
    elevation_m = np.random.uniform(1.0, 45.0, size=n_samples)
    drainage_capacity = np.random.uniform(0.15, 0.95, size=n_samples)
    
    # Flood gauge physics: gauge rises when rain is high, elevation is low, and drainage is poor
    flood_surge_potential = (rainfall_mm_h / 50.0) * (1.0 / (np.sqrt(elevation_m) + 0.5)) * (1.2 - drainage_capacity)
    flood_gauge_m = (flood_surge_potential * 1.8 + np.random.normal(0, 0.2, size=n_samples)).clip(0.0, 4.5)
    
    # 2. Demographic & Built Environment Drivers
    population_density = np.random.uniform(500, 8000, size=n_samples) # per km2
    elderly_ratio = np.random.beta(a=2.5, b=10.0, size=n_samples).clip(0.05, 0.55)
    pediatric_ratio = np.random.beta(a=2.0, b=15.0, size=n_samples).clip(0.02, 0.20)
    mobility_impaired_ratio = np.random.beta(a=2.0, b=12.0, size=n_samples).clip(0.03, 0.30)
    poverty_ratio = np.random.uniform(0.05, 0.50, size=n_samples)
    
    # 3. Infrastructure & Resilience Factors
    baseline_road_connectivity = np.random.uniform(0.70, 1.0, size=n_samples)
    # Severe flooding or wind causes road degradation
    road_degradation = (flood_gauge_m / 4.0) * 0.65 + (wind_gust_kmh / 200.0) * 0.25 + np.random.uniform(0, 0.1, size=n_samples)
    road_connectivity_pct = ((baseline_road_connectivity - road_degradation) * 100.0).clip(5.0, 100.0)
    
    power_grid_outage_risk = (wind_gust_kmh / 150.0) * 0.6 + (flood_gauge_m / 3.0) * 0.3 + np.random.uniform(0, 0.15, size=n_samples)
    power_grid_status_pct = ((1.0 - power_grid_outage_risk) * 100.0).clip(0.0, 100.0)
    
    hospital_bed_capacity = np.random.choice([0, 20, 50, 120, 250, 400], size=n_samples, p=[0.2, 0.15, 0.2, 0.2, 0.15, 0.1])
    
    # 4. Target Generation: Physical Composite Damage Severity S in [0, 1]
    # In emergency management, structural severity combines water inundation damage, wind destruction, and grid collapse
    hazard_damage = (
        0.48 * (flood_gauge_m / 4.0) +
        0.28 * (wind_gust_kmh / 200.0) +
        0.14 * (rainfall_mm_h / 150.0) +
        0.10 * ((100.0 - power_grid_status_pct) / 100.0)
    )
    # Add minor realistic noise
    composite_damage_severity = (hazard_damage + np.random.normal(0, 0.03, size=n_samples)).clip(0.02, 0.98)
    
    df = pd.DataFrame({
        "rainfall_mm_h": np.round(rainfall_mm_h, 1),
        "wind_gust_kmh": np.round(wind_gust_kmh, 1),
        "elevation_m": np.round(elevation_m, 1),
        "drainage_capacity": np.round(drainage_capacity, 2),
        "flood_gauge_m": np.round(flood_gauge_m, 2),
        "population_density": np.round(population_density, 0),
        "elderly_ratio": np.round(elderly_ratio, 3),
        "pediatric_ratio": np.round(pediatric_ratio, 3),
        "mobility_impaired_ratio": np.round(mobility_impaired_ratio, 3),
        "poverty_ratio": np.round(poverty_ratio, 3),
        "road_connectivity_pct": np.round(road_connectivity_pct, 1),
        "power_grid_status_pct": np.round(power_grid_status_pct, 1),
        "hospital_bed_capacity": hospital_bed_capacity,
        "composite_damage_severity": np.round(composite_damage_severity, 4)
    })
    
    return df


def generate_live_operational_telemetry(
    scenario_type: str = "flash_flood_surge",
    rainfall_modifier_pct: float = 0.0,
    wind_modifier_pct: float = 0.0,
    road_severance_sectors: Optional[List[str]] = None,
    grid_blackout_sectors: Optional[List[str]] = None,
    random_seed: int = 101
) -> pd.DataFrame:
    """
    Generates operational multi-zone telemetry for 15 sectors under selected disaster scenario
    and What-If slider adjustments.
    
    Scenarios supported:
    - 'flash_flood_surge': Heavy torrential rain, low-elevation bayous overwhelmed.
    - 'hurricane_landfall': Cat 4 winds, storm surge, widespread power and tree fall.
    - 'cascading_grid_failure': Heatwave/transformer blackout, water treatment and hospitals strained.
    - 'moderate_baseline': Typical seasonal rain, minimal infrastructure stress.
    """
    np.random.seed(random_seed)
    zones = load_seed_zones()
    n = len(zones)
    
    if scenario_type == "flash_flood_surge":
        base_rain = np.random.uniform(75.0, 140.0, size=n)
        base_wind = np.random.uniform(40.0, 75.0, size=n)
    elif scenario_type == "hurricane_landfall":
        base_rain = np.random.uniform(90.0, 160.0, size=n)
        base_wind = np.random.uniform(110.0, 185.0, size=n)
    elif scenario_type == "cascading_grid_failure":
        base_rain = np.random.uniform(10.0, 30.0, size=n)
        base_wind = np.random.uniform(20.0, 45.0, size=n)
    else:  # moderate_baseline
        base_rain = np.random.uniform(5.0, 25.0, size=n)
        base_wind = np.random.uniform(15.0, 35.0, size=n)
        
    # Apply What-If modifiers
    rain = (base_rain * (1.0 + rainfall_modifier_pct / 100.0)).clip(0.0, 220.0)
    wind = (base_wind * (1.0 + wind_modifier_pct / 100.0)).clip(0.0, 240.0)
    
    # Calculate flood gauge depth based on elevation and drainage index
    elev = np.maximum(zones["elevation_m"].values, 0.1)
    drainage = zones["drainage_capacity_index"].values
    
    surge_pot = (rain / 50.0) * (1.0 / (np.sqrt(elev) + 0.4)) * (1.25 - drainage)
    flood_depth = (surge_pot * 1.6 + np.random.uniform(-0.1, 0.15, size=n)).clip(0.0, 4.2)
    
    # Infrastructure degradation
    road_pct = (100.0 - (flood_depth / 3.5) * 60.0 - (wind / 200.0) * 25.0 + np.random.uniform(-5, 5, size=n)).clip(10.0, 100.0)
    power_pct = (100.0 - (wind / 160.0) * 60.0 - (flood_depth / 3.0) * 30.0 + np.random.uniform(-5, 5, size=n)).clip(5.0, 100.0)
    
    # Apply manual road severances / grid blackouts if selected in What-If sandbox
    if road_severance_sectors:
        for idx, row in zones.iterrows():
            if row["zone_id"] in road_severance_sectors:
                road_pct[idx] = np.random.uniform(5.0, 20.0) # Severed road threshold is < 30%
                
    if grid_blackout_sectors:
        for idx, row in zones.iterrows():
            if row["zone_id"] in grid_blackout_sectors:
                power_pct[idx] = np.random.uniform(0.0, 10.0)
                
    # Approximate population density per km2 assuming sector area ~ 5-10 km2
    pop_density = zones["total_population"].values / np.random.uniform(4.5, 7.5, size=n)
    
    telemetry_df = zones.copy()
    telemetry_df["rainfall_mm_h"] = np.round(rain, 1)
    telemetry_df["wind_gust_kmh"] = np.round(wind, 1)
    telemetry_df["drainage_capacity"] = np.round(drainage, 2)
    telemetry_df["flood_gauge_m"] = np.round(flood_depth, 2)
    telemetry_df["population_density"] = np.round(pop_density, 0)
    telemetry_df["road_connectivity_pct"] = np.round(road_pct, 1)
    telemetry_df["power_grid_status_pct"] = np.round(power_pct, 1)
    telemetry_df["hospital_bed_capacity"] = zones["hospital_beds"].values
    
    return telemetry_df


def fetch_live_open_meteo(latitude: float, longitude: float) -> Optional[Dict[str, Any]]:
    """
    Fetches real-time weather from Open-Meteo's open public API (free, no API key required).
    Returns temperature, precipitation, and wind speed if connected, else None.
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": ["temperature_2m", "precipitation", "wind_speed_10m", "relative_humidity_2m"],
        "hourly": ["precipitation"],
        "timezone": "auto"
    }
    try:
        response = requests.get(url, params=params, timeout=4.0)
        if response.status_code == 200:
            data = response.json()
            curr = data.get("current", {})
            return {
                "temperature_c": curr.get("temperature_2m"),
                "precipitation_mm": curr.get("precipitation"),
                "wind_speed_kmh": curr.get("wind_speed_10m"),
                "humidity_pct": curr.get("relative_humidity_2m"),
                "elevation": data.get("elevation")
            }
    except Exception:
        return None
    return None
