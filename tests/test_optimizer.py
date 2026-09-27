"""
Unit Tests for DisasterLens Prescriptive Constrained Resource Optimizer (MILP)
"""

import pytest
import numpy as np
import pandas as pd
from engine.optimizer import solve_resource_allocation, RESOURCE_TYPES, DEFAULT_SUPPLY
from data.generator import generate_live_operational_telemetry
from engine.opi import compute_operational_priority_index


@pytest.fixture
def sample_prioritized_data():
    telemetry = generate_live_operational_telemetry(scenario_type="flash_flood_surge")
    dummy_sev = np.random.uniform(0.3, 0.9, len(telemetry))
    prioritized = compute_operational_priority_index(telemetry, dummy_sev)
    return prioritized


def test_supply_constraints(sample_prioritized_data):
    supply = {
        "sar_boats": 10,
        "medical_clinics": 6,
        "ration_kits": 25,
        "generators": 8
    }
    alloc_df, summary = solve_resource_allocation(sample_prioritized_data, available_supply=supply)
    
    assert "Optimal" in summary["solver_status"]
    for r_name in RESOURCE_TYPES:
        total_alloc = alloc_df[f"alloc_{r_name}"].sum()
        assert total_alloc <= supply[r_name], f"Resource {r_name} exceeded supply limit!"


def test_demand_bounds(sample_prioritized_data):
    alloc_df, _ = solve_resource_allocation(sample_prioritized_data)
    for r_name in RESOURCE_TYPES:
        assert np.all(alloc_df[f"alloc_{r_name}"] <= alloc_df[f"demand_{r_name}"])
        assert np.all(alloc_df[f"alloc_{r_name}"] >= 0)
        assert np.all(alloc_df[f"deficit_{r_name}"] >= 0)


def test_road_severance_bottleneck():
    telemetry = generate_live_operational_telemetry(
        scenario_type="flash_flood_surge",
        road_severance_sectors=["IND-002", "IND-006"]
    )
    dummy_sev = np.random.uniform(0.5, 0.9, len(telemetry))
    prioritized = compute_operational_priority_index(telemetry, dummy_sev)
    
    alloc_df, summary = solve_resource_allocation(prioritized)
    
    # Check that road severed sectors receive 0 ground medical clinics
    for s_id in ["IND-002", "IND-006"]:
        sec_row = alloc_df[alloc_df["zone_id"] == s_id].iloc[0]
        assert sec_row["alloc_medical_clinics"] == 0, f"Severed sector {s_id} was improperly allocated wheeled clinics!"
        
    assert any("IND-002" in w for w in summary["logistics_warnings"])
    assert any("IND-006" in w for w in summary["logistics_warnings"])


def test_zero_supply_edge_case(sample_prioritized_data):
    zero_supply = {r: 0 for r in RESOURCE_TYPES}
    alloc_df, summary = solve_resource_allocation(sample_prioritized_data, available_supply=zero_supply)
    
    for r_name in RESOURCE_TYPES:
        assert alloc_df[f"alloc_{r_name}"].sum() == 0
