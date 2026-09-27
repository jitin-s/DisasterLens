"""
DisasterLens UI Components: Maps, Charts, KPI Metric Banners, and Manifest Tables
Light-theme, high-contrast, accessible emergency command UI components.
"""

import textwrap
from typing import Dict, Any, List
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import folium
from folium import plugins


def create_folium_map(
    df: pd.DataFrame,
    selected_zone_id: str = None,
    tile_provider: str = "Google Satellite Hybrid",
    metric_mode: str = "disaster",
    mapbox_api_key: str = None
) -> folium.Map:
    """
    Renders an interactive real GIS map of India with Google Maps & ISRO Bhuvan satellite layers,
    floating metric legend, and dynamic coloring based on the selected operational mode:
    - 'disaster': OPI Priority Triage
    - 'rain': Precipitation Radar & Inundation Depth
    - 'weather': Temperature & Wind Gust Velocity
    - 'aqi': Air Quality Index & PM2.5 Concentration
    """
    if len(df) > 0:
        center_lat = float(df["latitude"].mean())
        center_lon = float(df["longitude"].mean())
        zoom_start = 5 if len(df) > 30 else (7 if len(df) > 5 else 9)
    else:
        center_lat = 22.5
        center_lon = 82.5
        zoom_start = 5

    # Base Folium Map Container
    m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom_start, tiles=None, control_scale=True)

    # 1. Base Tile Layers (Google Maps & ISRO Bhuvan Satellite)
    folium.TileLayer(
        tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
        attr="Google Satellite &copy; Google Maps",
        name="🛰️ Google Satellite Hybrid",
        max_zoom=20,
        show=("Google Satellite" in tile_provider or "Satellite" in tile_provider)
    ).add_to(m)

    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Satellite Imagery: ISRO Bhuvan &copy; NRSC / Earthstar",
        name="🇮🇳 ISRO Bhuvan Satellite (Govt of India)",
        max_zoom=19,
        show=("Bhuvan" in tile_provider)
    ).add_to(m)

    folium.TileLayer(
        tiles="https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}",
        attr="Google Maps &copy; Google",
        name="🗺️ Google Maps Street",
        max_zoom=20,
        show=("Street" in tile_provider or "Road" in tile_provider)
    ).add_to(m)

    folium.TileLayer(
        tiles="https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}",
        attr="Google Maps &copy; Google Terrain",
        name="⛰️ Google Maps Terrain",
        max_zoom=20,
        show=("Terrain" in tile_provider)
    ).add_to(m)

    folium.TileLayer(
        tiles="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        attr="&copy; OpenStreetMap contributors",
        name="🌐 OpenStreetMap India Official",
        max_zoom=19,
        show=("OpenStreetMap" in tile_provider)
    ).add_to(m)

    # 2. Add Location Markers with Mode-Specific Aesthetics
    for _, row in df.iterrows():
        zone_id = row["zone_id"]
        zone_name = row["zone_name"]
        state = row.get("state", "India")
        hazard_type = row.get("primary_hazard", row.get("region_type", "Multi-Hazard"))
        pop = int(row.get("total_population", 0))
        facilities = ", ".join(row.get("critical_facilities", []))
        
        opi = float(row.get("opi_score", 0.0))
        sev = float(row.get("predicted_severity", 0.0))
        flood = float(row.get("flood_gauge_m", 0.0))
        elev = float(row.get("elevation_m", 0.0))
        road = float(row.get("road_connectivity_pct", 100.0))
        rain = float(row.get("precipitation_mm_h", row.get("rainfall_mm_h", 0.0)))
        wind = float(row.get("wind_gust_kmh", 0.0))
        temp = float(row.get("temperature_c", 28.0))
        aqi = int(row.get("air_quality_aqi", 75))
        pm25 = float(row.get("pm2_5", 35.0))
        tier = row.get("triage_tier", "Tier")

        # Color & tooltip determination according to metric_mode
        if metric_mode == "rain":
            if rain >= 35.0:
                color = "#dc2626"  # Torrential Deluge (Red)
                sub_label = f"Torrential Rain ({rain:.1f} mm/h)"
            elif rain >= 15.0:
                color = "#ea580c"  # Heavy Rain (Orange)
                sub_label = f"Heavy Rain ({rain:.1f} mm/h)"
            elif rain >= 5.0:
                color = "#0284c7"  # Moderate Rain (Sky Blue)
                sub_label = f"Moderate Rain ({rain:.1f} mm/h)"
            elif rain >= 0.5:
                color = "#38bdf8"  # Light Rain (Light Blue)
                sub_label = f"Light Showers ({rain:.1f} mm/h)"
            else:
                color = "#10b981"  # Trace / Dry (Green)
                sub_label = "Dry / Clear"
        elif metric_mode == "weather":
            if temp >= 42.0 or wind >= 80.0:
                color = "#991b1b"  # Severe Heat/Gale (Dark Red)
                sub_label = f"Severe Thermal/Gale ({temp:.1f}°C, {wind:.0f} km/h)"
            elif temp >= 36.0 or wind >= 50.0:
                color = "#ea580c"  # High Heat (Orange)
                sub_label = f"High Heat / Gusts ({temp:.1f}°C, {wind:.0f} km/h)"
            elif temp >= 28.0:
                color = "#f59e0b"  # Warm (Amber)
                sub_label = f"Warm ({temp:.1f}°C, {wind:.0f} km/h)"
            elif temp >= 18.0:
                color = "#10b981"  # Mild / Pleasant (Green)
                sub_label = f"Mild ({temp:.1f}°C, {wind:.0f} km/h)"
            else:
                color = "#0284c7"  # Cold (Blue)
                sub_label = f"Cold ({temp:.1f}°C, {wind:.0f} km/h)"
        elif metric_mode == "aqi":
            if aqi > 300:
                color = "#7f1d1d"  # Hazardous (Dark Maroon)
                sub_label = f"Hazardous AQI {aqi}"
            elif aqi > 200:
                color = "#9333ea"  # Very Unhealthy (Purple)
                sub_label = f"Very Unhealthy AQI {aqi}"
            elif aqi > 150:
                color = "#dc2626"  # Unhealthy (Red)
                sub_label = f"Unhealthy AQI {aqi}"
            elif aqi > 100:
                color = "#f97316"  # Moderate/Sensitive (Orange)
                sub_label = f"Moderate AQI {aqi}"
            elif aqi > 50:
                color = "#eab308"  # Moderate (Yellow)
                sub_label = f"Moderate AQI {aqi}"
            else:
                color = "#16a34a"  # Good (Green)
                sub_label = f"Good AQI {aqi}"
        else: # "disaster" default
            color = row.get("triage_color", "#16a34a")
            sub_label = f"OPI {opi:.1f} • {tier}"

        is_selected = (zone_id == selected_zone_id)
        border_weight = 4 if is_selected else 2
        border_color = "#f59e0b" if is_selected else "#ffffff"
        radius = 8 + int(np.sqrt(max(pop, 1000)) / 16.0)
        radius = min(radius, 22)

        road_status_badge = f'<span style="background-color: #fee2e2; color: #b91c1c; padding: 2px 6px; border-radius: 4px; font-weight: bold;">🚨 SEVERED ({road:.1f}%)</span>' if road < 30 else f'<span style="color: #166534; font-weight: bold;">Intact ({road:.1f}%)</span>'

        # Optimize DOM payload: detailed HTML popup for selected and high-risk nodes; lightweight for background nodes
        is_high_risk = (opi >= 40.0 or rain >= 15.0 or aqi > 200 or wind >= 60.0)
        if len(df) <= 80 or is_selected or is_high_risk:
            popup_html = f"""
            <div style="font-family: 'Plus Jakarta Sans', Arial, sans-serif; font-size: 12px; width: 270px; line-height: 1.45; background-color: #111827; color: #f8fafc; padding: 6px; border-radius: 6px;">
                <div style="background-color: {color}; color: white; padding: 7px 10px; border-radius: 6px; font-weight: 800; font-size: 13px; margin-bottom: 8px;">
                    {zone_id}: {zone_name} ({state})
                </div>
                <div style="margin-bottom: 4px; color: #cbd5e1;"><strong>Active Status:</strong> <span style="font-weight: 700; color: {color};">{sub_label}</span></div>
                <div style="margin-bottom: 4px; color: #cbd5e1;"><strong>Hazard Type:</strong> <span style="color: #f87171; font-weight: 600;">{hazard_type}</span></div>
                <div style="margin-bottom: 4px; color: #cbd5e1;"><strong>Operational Priority:</strong> <span style="font-size: 14px; font-weight: 800; color: {color};">{opi:.1f}</span> / 100 ({tier})</div>
                <div style="margin-bottom: 4px; color: #cbd5e1;"><strong>Sat. Rain Rate:</strong> <b style="color: #38bdf8;">{rain:.1f} mm/h</b> | Surge: <b style="color: #38bdf8;">{flood:.2f} m</b></div>
                <div style="margin-bottom: 4px; color: #cbd5e1;"><strong>Weather Telemetry:</strong> {temp:.1f}°C | Gusts: {wind:.0f} km/h</div>
                <div style="margin-bottom: 4px; color: #cbd5e1;"><strong>Air Quality:</strong> AQI <b style="color: #c084fc;">{aqi}</b> | PM2.5: {pm25:.1f} µg/m³</div>
                <div style="margin-bottom: 4px; color: #cbd5e1;"><strong>Transit Access:</strong> {road_status_badge}</div>
                <div style="margin-top: 6px; padding-top: 6px; border-top: 1px solid #334155; font-size: 11px; color: #94a3b8;">
                    <strong>Population:</strong> {pop:,} | Elev: {elev:.0f}m ASL
                </div>
            </div>
            """
            popup_obj = folium.Popup(popup_html, max_width=290)
        else:
            popup_obj = folium.Popup(
                f'<div style="font-family: sans-serif; font-size: 12px; color: #0f172a; padding: 4px;"><b>{zone_name} ({state})</b><br/><span style="color: {color}; font-weight: 700;">{sub_label}</span><br/><span style="color: #64748b; font-size: 11px;">OPI: {opi:.1f} | Rain: {rain:.1f}mm/h</span></div>',
                max_width=220
            )

        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=radius,
            color=border_color,
            weight=border_weight,
            fill=True,
            fill_color=color,
            fill_opacity=0.88,
            popup=popup_obj,
            tooltip=f"{zone_name} ({state}) • {sub_label}"
        ).add_to(m)

    # 3. Dynamic Floating Legend matching metric_mode
    if metric_mode == "rain":
        legend_content = """
        <div style="font-weight: 800; font-size: 12px; margin-bottom: 6px; color: #f8fafc; text-transform: uppercase; border-bottom: 1px solid #334155; padding-bottom: 4px;">🌧️ Sat. Rain Intensity</div>
        <div style="display: flex; align-items: center; margin-bottom: 4px;"><span style="height: 11px; width: 11px; background-color: #dc2626; border-radius: 50%; display: inline-block; margin-right: 7px;"></span><span style="font-weight: 700; color: #fca5a5;">Torrential (≥35 mm/h)</span></div>
        <div style="display: flex; align-items: center; margin-bottom: 4px;"><span style="height: 11px; width: 11px; background-color: #ea580c; border-radius: 50%; display: inline-block; margin-right: 7px;"></span><span style="font-weight: 700; color: #fdba74;">Heavy (15-34 mm/h)</span></div>
        <div style="display: flex; align-items: center; margin-bottom: 4px;"><span style="height: 11px; width: 11px; background-color: #0284c7; border-radius: 50%; display: inline-block; margin-right: 7px;"></span><span style="font-weight: 700; color: #7dd3fc;">Moderate (5-14 mm/h)</span></div>
        <div style="display: flex; align-items: center; margin-bottom: 4px;"><span style="height: 11px; width: 11px; background-color: #38bdf8; border-radius: 50%; display: inline-block; margin-right: 7px;"></span><span style="font-weight: 700; color: #bae6fd;">Light Showers (&lt;5 mm/h)</span></div>
        <div style="display: flex; align-items: center;"><span style="height: 11px; width: 11px; background-color: #10b981; border-radius: 50%; display: inline-block; margin-right: 7px;"></span><span style="font-weight: 700; color: #86efac;">Dry / Clear</span></div>
        """
    elif metric_mode == "weather":
        legend_content = """
        <div style="font-weight: 800; font-size: 12px; margin-bottom: 6px; color: #f8fafc; text-transform: uppercase; border-bottom: 1px solid #334155; padding-bottom: 4px;">🌡️ Thermal & Wind Scale</div>
        <div style="display: flex; align-items: center; margin-bottom: 4px;"><span style="height: 11px; width: 11px; background-color: #991b1b; border-radius: 50%; display: inline-block; margin-right: 7px;"></span><span style="font-weight: 700; color: #fca5a5;">Severe (≥42°C or ≥80 km/h)</span></div>
        <div style="display: flex; align-items: center; margin-bottom: 4px;"><span style="height: 11px; width: 11px; background-color: #ea580c; border-radius: 50%; display: inline-block; margin-right: 7px;"></span><span style="font-weight: 700; color: #fdba74;">High Heat (36-41°C)</span></div>
        <div style="display: flex; align-items: center; margin-bottom: 4px;"><span style="height: 11px; width: 11px; background-color: #f59e0b; border-radius: 50%; display: inline-block; margin-right: 7px;"></span><span style="font-weight: 700; color: #fde68a;">Warm (28-35°C)</span></div>
        <div style="display: flex; align-items: center; margin-bottom: 4px;"><span style="height: 11px; width: 11px; background-color: #10b981; border-radius: 50%; display: inline-block; margin-right: 7px;"></span><span style="font-weight: 700; color: #86efac;">Mild (18-27°C)</span></div>
        <div style="display: flex; align-items: center;"><span style="height: 11px; width: 11px; background-color: #0284c7; border-radius: 50%; display: inline-block; margin-right: 7px;"></span><span style="font-weight: 700; color: #7dd3fc;">Cold (&lt;18°C)</span></div>
        """
    elif metric_mode == "aqi":
        legend_content = """
        <div style="font-weight: 800; font-size: 12px; margin-bottom: 6px; color: #f8fafc; text-transform: uppercase; border-bottom: 1px solid #334155; padding-bottom: 4px;">🌫️ Air Quality Index (AQI)</div>
        <div style="display: flex; align-items: center; margin-bottom: 4px;"><span style="height: 11px; width: 11px; background-color: #7f1d1d; border-radius: 50%; display: inline-block; margin-right: 7px;"></span><span style="font-weight: 700; color: #fca5a5;">Hazardous (&gt;300)</span></div>
        <div style="display: flex; align-items: center; margin-bottom: 4px;"><span style="height: 11px; width: 11px; background-color: #9333ea; border-radius: 50%; display: inline-block; margin-right: 7px;"></span><span style="font-weight: 700; color: #d8b4fe;">Very Unhealthy (201-300)</span></div>
        <div style="display: flex; align-items: center; margin-bottom: 4px;"><span style="height: 11px; width: 11px; background-color: #dc2626; border-radius: 50%; display: inline-block; margin-right: 7px;"></span><span style="font-weight: 700; color: #f87171;">Unhealthy (151-200)</span></div>
        <div style="display: flex; align-items: center; margin-bottom: 4px;"><span style="height: 11px; width: 11px; background-color: #f97316; border-radius: 50%; display: inline-block; margin-right: 7px;"></span><span style="font-weight: 700; color: #fb923c;">Moderate/Sens. (101-150)</span></div>
        <div style="display: flex; align-items: center; margin-bottom: 4px;"><span style="height: 11px; width: 11px; background-color: #eab308; border-radius: 50%; display: inline-block; margin-right: 7px;"></span><span style="font-weight: 700; color: #facc15;">Moderate (51-100)</span></div>
        <div style="display: flex; align-items: center;"><span style="height: 11px; width: 11px; background-color: #16a34a; border-radius: 50%; display: inline-block; margin-right: 7px;"></span><span style="font-weight: 700; color: #4ade80;">Good (0-50)</span></div>
        """
    else:
        legend_content = """
        <div style="font-weight: 800; font-size: 12px; margin-bottom: 6px; color: #f8fafc; text-transform: uppercase; border-bottom: 1px solid #334155; padding-bottom: 4px;">🚦 Priority Triage Legend</div>
        <div style="display: flex; align-items: center; margin-bottom: 4px;"><span style="height: 11px; width: 11px; background-color: #D32F2F; border-radius: 50%; display: inline-block; margin-right: 7px;"></span><span style="font-weight: 700; color: #fca5a5;">Catastrophic (≥70)</span></div>
        <div style="display: flex; align-items: center; margin-bottom: 4px;"><span style="height: 11px; width: 11px; background-color: #F57C00; border-radius: 50%; display: inline-block; margin-right: 7px;"></span><span style="font-weight: 700; color: #fdba74;">High Priority (50-69)</span></div>
        <div style="display: flex; align-items: center; margin-bottom: 4px;"><span style="height: 11px; width: 11px; background-color: #FBC02D; border-radius: 50%; display: inline-block; margin-right: 7px;"></span><span style="font-weight: 700; color: #fde68a;">Moderate (30-49)</span></div>
        <div style="display: flex; align-items: center;"><span style="height: 11px; width: 11px; background-color: #388E3C; border-radius: 50%; display: inline-block; margin-right: 7px;"></span><span style="font-weight: 700; color: #86efac;">Low Risk (&lt;30)</span></div>
        """

    legend_html = f"""
    <div style="
        position: fixed; 
        bottom: 25px; 
        right: 25px; 
        z-index: 9999; 
        background-color: rgba(17, 24, 39, 0.94);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 10px;
        padding: 12px 16px;
        font-family: 'Plus Jakarta Sans', Arial, sans-serif;
        font-size: 11.5px;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.5);
        min-width: 180px;
        backdrop-filter: blur(8px);
    ">
        {legend_content}
        <div style="margin-top: 6px; padding-top: 4px; border-top: 1px dashed #334155; font-size: 10px; color: #94a3b8;">
            ⚪ Marker Size = Population
        </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    # Add Layer Control for Google Maps & ISRO Bhuvan satellite toggle
    folium.LayerControl(position="topright", collapsed=False).add_to(m)

    return m


def plot_shap_drivers(attribution: Dict[str, Any]) -> go.Figure:
    """
    Renders an explainable SHAP contribution horizontal bar chart for a selected sector.
    """
    drivers = attribution.get("top_drivers", [])
    if not drivers:
        return go.Figure()
        
    features = [d["label"] for d in reversed(drivers)]
    shap_vals = [d["shap_value"] for d in reversed(drivers)]
    colors = ["#dc2626" if val > 0 else "#16a34a" for val in shap_vals]
    
    fig = go.Figure(go.Bar(
        x=shap_vals,
        y=features,
        orientation='h',
        marker=dict(color=colors, line=dict(width=1, color="#ffffff")),
        text=[f"{val:+.3f}" for val in shap_vals],
        textposition="auto",
        textfont=dict(size=12, color="#ffffff")
    ))
    
    fig.update_layout(
        title=f"<b>XAI Risk Attribution: {attribution['zone_id']} ({attribution['zone_name']})</b>",
        xaxis_title="SHAP Marginal Contribution (Push Towards Severity)",
        yaxis_title="",
        margin=dict(l=20, r=20, t=40, b=20),
        height=330,
        template="plotly_dark",
        paper_bgcolor="#111827",
        plot_bgcolor="#0b0f19",
        font=dict(family="Plus Jakarta Sans, sans-serif", color="#f8fafc")
    )
    fig.add_vline(x=0, line_width=1.5, line_dash="dash", line_color="#94a3b8")
    return fig


def plot_resource_balance(summary_metrics: Dict[str, Any]) -> go.Figure:
    """
    Renders a grouped bar chart comparing Total Demand, Units Allocated, and Remaining Deficit.
    """
    breakdown = summary_metrics.get("resource_breakdown", {})
    labels = [b["label"] for b in breakdown.values()]
    demands = [b["total_demand"] for b in breakdown.values()]
    allocated = [b["allocated"] for b in breakdown.values()]
    deficits = [b["unmet_deficit"] for b in breakdown.values()]
    
    fig = go.Figure(data=[
        go.Bar(name='Required Demand', x=labels, y=demands, marker_color='#64748b'),
        go.Bar(name='Dispatched Units', x=labels, y=allocated, marker_color='#0284c7'),
        go.Bar(name='Unmet Deficit', x=labels, y=deficits, marker_color='#ef4444')
    ])
    
    fig.update_layout(
        barmode='group',
        title="<b>National Disaster Resource Allocation & Demand Satiation</b>",
        yaxis_title="Units",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=20, r=20, t=50, b=20),
        height=330,
        template="plotly_dark",
        paper_bgcolor="#111827",
        plot_bgcolor="#0b0f19",
        font=dict(family="Plus Jakarta Sans, sans-serif", color="#f8fafc")
    )
    return fig


def plot_radar_zone_comparison(df: pd.DataFrame, zone_ids: List[str]) -> go.Figure:
    """
    Plots a multi-axis radar chart comparing Hazard, Vulnerability, and Coping Deficit across zones.
    """
    categories = [
        'Flood Hazard', 'Wind Hazard', 'Demographic Frailty',
        'Infra Deficit', 'Inverted Coping'
    ]
    
    fig = go.Figure()
    colors = ["#dc2626", "#2563eb", "#ea580c", "#16a34a"]
    
    for idx, z_id in enumerate(zone_ids[:4]):
        zone_df = df[df["zone_id"] == z_id]
        if zone_df.empty:
            continue
        row = zone_df.iloc[0]
        
        flood_norm = min(1.0, row.get("flood_gauge_m", 0.0) / 3.0)
        wind_norm = min(1.0, row.get("wind_gust_kmh", 0.0) / 160.0)
        vuln_norm = row.get("vulnerability_score", 0.5)
        infra_norm = row.get("infrastructure_deficit", 0.5)
        coping_inv = 1.0 - row.get("coping_capacity", 0.5)
        
        vals = [flood_norm, wind_norm, vuln_norm, infra_norm, coping_inv]
        vals.append(vals[0])
        
        c = colors[idx % len(colors)]
        fig.add_trace(go.Scatterpolar(
            r=vals,
            theta=categories + [categories[0]],
            fill='toself',
            name=f"{row['zone_id']} ({row['zone_name']})",
            line_color=c,
            opacity=0.6
        ))
        
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 1], gridcolor="#334155"),
            bgcolor="#0b0f19"
        ),
        showlegend=True,
        title="<b>Multi-Dimensional Disaster Profile Comparison</b>",
        height=340,
        margin=dict(l=30, r=30, t=40, b=20),
        template="plotly_dark",
        paper_bgcolor="#111827",
        plot_bgcolor="#0b0f19",
        font=dict(family="Plus Jakarta Sans, sans-serif", color="#f8fafc")
    )
    return fig


def plot_flood_trajectory(forecast: Dict[str, Any], zone_name: str = "") -> go.Figure:
    """
    Renders 24-hour flood inundation trajectory curve with critical infrastructure thresholds.
    """
    hours = [0, 6, 12, 24]
    depths = [
        forecast.get("current_depth_m", 0.0),
        forecast.get("forecast_6h_depth_m", 0.0),
        forecast.get("forecast_12h_depth_m", 0.0),
        forecast.get("forecast_24h_depth_m", 0.0)
    ]

    fig = go.Figure()

    # Fill area under curve
    fig.add_trace(go.Scatter(
        x=hours,
        y=depths,
        mode="lines+markers",
        name="Water Depth (m)",
        line=dict(color="#38bdf8", width=3.5),
        marker=dict(size=9, color="#0284c7", symbol="diamond"),
        fill="tozeroy",
        fillcolor="rgba(56, 189, 248, 0.2)"
    ))

    # Threshold: Road Severance (0.35m)
    fig.add_hline(
        y=0.35,
        line_dash="dot",
        line_color="#ef4444",
        annotation_text="Car/Ambulance Cutoff (0.35m)",
        annotation_position="top left",
        annotation_font=dict(size=10, color="#f87171")
    )

    # Threshold: Ground Floor Submersion (1.2m)
    fig.add_hline(
        y=1.2,
        line_dash="dash",
        line_color="#c084fc",
        annotation_text="Ground Floor Inundation (1.2m)",
        annotation_position="top left",
        annotation_font=dict(size=10, color="#d8b4fe")
    )

    fig.update_layout(
        title=f"<b>24-Hour Hydrological Inundation Trajectory: {zone_name}</b>",
        xaxis_title="Forecast Horizon (Hours from Present)",
        yaxis_title="Standing Water Depth (Meters)",
        xaxis=dict(tickvals=[0, 6, 12, 24], ticktext=["Now (T+0)", "+6 Hours", "+12 Hours", "+24 Hours"]),
        yaxis=dict(rangemode="tozero"),
        height=320,
        margin=dict(l=20, r=20, t=45, b=20),
        template="plotly_dark",
        paper_bgcolor="#111827",
        plot_bgcolor="#0b0f19",
        font=dict(family="Plus Jakarta Sans, sans-serif", color="#f8fafc")
    )
    return fig


def plot_atmospheric_radar_profile(telemetry: Dict[str, Any], zone_name: str = "") -> go.Figure:
    """
    Renders bar telemetry comparing rainfall, wind gusts, AQI, and atmospheric pressure.
    """
    rain = float(telemetry.get("precipitation_mm_h", telemetry.get("rainfall_mm_h", 0.0)))
    wind = float(telemetry.get("wind_gust_kmh", 0.0))
    aqi = float(telemetry.get("air_quality_aqi", telemetry.get("pm2_5", 45.0)))
    temp = float(telemetry.get("temperature_c", 28.0))

    metrics = ["Rain (mm/h)", "Wind (km/h)", "AQI / PM2.5", "Temp (°C)"]
    vals = [rain, wind, aqi, temp]
    colors = [
        "#0284c7" if rain < 30 else "#dc2626",
        "#0d9488" if wind < 60 else "#ea580c",
        "#16a34a" if aqi < 100 else "#dc2626",
        "#f59e0b" if temp < 38 else "#7f1d1d"
    ]

    fig = go.Figure(go.Bar(
        x=metrics,
        y=vals,
        marker=dict(color=colors, line=dict(width=1, color="#ffffff")),
        text=[f"{v:.1f}" for v in vals],
        textposition="auto",
        textfont=dict(size=12, color="#ffffff", family="Plus Jakarta Sans")
    ))

    fig.update_layout(
        title=f"<b>Real-Time Atmospheric Telemetry: {zone_name}</b>",
        yaxis_title="Sensor Value",
        height=280,
        margin=dict(l=20, r=20, t=45, b=20),
        template="plotly_dark",
        paper_bgcolor="#111827",
        plot_bgcolor="#0b0f19",
        font=dict(family="Plus Jakarta Sans, sans-serif", color="#f8fafc")
    )
    return fig


def clean_html(html_str: str) -> str:
    """Strips leading and trailing whitespace from every line so CommonMark cannot parse indented lines as code."""
    if not html_str:
        return ""
    return "\n".join(line.strip() for line in html_str.strip().splitlines() if line.strip())


def render_golden_hour_card_html(gh_data: Dict[str, Any]) -> str:
    """Renders high-visibility Golden-Hour evacuation countdown card."""
    tau_str = gh_data.get("time_remaining_str", "--")
    status = gh_data.get("evacuation_status", "ACTIVE")
    color = gh_data.get("evacuation_color", "#2563eb")
    action = gh_data.get("recommended_action", "")
    rate = gh_data.get("inundation_rate_cm_h", 0.0)
    clearance = gh_data.get("navigable_clearance_cm", 0.0)

    raw_html = f"""
    <div style="background-color: #111827; border: 1.5px solid {color}; border-radius: 12px; padding: 18px 22px; margin-bottom: 16px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; margin-bottom: 10px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 26px;">⏳</span>
                <div>
                    <div style="font-size: 11px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.8px; color: #94a3b8;">
                        CRITICAL LIFE SAFETY COUNTDOWN (&tau;<sub>crit</sub>)
                    </div>
                    <div style="font-size: 17px; font-weight: 800; color: #f8fafc;">
                        Golden-Hour Evacuation Window
                    </div>
                </div>
            </div>
            <div style="background-color: {color}; color: #ffffff; padding: 6px 14px; border-radius: 20px; font-weight: 800; font-size: 13px; letter-spacing: 0.3px; box-shadow: 0 0 10px {color};">
                {status}
            </div>
        </div>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 12px; margin-top: 12px; margin-bottom: 14px; background-color: #0d131f; padding: 12px; border-radius: 8px; border: 1px solid #1e293b;">
            <div>
                <div style="font-size: 11px; color: #94a3b8; font-weight: 600;">TIME UNTIL ROAD SEVERANCE</div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 24px; font-weight: 800; color: {color};">{tau_str}</div>
            </div>
            <div>
                <div style="font-size: 11px; color: #94a3b8; font-weight: 600;">INUNDATION RATE</div>
                <div style="font-size: 20px; font-weight: 800; color: #f8fafc;">{rate} cm/hour</div>
            </div>
            <div>
                <div style="font-size: 11px; color: #94a3b8; font-weight: 600;">ROAD CLEARANCE MARGIN</div>
                <div style="font-size: 20px; font-weight: 800; color: #38bdf8;">{clearance} cm left</div>
            </div>
        </div>
        <div style="border-left: 3.5px solid {color}; padding-left: 12px; font-size: 12.5px; line-height: 1.5; color: #cbd5e1;">
            <strong>Mandated Citizen & Rescue Directive:</strong> {action}
        </div>
    </div>
    """
    return clean_html(raw_html)


def render_cascading_chains_html(chains: List[Dict[str, Any]]) -> str:
    """Renders cascading multi-hazard compounding chain cards."""
    cards_html = ""
    for ch in chains:
        cid = ch.get("chain_id", "CHAIN")
        name = ch.get("name", "Hazard Coupling")
        prob = ch.get("probability_pct", 50.0)
        trigger = ch.get("trigger_vector", "")
        effects = ch.get("cascading_effects", [])
        mitig = ch.get("priority_mitigation", "")

        sev_color = "#dc2626" if prob >= 75 else ("#ea580c" if prob >= 40 else "#2563eb")
        effects_li = "".join([f"<li style='margin-bottom: 4px;'>{ef}</li>" for ef in effects])

        card_raw = f"""
        <div style="background-color: #111827; border: 1px solid #1e293b; border-top: 3.5px solid {sev_color}; border-radius: 8px; padding: 14px 18px; margin-bottom: 12px; box-shadow: 0 4px 14px rgba(0,0,0,0.3);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <div style="font-weight: 800; font-size: 14px; color: #f8fafc;">
                    ⚡ {name}
                </div>
                <span style="background-color: rgba(239, 68, 68, 0.15); color: {sev_color}; border: 1px solid {sev_color}; padding: 3px 8px; border-radius: 12px; font-weight: 800; font-size: 11.5px;">
                    Trigger Risk: {prob:.1f}%
                </span>
            </div>
            <div style="font-size: 12px; color: #94a3b8; margin-bottom: 8px;">
                <strong style="color: #cbd5e1;">Primary Trigger:</strong> {trigger}
            </div>
            <div style="font-size: 12px; color: #cbd5e1; margin-bottom: 8px;">
                <strong style="color: #f8fafc;">Cascading Sequence:</strong>
                <ul style="margin: 4px 0 0 18px; padding: 0; color: #cbd5e1;">
                    {effects_li}
                </ul>
            </div>
            <div style="background-color: #1e293b; border: 1px solid #334155; padding: 8px 12px; border-radius: 6px; font-size: 11.5px; color: #e2e8f0; border-left: 3px solid #38bdf8;">
                <strong style="color: #38bdf8;">Intervention Strategy:</strong> {mitig}
            </div>
        </div>
        """
        cards_html += clean_html(card_raw) + "\n"
    return cards_html


def plot_predictive_hourly_rain_chart(hourly: Dict[str, Any], zone_name: str = "") -> go.Figure:
    """
    Renders 24-hour predictive hourly rainfall (mm/h) and projected flood accumulation (m).
    """
    hours = hourly.get("hours", [f"{i:02d}:00" for i in range(24)])
    rain = hourly.get("rain_mm_h", [0.0] * 24)
    flood = hourly.get("projected_flood_depth_m", [0.0] * 24)

    fig = go.Figure()

    # Hourly rain bars
    bar_colors = ["#dc2626" if r >= 25 else ("#ea580c" if r >= 10 else "#0284c7") for r in rain]
    fig.add_trace(go.Bar(
        x=hours,
        y=rain,
        name="Hourly Rain (mm/h)",
        marker_color=bar_colors,
        yaxis="y1"
    ))

    # Projected flood depth line
    fig.add_trace(go.Scatter(
        x=hours,
        y=flood,
        name="Projected Water Depth (m)",
        mode="lines+markers",
        line=dict(color="#7c3aed", width=3),
        marker=dict(size=6, color="#6d28d9"),
        yaxis="y2"
    ))

    fig.update_layout(
        title=f"<b>24-Hour Predictive Precipitation & Runoff Horizon: {zone_name}</b>",
        xaxis_title="Forecast Timeline (Hours)",
        yaxis=dict(title="Precipitation Intensity (mm/h)", side="left", rangemode="tozero"),
        yaxis2=dict(title="Projected Flood Depth (m)", side="right", overlaying="y", rangemode="tozero"),
        height=320,
        margin=dict(l=20, r=20, t=45, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template="plotly_dark",
        paper_bgcolor="#111827",
        plot_bgcolor="#0b0f19",
        font=dict(family="Plus Jakarta Sans, sans-serif", color="#f8fafc")
    )
    return fig


def plot_predictive_hourly_weather_aqi_chart(hourly: Dict[str, Any], zone_name: str = "") -> go.Figure:
    """
    Renders 24-hour predictive hourly Temperature (°C), Wind Gusts (km/h), and AQI curves.
    """
    hours = hourly.get("hours", [f"{i:02d}:00" for i in range(24)])
    temp = hourly.get("temperature_c", [28.0] * 24)
    wind = hourly.get("wind_gust_kmh", [20.0] * 24)
    aqi = hourly.get("aqi", [75] * 24)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=hours,
        y=temp,
        name="Temperature (°C)",
        mode="lines+markers",
        line=dict(color="#f97316", width=2.5),
        marker=dict(size=6, color="#ea580c"),
        yaxis="y1"
    ))

    fig.add_trace(go.Scatter(
        x=hours,
        y=wind,
        name="Peak Wind Gusts (km/h)",
        mode="lines",
        line=dict(color="#0284c7", width=2, dash="dash"),
        yaxis="y1"
    ))

    fig.add_trace(go.Scatter(
        x=hours,
        y=aqi,
        name="Air Quality Index (AQI)",
        mode="lines+markers",
        line=dict(color="#9333ea", width=2.5),
        marker=dict(size=5, color="#7e22ce"),
        yaxis="y2"
    ))

    fig.update_layout(
        title=f"<b>24-Hour Atmospheric Dynamics & Pollution Forecast: {zone_name}</b>",
        xaxis_title="Forecast Timeline (Hours)",
        yaxis=dict(title="Temperature (°C) / Wind (km/h)", side="left", rangemode="tozero"),
        yaxis2=dict(title="Air Quality Index (AQI)", side="right", overlaying="y", rangemode="tozero"),
        height=320,
        margin=dict(l=20, r=20, t=45, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template="plotly_dark",
        paper_bgcolor="#111827",
        plot_bgcolor="#0b0f19",
        font=dict(family="Plus Jakarta Sans, sans-serif", color="#f8fafc")
    )
    return fig

