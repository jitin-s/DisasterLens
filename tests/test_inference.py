"""
Unit Tests for Machine Learning Inference, Pipeline Generation, and SHAP Explainability
"""

import pytest
import os
import numpy as np
import pandas as pd
from data.generator import generate_historical_training_data, generate_live_operational_telemetry, load_seed_zones
from models.train_severity import FEATURE_COLUMNS, train_and_evaluate, load_trained_model
from engine.explainability import DisasterExplainer


def test_data_generator_validity():
    df = generate_historical_training_data(n_samples=200)
    assert len(df) == 200
    assert not df.isnull().values.any(), "Historical dataset contains unexpected NaN values"
    
    for col in FEATURE_COLUMNS:
        assert col in df.columns, f"Missing feature column: {col}"
        
    assert np.all(df["composite_damage_severity"] >= 0.0)
    assert np.all(df["composite_damage_severity"] <= 1.0)


def test_live_telemetry_generator():
    zones = load_seed_zones()
    telemetry = generate_live_operational_telemetry(scenario_type="flash_flood_surge")
    assert len(telemetry) == len(zones)
    assert "flood_gauge_m" in telemetry.columns
    assert "road_connectivity_pct" in telemetry.columns


def test_trained_model_and_shap_explainability():
    # Load model (trains a fast mini model or loads existing)
    model = load_trained_model()
    telemetry = generate_live_operational_telemetry(scenario_type="flash_flood_surge")
    
    X = telemetry[FEATURE_COLUMNS]
    predictions = model.predict(X)
    
    assert len(predictions) == len(telemetry)
    assert np.all(predictions >= 0.0)
    assert np.all(predictions <= 1.2) # Bound check
    
    # SHAP Explainer test
    explainer = DisasterExplainer(model)
    shap_vals, base_val = explainer.explain_zones(telemetry)
    
    assert shap_vals.shape == (len(telemetry), len(FEATURE_COLUMNS))
    
    # Test zone attribution
    sample_row = telemetry.iloc[0]
    sample_shap = shap_vals[0]
    attrib = explainer.get_zone_attribution(sample_row, sample_shap)
    
    assert "top_drivers" in attrib
    assert len(attrib["top_drivers"]) > 0
    assert "commander_briefing" in attrib
    assert len(attrib["commander_briefing"]) > 10
