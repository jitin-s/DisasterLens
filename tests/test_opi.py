"""
Unit Tests for DisasterLens Operational Priority Index (OPI) Engine
"""

import pytest
import numpy as np
import pandas as pd
from engine.opi import (
    compute_operational_priority_index,
    compute_vulnerability_score,
    compute_infrastructure_deficit,
    compute_coping_capacity
)
from data.generator import load_seed_zones


def test_vulnerability_score_bounds():
    df = load_seed_zones()
    v_score = compute_vulnerability_score(df)
    assert np.all(v_score >= 0.0)
    assert np.all(v_score <= 1.0)


def test_infrastructure_deficit_bounds():
    df = load_seed_zones()
    df["road_connectivity_pct"] = np.random.uniform(0, 100, len(df))
    df["power_grid_status_pct"] = np.random.uniform(0, 100, len(df))
    infra = compute_infrastructure_deficit(df)
    assert np.all(infra >= 0.0)
    assert np.all(infra <= 1.0)


def test_coping_capacity_bounds():
    df = load_seed_zones()
    df["drainage_capacity"] = df["drainage_capacity_index"]
    coping = compute_coping_capacity(df)
    assert np.all(coping >= 0.05)
    assert np.all(coping <= 1.0)


def test_opi_monotonicity_with_severity():
    df = load_seed_zones()
    df["drainage_capacity"] = df["drainage_capacity_index"]
    df["road_connectivity_pct"] = 80.0
    df["power_grid_status_pct"] = 80.0
    df["flood_gauge_m"] = 1.0
    
    n = len(df)
    low_sev = np.full(n, 0.1)
    high_sev = np.full(n, 0.9)
    
    res_low = compute_operational_priority_index(df, low_sev)
    res_high = compute_operational_priority_index(df, high_sev)
    
    # Higher damage severity must yield higher or equal OPI score
    assert np.all(res_high["opi_score"].values >= res_low["opi_score"].values)


def test_triage_tier_labels():
    df = load_seed_zones()
    df["drainage_capacity"] = df["drainage_capacity_index"]
    df["road_connectivity_pct"] = 80.0
    df["power_grid_status_pct"] = 80.0
    df["flood_gauge_m"] = 1.0
    
    sev = np.linspace(0.05, 0.95, len(df))
    res = compute_operational_priority_index(df, sev)
    
    valid_tiers = {
        "Catastrophic (Tier 1)",
        "High Priority (Tier 2)",
        "Moderate (Tier 3)",
        "Low Priority (Tier 4)"
    }
    for tier in res["triage_tier"]:
        assert tier in valid_tiers
        
    assert list(res["priority_rank"]) == list(range(1, len(df) + 1))
