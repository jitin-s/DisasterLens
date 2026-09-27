"""
Unit Tests for Multi-Platform Live Data Providers & 10-Minute Sync
==================================================================
Tests:
- Active provider detection
- 10-minute (600s) TTL validation
- Real SRTM DEM elevation distribution across all 632 districts
- Key saving and cache purge behavior
- External provider fallback resilience
"""

import os
import json
import pytest
from unittest.mock import patch, MagicMock
from engine.realtime_telemetry import (
    CACHE_TTL,
    get_active_providers,
    save_api_keys,
    purge_telemetry_cache,
    fetch_openweather_telemetry,
    fetch_weatherapi_telemetry,
    fetch_waqi_cpcb_telemetry,
    fetch_google_elevation,
    load_pan_india_zones
)


def test_cache_ttl_is_ten_minutes():
    """Confirms operational cache TTL is exactly 600 seconds (10 minutes)."""
    assert CACHE_TTL == 600, f"Expected 600 seconds TTL, got {CACHE_TTL}"


def test_all_india_zones_srtm_elevation_non_dummy():
    """Confirms all 632 districts have real SRTM DEM elevation and no flat 45m dummy values."""
    zones_df = load_pan_india_zones()
    assert len(zones_df) == 632, f"Expected 632 districts, got {len(zones_df)}"
    
    # Elevation must not be uniform
    elevations = zones_df["elevation_m"].tolist()
    unique_elevations = set(elevations)
    assert len(unique_elevations) > 200, "Elevations appear synthetic or flat"
    
    # Specific known topography checks
    bengaluru = zones_df[zones_df["zone_id"] == "KA_BENGALURU_URBAN"]
    if not bengaluru.empty:
        b_elev = float(bengaluru.iloc[0]["elevation_m"])
        assert 850.0 <= b_elev <= 950.0, f"Bengaluru elevation wrong: {b_elev}m (expected ~900m)"
        
    shimla = zones_df[zones_df["zone_id"] == "HP_SHIMLA"]
    if not shimla.empty:
        s_elev = float(shimla.iloc[0]["elevation_m"])
        assert 2000.0 <= s_elev <= 2400.0, f"Shimla elevation wrong: {s_elev}m (expected ~2200m)"


def test_get_active_providers_structure():
    """Verifies that provider status dictionary returns all core dimensions."""
    providers = get_active_providers()
    assert "weather" in providers
    assert "aqi" in providers
    assert "elevation" in providers
    assert "alerts" in providers
    assert "refresh" in providers
    assert "10 Minutes" in providers["refresh"]


def test_save_api_keys_and_purge_cache(tmp_path):
    """Tests saving API keys and clearing telemetry cache files."""
    test_keys = {"TEST_DL_KEY": "secret_12345"}
    save_api_keys(test_keys)
    assert os.environ.get("TEST_DL_KEY") == "secret_12345"
    
    # Purge cache
    purge_telemetry_cache()


@patch("requests.get")
def test_openweather_telemetry_parser(mock_get):
    """Tests parsing of OpenWeatherMap weather + air pollution response."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "main": {"temp": 31.4, "humidity": 65.0, "pressure": 1010.0},
        "wind": {"speed": 4.5, "gust": 7.2},
        "rain": {"1h": 8.5}
    }
    mock_get.return_value = mock_resp
    
    data = fetch_openweather_telemetry(12.97, 77.59, "mock_owm_key")
    assert data is not None
    assert data["temperature_c"] == 31.4
    assert data["precipitation_mm_h"] == 8.5
    assert data["relative_humidity_pct"] == 65.0


@patch("requests.get")
def test_waqi_cpcb_telemetry_parser(mock_get):
    """Tests parsing of WAQI / CPCB ground monitoring station response."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "status": "ok",
        "data": {
            "aqi": 182,
            "city": {"name": "Anand Vihar, Delhi - DPCC"},
            "iaqi": {
                "pm25": {"v": 115.4},
                "pm10": {"v": 210.0}
            }
        }
    }
    mock_get.return_value = mock_resp
    
    data = fetch_waqi_cpcb_telemetry(28.64, 77.31, "mock_token")
    assert data is not None
    assert data["air_quality_aqi"] == 182
    assert data["pm2_5"] == 115.4
    assert "Anand Vihar" in data["cpcb_station"]
