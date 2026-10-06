"""
DisasterLens Operational Priority Index (OPI) Engine
Implements the UN INFORM / UNDRR Risk Formulation adapted for emergency decision-support:
Risk = (Hazard & Exposure) x Vulnerability x (1 - Coping Capacity)
"""

from typing import Dict, Any, Tuple, Optional
import numpy as np
import pandas as pd



def compute_vulnerability_score(df: pd.DataFrame) -> np.ndarray:
    """
    Computes demographic vulnerability index V_i in [0, 1].
    Gives appropriate weights to elderly (>=65), mobility-impaired, poverty, and pediatric (<5).
    Safely defaults if columns are missing or contain NaNs.
    """
    elderly = np.nan_to_num(pd.to_numeric(df["elderly_ratio"] if "elderly_ratio" in df.columns else 0.12, errors="coerce"), nan=0.12)
    mobility = np.nan_to_num(pd.to_numeric(df["mobility_impaired_ratio"] if "mobility_impaired_ratio" in df.columns else 0.08, errors="coerce"), nan=0.08)
    poverty = np.nan_to_num(pd.to_numeric(df["poverty_ratio"] if "poverty_ratio" in df.columns else 0.22, errors="coerce"), nan=0.22)
    pediatric = np.nan_to_num(pd.to_numeric(df["pediatric_ratio"] if "pediatric_ratio" in df.columns else 0.14, errors="coerce"), nan=0.14)
    
    v_score = 0.40 * elderly + 0.25 * mobility + 0.20 * poverty + 0.15 * pediatric
    return np.clip(v_score, 0.0, 1.0)


def compute_infrastructure_deficit(df: pd.DataFrame) -> np.ndarray:
    """
    Computes infrastructure vulnerability / deficit I_i in [0, 1].
    Considers road network severances (vital for physical evacuation) and grid collapse.
    """
    road_raw = np.nan_to_num(pd.to_numeric(df["road_connectivity_pct"] if "road_connectivity_pct" in df.columns else 100.0, errors="coerce"), nan=100.0)
    grid_raw = np.nan_to_num(pd.to_numeric(df["power_grid_status_pct"] if "power_grid_status_pct" in df.columns else 100.0, errors="coerce"), nan=100.0)
    
    road_pct = road_raw / 100.0
    grid_pct = grid_raw / 100.0
    
    infra_deficit = 0.60 * (1.0 - road_pct) + 0.40 * (1.0 - grid_pct)
    return np.clip(infra_deficit, 0.0, 1.0)


def compute_coping_capacity(df: pd.DataFrame) -> np.ndarray:
    """
    Computes local coping capacity C_i in [0.05, 1.0].
    Based on acute hospital bed ratio per capita and drainage resilience.
    """
    pop = np.nan_to_num(pd.to_numeric(df["total_population"] if "total_population" in df.columns else 50000, errors="coerce"), nan=50000)
    if "hospital_bed_capacity" in df.columns:
        beds = np.nan_to_num(pd.to_numeric(df["hospital_bed_capacity"], errors="coerce"), nan=50)
    elif "hospital_beds" in df.columns:
        beds = np.nan_to_num(pd.to_numeric(df["hospital_beds"], errors="coerce"), nan=50)
    else:
        beds = np.full(len(df), 50.0)
    
    drainage = np.nan_to_num(pd.to_numeric(df["drainage_capacity"] if "drainage_capacity" in df.columns else df.get("drainage_capacity_index", 0.5), errors="coerce"), nan=0.5)
    
    # Bed capacity benchmark: 4 beds per 1,000 population
    bed_ratio = beds / (np.maximum(pop, 1) / 1000.0 * 4.0)
    coping = 0.65 * np.clip(bed_ratio, 0.0, 1.0) + 0.35 * drainage
    return np.clip(coping, 0.05, 1.0)



def compute_operational_priority_index(
    df: pd.DataFrame,
    predicted_severity: Optional[np.ndarray] = None,
    weight_hazard: float = 0.40,
    weight_vulnerability: float = 0.35,
    weight_infrastructure: float = 0.25
) -> pd.DataFrame:
    """
    Computes the Operational Priority Index (OPI) in [0, 100] for each operational sector.
    
    Formula:
    OPI_i = [ w_h * (S_hat_i * log(Exposure)) + w_v * V_i + w_infra * I_i ] / (0.4 * C_i + 0.6)
    
    Returns enriched DataFrame with OPI, Triage Tier, and specific resource demand estimations.
    """
    result = df.copy()
    if predicted_severity is None:
        if "predicted_severity" in result.columns:
            predicted_severity = result["predicted_severity"].values
        else:
            predicted_severity = np.zeros(len(result))

    result["predicted_severity"] = np.round(predicted_severity, 4)

    
    # Population exposure scaling (log-scaled to prevent mega-zones from drowning out high-risk smaller zones) and normalized to [0.2, 1.0] 
    pop = result["total_population"].values
    norm_exposure = np.log10(np.maximum(pop, 100.0)) / np.log10(50000.0) # max ~50k pop
    norm_exposure = np.clip(norm_exposure, 0.2, 1.0)
    
    hazard_exposure_impact = predicted_severity * norm_exposure
    vulnerability_score = compute_vulnerability_score(result)
    infra_deficit = compute_infrastructure_deficit(result)
    coping_capacity = compute_coping_capacity(result)
    
    raw_priority = (
        weight_hazard * hazard_exposure_impact +
        weight_vulnerability * vulnerability_score +
        weight_infrastructure * infra_deficit
    ) / (0.45 * coping_capacity + 0.55)
    
    # Normalize to 0-100 scale
    opi_score = (raw_priority * 100.0).clip(0.0, 100.0)
    result["vulnerability_score"] = np.round(vulnerability_score, 3)
    result["infrastructure_deficit"] = np.round(infra_deficit, 3)
    result["coping_capacity"] = np.round(coping_capacity, 3)
    result["opi_score"] = np.round(opi_score, 1)
    
    # Assign Triage Tier
    def assign_triage(score: float) -> Tuple[str, str]:
        if score >= 70.0:
            return "Catastrophic (Tier 1)", "#D32F2F" # Deep Red
        elif score >= 50.0:
            return "High Priority (Tier 2)", "#F57C00" # Orange
        elif score >= 30.0:
            return "Moderate (Tier 3)", "#FBC02D" # Amber/Yellow
        else:
            return "Low Priority (Tier 4)", "#388E3C" # Green
            
    triage_info = [assign_triage(s) for s in result["opi_score"]]
    result["triage_tier"] = [t[0] for t in triage_info]
    result["triage_color"] = [t[1] for t in triage_info]
    
    # Estimate Resource Demands (for prescriptive optimization)
    # 1. Search & Rescue Boats: demanded when flood gauge is elevated and OPI is high
    flood_depth = np.nan_to_num(pd.to_numeric(result["flood_gauge_m"] if "flood_gauge_m" in result.columns else 0.0, errors="coerce"), nan=0.0)
    boat_demand = np.where(flood_depth >= 0.8, np.ceil(flood_depth * 1.5 + (opi_score / 25.0)), 0)
    boat_demand = np.nan_to_num(boat_demand, nan=0).astype(int)
    result["demand_sar_boats"] = np.clip(boat_demand, 0, 10)
    
    # 2. Advanced Mobile Medical Units: demanded by high OPI & high elderly/mobility
    elderly_r = np.nan_to_num(pd.to_numeric(result["elderly_ratio"] if "elderly_ratio" in result.columns else 0.12, errors="coerce"), nan=0.12)
    mobility_r = np.nan_to_num(pd.to_numeric(result["mobility_impaired_ratio"] if "mobility_impaired_ratio" in result.columns else 0.08, errors="coerce"), nan=0.08)
    med_demand = np.ceil((opi_score / 30.0) * (elderly_r + mobility_r) * 3.5)
    med_demand = np.nan_to_num(med_demand, nan=0).astype(int)
    result["demand_medical_clinics"] = np.clip(med_demand, 0, 8)
    
    # 3. Clean Water & Food Ration Kits (hundreds of kits, e.g., in units of 100-packs):
    pop = np.nan_to_num(pd.to_numeric(result["total_population"] if "total_population" in result.columns else 5000, errors="coerce"), nan=5000.0)
    infra_def = np.nan_to_num(pd.to_numeric(result["infrastructure_deficit"] if "infrastructure_deficit" in result.columns else 0.3, errors="coerce"), nan=0.3)
    ration_demand = np.ceil((pop / 5000.0) * (infra_def + 0.2) * 2.0)
    ration_demand = np.nan_to_num(ration_demand, nan=1).astype(int)
    result["demand_ration_kits"] = np.clip(ration_demand, 1, 20)
    
    # 4. Heavy Generators: demanded by power grid blackout + critical facilities
    grid_pct = np.nan_to_num(pd.to_numeric(result["power_grid_status_pct"] if "power_grid_status_pct" in result.columns else 100.0, errors="coerce"), nan=100.0)
    grid_down = (100.0 - grid_pct) / 100.0
    if "hospital_bed_capacity" in result.columns:
        beds_count = np.nan_to_num(pd.to_numeric(result["hospital_bed_capacity"], errors="coerce"), nan=0.0)
    elif "hospital_beds" in result.columns:
        beds_count = np.nan_to_num(pd.to_numeric(result["hospital_beds"], errors="coerce"), nan=0.0)
    else:
        beds_count = np.zeros(len(result))
    has_hosp = (beds_count > 0)
    gen_demand = np.where(grid_down > 0.4, np.ceil(grid_down * 3.0 + has_hosp * 2), 0)
    gen_demand = np.nan_to_num(gen_demand, nan=0).astype(int)
    result["demand_generators"] = np.clip(gen_demand, 0, 6)
    
    # Sort descending by OPI score to form the triage queue
    result = result.sort_values(by="opi_score", ascending=False).reset_index(drop=True)
    result["priority_rank"] = np.arange(1, len(result) + 1)
    
    return result
