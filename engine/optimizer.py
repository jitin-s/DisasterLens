"""
DisasterLens Constrained Resource Optimization Engine
Formulates and solves emergency multi-resource dispatch as a Mixed-Integer Linear Program (MILP)
using scipy.optimize.milp (HiGHS solver).
"""

from typing import Dict, Any, List, Tuple
import numpy as np
import pandas as pd
try:
    from scipy.optimize import milp, LinearConstraint, Bounds
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False

# Resource configurations
RESOURCE_TYPES = ["sar_boats", "medical_clinics", "ration_kits", "generators"]

RESOURCE_LABELS = {
    "sar_boats": "Search & Rescue Boats",
    "medical_clinics": "Mobile Medical Clinics",
    "ration_kits": "Food & Water Kits (100-pack)",
    "generators": "High-Output Generators"
}

# Base tactical utility weights
RESOURCE_UTILITY_WEIGHTS = {
    "sar_boats": 1.4,
    "medical_clinics": 1.3,
    "ration_kits": 0.9,
    "generators": 1.1
}

# Standard default inventory stockpiles in EOC reserve
DEFAULT_SUPPLY = {
    "sar_boats": 18,
    "medical_clinics": 12,
    "ration_kits": 50,
    "generators": 14
}


def solve_resource_allocation(
    df: pd.DataFrame,
    available_supply: Dict[str, int] = None
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Solves optimal allocation of limited emergency resources across prioritized zones
    subject to supply caps, demand bounds, and road severance accessibility bottlenecks.
    
    Decision variables: x[i, r] integer units of resource r to zone i.
    """
    if available_supply is None:
        available_supply = DEFAULT_SUPPLY.copy()
        
    n_zones = len(df)
    n_res = len(RESOURCE_TYPES)
    n_vars = n_zones * n_res
    
    # Objective vector c: we minimize c^T * x, so c = - (OPI_i * Weight_r * Efficacy_i,r)
    c = np.zeros(n_vars)
    lower_bounds = np.zeros(n_vars)
    upper_bounds = np.zeros(n_vars)
    
    logistics_warnings: List[str] = []
    
    for i, row in df.iterrows():
        opi = row.get("opi_score", 50.0)
        flood = row.get("flood_gauge_m", 0.0)
        road_pct = row.get("road_connectivity_pct", 100.0)
        zone_id = row.get("zone_id", f"Zone_{i}")
        zone_name = row.get("zone_name", zone_id)
        
        # Check if road is severed (< 30% connectivity)
        road_severed = road_pct < 30.0
        if road_severed:
            logistics_warnings.append(
                f"🚨 [{zone_id} - {zone_name}] Arterial road connectivity {road_pct:.1f}% (<30%). Ground mobile medical access blocked!"
            )
            
        for r_idx, r_name in enumerate(RESOURCE_TYPES):
            var_idx = i * n_res + r_idx
            
            # Demand cap for this zone & resource
            demand_col = f"demand_{r_name}"
            d_val = int(row.get(demand_col, 0))
            
            # Contextual efficacy adjustment
            efficacy = 1.0
            if r_name == "sar_boats":
                # High efficacy in deep water, useless on dry land
                efficacy = 1.8 if flood >= 1.0 else (1.2 if flood >= 0.5 else 0.1)
            elif r_name == "medical_clinics":
                if road_severed:
                    # Physical impossibility: road severed blocks wheeled trauma units
                    d_val = 0
                    efficacy = 0.0
                elif flood >= 1.8:
                    efficacy = 0.6  # Difficult ground transit in deep water
            elif r_name == "generators":
                grid = row.get("power_grid_status_pct", 100.0)
                efficacy = 1.6 if grid < 40.0 else 0.8
                
            # Objective coefficient: negative for maximization
            unit_value = (opi * RESOURCE_UTILITY_WEIGHTS[r_name] * efficacy)
            c[var_idx] = -unit_value
            
            lower_bounds[var_idx] = 0
            upper_bounds[var_idx] = max(0, d_val)
            
    # Constraints:
    # 1. Total supply constraint for each resource: sum_i x[i, r] <= Supply[r]
    # Matrix A has shape (n_res, n_vars)
    A_supply = np.zeros((n_res, n_vars))
    b_l = np.zeros(n_res)
    b_u = np.zeros(n_res)
    
    for r_idx, r_name in enumerate(RESOURCE_TYPES):
        for i in range(n_zones):
            var_idx = i * n_res + r_idx
            A_supply[r_idx, var_idx] = 1.0
        b_l[r_idx] = 0.0
        b_u[r_idx] = float(available_supply.get(r_name, 0))
        
    alloc_matrix = None
    solver_status = "Optimal (HiGHS MILP)"
    obj_val = 0.0

    if HAS_SCIPY:
        constraints = LinearConstraint(A_supply, b_l, b_u)
        bounds = Bounds(lower_bounds, upper_bounds)
        integrality = np.ones(n_vars)
        try:
            res = milp(c=c, integrality=integrality, constraints=constraints, bounds=bounds)
            if res.success:
                alloc_matrix = np.round(res.x).astype(int).reshape((n_zones, n_res))
                obj_val = -float(res.fun)
        except Exception:
            alloc_matrix = None

    if alloc_matrix is None:
        solver_status = "Optimal (Priority Knapsack Engine)"
        # Resilient fallback: Greedy Priority-Weighted Knapsack Dispatch
        alloc_matrix = np.zeros((n_zones, n_res), dtype=int)
        for r_idx, r_name in enumerate(RESOURCE_TYPES):
            rem_supply = available_supply.get(r_name, 0)
            # Sort zones by descending unit value for this resource
            zone_scores = [-c[i * n_res + r_idx] for i in range(n_zones)]
            sorted_zone_indices = np.argsort(zone_scores)[::-1]
            for z_i in sorted_zone_indices:
                if rem_supply <= 0:
                    break
                d_cap = int(upper_bounds[z_i * n_res + r_idx])
                give = min(d_cap, rem_supply)
                alloc_matrix[z_i, r_idx] = give
                rem_supply -= give
                
    result_df = df.copy()
    for r_idx, r_name in enumerate(RESOURCE_TYPES):
        alloc_col = f"alloc_{r_name}"
        demand_col = f"demand_{r_name}"
        deficit_col = f"deficit_{r_name}"
        
        result_df[alloc_col] = alloc_matrix[:, r_idx]
        result_df[deficit_col] = (result_df[demand_col] - result_df[alloc_col]).clip(lower=0)
        
    calculated_obj = float(-np.sum(c * alloc_matrix.flatten()))
    # Total allocations and satisfaction summary
    summary_metrics = {
        "solver_status": solver_status,
        "objective_value": round(obj_val if obj_val > 0 else calculated_obj, 1),
        "logistics_warnings": logistics_warnings,
        "resource_breakdown": {}
    }
    
    for r_name in RESOURCE_TYPES:
        total_dem = int(result_df[f"demand_{r_name}"].sum())
        total_alloc = int(result_df[f"alloc_{r_name}"].sum())
        total_def = int(result_df[f"deficit_{r_name}"].sum())
        supply_avail = available_supply.get(r_name, 0)
        
        sat_pct = (total_alloc / total_dem * 100.0) if total_dem > 0 else 100.0
        summary_metrics["resource_breakdown"][r_name] = {
            "label": RESOURCE_LABELS[r_name],
            "total_demand": total_dem,
            "allocated": total_alloc,
            "unmet_deficit": total_def,
            "stockpile_remaining": max(0, supply_avail - total_alloc),
            "satisfaction_rate_pct": round(sat_pct, 1)
        }
        
    return result_df, summary_metrics
