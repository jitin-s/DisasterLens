"""
Tests for bilingual localization dictionary and AI Disaster Assistant Chatbot.
"""

import pytest
import pandas as pd
from app.translations import get_text, TRANSLATIONS
from app.chatbot import DisasterLensChatbot


def test_translations_keys_consistency():
    """Verifies that English and Hindi translation dictionaries have consistent keys."""
    en_keys = set(TRANSLATIONS["en"].keys())
    hi_keys = set(TRANSLATIONS["hi"].keys())
    
    # Check that crucial keys exist in both
    crucial_keys = [
        "portal_title", "portal_subtitle", "live_eoc_badge",
        "tab_map", "tab_why", "tab_dispatch", "tab_manifest",
        "tab_prevention", "tab_sos", "tab_chatbot",
        "kpi_monitored", "kpi_red", "kpi_orange", "kpi_exposed", "kpi_dispatched"
    ]
    for key in crucial_keys:
        assert key in en_keys, f"Missing {key} in English translations"
        assert key in hi_keys, f"Missing {key} in Hindi translations"
        
        # Test get_text function
        assert len(get_text(key, "en")) > 0
        assert len(get_text(key, "hi")) > 0


def test_chatbot_feature_inquiry():
    """Verifies that the chatbot answers portal feature inquiries in English and Hindi."""
    chatbot = DisasterLensChatbot()
    dummy_df = pd.DataFrame([{
        "zone_id": "IN-UK-01",
        "zone_name": "Joshimath",
        "state": "Uttarakhand",
        "triage_tier": "Catastrophic (Tier 1)",
        "opi_score": 85.0,
        "total_population": 25000
    }])
    summary_metrics = {
        "resource_breakdown": {
            "sar_boats": {"allocated": 10, "total_demand": 15},
            "medical_clinics": {"allocated": 5, "total_demand": 8}
        }
    }
    
    # English feature inquiry
    resp_en = chatbot.respond("What features does DisasterLens have?", dummy_df, summary_metrics, lang="en")
    assert "Features" in resp_en or "Interactive" in resp_en
    
    # Hindi feature inquiry
    resp_hi = chatbot.respond("इस पोर्टल की क्या विशेषताएं हैं?", dummy_df, summary_metrics, lang="hi")
    assert "विशेषताएं" in resp_hi or "नक्शा" in resp_hi


def test_chatbot_danger_status_inquiry():
    """Verifies that the chatbot queries live session state to report Red Alert districts."""
    chatbot = DisasterLensChatbot()
    dummy_df = pd.DataFrame([
        {
            "zone_id": "IN-UK-01",
            "zone_name": "Joshimath",
            "state": "Uttarakhand",
            "triage_tier": "Catastrophic (Tier 1)",
            "opi_score": 85.0,
            "total_population": 25000
        },
        {
            "zone_id": "IN-AS-01",
            "zone_name": "Majuli Island",
            "state": "Assam",
            "triage_tier": "Catastrophic (Tier 1)",
            "opi_score": 82.0,
            "total_population": 40000
        }
    ])
    summary_metrics = {"resource_breakdown": {}}
    
    resp = chatbot.respond("Which districts are in Red Alert?", dummy_df, summary_metrics, lang="en")
    assert "Joshimath" in resp
    assert "2 districts" in resp or "Red Alert" in resp
    
    resp_hi = chatbot.respond("कौनसे जिले रेड अलर्ट पर हैं?", dummy_df, summary_metrics, lang="hi")
    assert "Joshimath" in resp_hi
    assert "रेड अलर्ट" in resp_hi


def test_chatbot_district_search_keyword():
    """Verifies keyword search for specific district names like Chamoli or Wayanad."""
    chatbot = DisasterLensChatbot()
    dummy_df = pd.DataFrame([
        {
            "zone_id": "IN-UK-03",
            "zone_name": "Chamoli Gopeshwar",
            "state": "Uttarakhand",
            "priority_rank": 3,
            "opi_score": 79.4,
            "triage_tier": "Catastrophic (Tier 1)",
            "flood_gauge_m": 2.8,
            "road_connectivity_pct": 18.0,
            "total_population": 38000,
            "alloc_sar_boats": 4,
            "alloc_medical_clinics": 0,
            "alloc_ration_kits": 25
        }
    ])
    summary_metrics = {"resource_breakdown": {}}
    
    # English search for Chamoli
    resp_en = chatbot.respond("Tell me about Chamoli status and water level", dummy_df, summary_metrics, lang="en")
    assert "Chamoli" in resp_en
    assert "79.4" in resp_en
    assert "SEVERED" in resp_en
    
    # Hindi search for Chamoli
    resp_hi = chatbot.respond("चमोली जिले में क्या स्थिति है?", dummy_df, summary_metrics, lang="hi")
    assert "Chamoli" in resp_hi
    assert "79.4" in resp_hi


def test_chatbot_operational_topics():
    """Verifies keyword search for Red vs Orange difference, roads, kit, and manifest."""
    chatbot = DisasterLensChatbot()
    dummy_df = pd.DataFrame([])
    summary_metrics = {"resource_breakdown": {}}
    
    # Red vs Orange difference
    resp_diff = chatbot.respond("What is the difference between Red and Orange alert?", dummy_df, summary_metrics, lang="en")
    assert "Red Alert" in resp_diff and "Orange Alert" in resp_diff
    
    # 72-hour kit
    resp_kit = chatbot.respond("What should be in the 72 hour emergency kit?", dummy_df, summary_metrics, lang="en")
    assert "Water" in resp_kit and "First Aid" in resp_kit
    
    # CSV download
    resp_csv = chatbot.respond("How to download CSV manifest report?", dummy_df, summary_metrics, lang="en")
    assert "Download" in resp_csv and "CSV" in resp_csv
