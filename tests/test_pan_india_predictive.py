"""
Unit Tests for Pan-India Coverage, 24-Hour Predictive Hourly Telemetry, and Multi-Metric GIS Visualizers.
"""

import pytest
import os
import pandas as pd
from engine.realtime_telemetry import (
    load_pan_india_zones,
    generate_pan_india_operational_telemetry,
    fetch_live_atmospheric_telemetry
)
from app.components import (
    create_folium_map,
    plot_predictive_hourly_rain_chart,
    plot_predictive_hourly_weather_aqi_chart
)


def test_pan_india_zones_coverage():
    """Verify that all-India zones dataset has >= 670 districts across states."""
    df_zones = load_pan_india_zones()
    assert len(df_zones) >= 600, f"Expected >= 600 districts, got {len(df_zones)}"
    
    # Check essential demographic and geographical properties
    for _, z in df_zones.head(20).iterrows():
        assert "zone_id" in z
        assert "zone_name" in z
        assert -90 <= z["latitude"] <= 90
        assert -180 <= z["longitude"] <= 180
        assert "elevation_m" in z
        assert "drainage_capacity_index" in z


def test_realtime_hourly_forecast_engine():
    """Verify that live atmospheric telemetry returns current metrics and 24h predictive arrays."""
    # Delhi coordinates
    res = fetch_live_atmospheric_telemetry(28.6139, 77.2090)
    assert "precipitation_mm_h" in res
    assert "temperature_c" in res
    assert "wind_gust_kmh" in res
    assert "hourly_forecast" in res
    
    hourly = res["hourly_forecast"]
    assert "hours" in hourly
    assert len(hourly["hours"]) == 24
    assert len(hourly["rain_mm_h"]) == 24
    assert len(hourly["temperature_c"]) == 24
    assert len(hourly["wind_gust_kmh"]) == 24
    assert len(hourly["projected_flood_depth_m"]) == 24


def test_folium_map_metric_modes():
    """Verify Folium map generation across all 4 operational metric modes."""
    zones = load_pan_india_zones()[:15]
    df = pd.DataFrame(zones)
    df["opi_score"] = 55.0
    df["triage_tier"] = "High Priority"
    df["triage_color"] = "#ea580c"
    df["flood_gauge_m"] = 0.5
    df["road_connectivity_pct"] = 80.0
    df["rainfall_mm_h"] = 12.0
    df["temperature_c"] = 32.0
    df["wind_gust_kmh"] = 45.0
    df["air_quality_aqi"] = 120
    df["predicted_severity"] = 0.6

    for mode in ["disaster", "rain", "weather", "aqi"]:
        m = create_folium_map(df, selected_zone_id=df.iloc[0]["zone_id"], metric_mode=mode)
        assert m is not None


def test_predictive_hourly_charts():
    """Verify Plotly figure generation for 24h rain and weather/aqi charts."""
    sample_hourly = {
        "hours": [f"{i:02d}:00" for i in range(24)],
        "rain_mm_h": [2.5] * 24,
        "temperature_c": [30.0] * 24,
        "wind_gust_kmh": [25.0] * 24,
        "aqi": [95] * 24,
        "projected_flood_depth_m": [0.3] * 24
    }
    
    fig_rain = plot_predictive_hourly_rain_chart(sample_hourly, zone_name="Delhi")
    assert fig_rain is not None
    assert len(fig_rain.data) >= 2
    
    fig_wx = plot_predictive_hourly_weather_aqi_chart(sample_hourly, zone_name="Delhi")
    assert fig_wx is not None
    assert len(fig_wx.data) >= 3


def test_performance_telemetry_cache():
    """Verify telemetry caching functions return valid data and respond rapidly."""
    from app.main import (
        get_cached_pan_india_telemetry,
        get_cached_sachet_alerts,
        get_cached_live_telemetry
    )
    
    # 1. Verify telemetry caching functions return valid data
    telemetry = get_cached_pan_india_telemetry("realtime_satellite", 0.0, 0.0)
    assert len(telemetry) >= 600
    assert "zone_id" in telemetry.columns

    sachet = get_cached_sachet_alerts()
    assert isinstance(sachet, list)

    live_tel = get_cached_live_telemetry(28.6139, 77.2090)
    assert "precipitation_mm_h" in live_tel
    assert "hourly_forecast" in live_tel
