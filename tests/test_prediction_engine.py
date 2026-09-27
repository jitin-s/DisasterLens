"""
tests/test_prediction_engine.py
================================
Unit tests for the multi-disaster prediction engine, golden hour evacuation,
and cascading risk chain calculations.
"""

import pytest
from engine.prediction_engine import (
    predict_flood_trajectory,
    predict_cyclone_trajectory,
    predict_landslide_probability,
    predict_heatwave_wetbulb,
    calculate_golden_hour,
    model_cascading_chains
)
from engine.sachet_feed import get_sachet_live_alerts, query_zone_sachet_status
from engine.realtime_telemetry import fetch_realtime_telemetry, batch_enrich_zones_with_telemetry


def test_flood_trajectory_low_elevation_poor_drainage():
    # In low elevation zone with poor drainage and heavy rain
    res = predict_flood_trajectory(rain_mm_h=45.0, elev_m=8.0, drainage="Poor", river_dist_km=1.5)
    assert res["forecast_6h_depth_m"] > 0
    assert res["forecast_12h_depth_m"] > res["forecast_6h_depth_m"]
    assert res["forecast_24h_depth_m"] > res["forecast_12h_depth_m"]
    assert res["flash_flood_probability_pct"] >= 50.0
    assert "Catastrophic" in res["inundation_tier"] or "Severe" in res["inundation_tier"]


def test_flood_trajectory_dry_high_elevation():
    # Dry conditions in high elevation
    res = predict_flood_trajectory(rain_mm_h=0.0, elev_m=1200.0, drainage="Good")
    assert res["forecast_6h_depth_m"] == 0.0
    assert res["forecast_24h_depth_m"] == 0.0
    assert res["flash_flood_probability_pct"] < 20.0
    assert res["inundation_tier"] == "Normal / Safe Runoff"


def test_cyclone_trajectory_super_cyclone():
    # Gale force > 222 km/h
    res = predict_cyclone_trajectory(wind_gust_kmh=235.0, pressure_hpa=910.0, dist_to_coast_km=10.0)
    assert "Super Cyclonic Storm" in res["imd_category"]
    assert res["severity_level"] == "EXTREME_CATASTROPHIC"
    assert res["storm_surge_height_m"] > 3.0
    assert res["gale_radius_km"] > 200.0
    assert res["coastal_inundation_risk"] == "CRITICAL"


def test_cyclone_trajectory_inland_normal():
    # Inland mild wind
    res = predict_cyclone_trajectory(wind_gust_kmh=20.0, pressure_hpa=1012.0, dist_to_coast_km=500.0)
    assert res["imd_category"] == "Normal Atmospheric Gradient"
    assert res["storm_surge_height_m"] == 0.0
    assert res["gale_radius_km"] == 0.0


def test_landslide_probability_himalayan_rain():
    # Chamoli or Wayanad heavy rain
    res = predict_landslide_probability(rain_mm_h=35.0, elev_m=2100.0, slope_deg=38.0)
    assert res["landslide_probability_pct"] >= 50.0
    assert res["critical_rainfall_threshold_exceeded"] is True
    assert res["road_cutoff_risk_pct"] > 40.0
    assert res["debris_flow_volume_m3"] > 0


def test_landslide_probability_plains():
    # Delhi or Patna flat plains
    res = predict_landslide_probability(rain_mm_h=50.0, elev_m=150.0, slope_deg=2.0)
    assert res["landslide_probability_pct"] == 0.0
    assert res["road_cutoff_risk_pct"] == 0.0


def test_heatwave_wetbulb_stull_formula():
    # Extreme heat + humidity (e.g. 44C, 70% RH)
    res = predict_heatwave_wetbulb(temp_c=44.0, humidity_pct=70.0)
    assert res["wet_bulb_temp_c"] >= 34.0
    assert "LETHAL" in res["thermal_tier"] or "EXTREME DANGER" in res["thermal_tier"]
    assert res["physiological_threshold_warning"] is True

    # Mild weather (25C, 40% RH)
    res_mild = predict_heatwave_wetbulb(temp_c=25.0, humidity_pct=40.0)
    assert res_mild["wet_bulb_temp_c"] < 20.0
    assert res_mild["physiological_threshold_warning"] is False


def test_golden_hour_countdown():
    # Flood rising rapidly in poor drainage
    res = calculate_golden_hour(flood_depth_m=0.10, rain_mm_h=40.0, drainage="Poor", elev_m=5.0)
    assert res["tau_crit_hours"] < 15.0
    assert "mins" in res["time_remaining_str"] or "h" in res["time_remaining_str"]

    # Roads already submerged (> 0.35m)
    res_submerged = calculate_golden_hour(flood_depth_m=0.50, rain_mm_h=20.0)
    assert res_submerged["tau_crit_hours"] == 0.0
    assert "ROAD SEVERED" in res_submerged["evacuation_status"]


def test_cascading_chains():
    zone = {"elevation_m": 12.0, "dist_to_coast_km": 15.0}
    telemetry = {"wind_gust_kmh": 125.0, "precipitation_mm_h": 35.0, "temperature_c": 30.0, "air_quality_aqi": 80.0}
    chains = model_cascading_chains(zone, telemetry)
    assert len(chains) >= 1
    chain_ids = [c["chain_id"] for c in chains]
    assert any("GRID" in cid or "SURGE" in cid for cid in chain_ids)


def test_sachet_feed_integration():
    alerts = get_sachet_live_alerts()
    assert isinstance(alerts, list)
    assert len(alerts) > 0
    first = alerts[0]
    assert "identifier" in first
    assert "headline" in first
    assert "severity" in first

    status = query_zone_sachet_status(zone_id="ZONE_01", alerts=alerts)
    assert "has_active_alert" in status
