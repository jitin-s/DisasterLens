"""
Vercel Serverless Entry Point for DisasterLens.
Handles incoming HTTP requests in Vercel's serverless environment.
"""

from http.server import BaseHTTPRequestHandler
import json
import os
import sys

# Ensure root directory is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DisasterLens | National AI Predictive Portal</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: #0b0f19;
            color: #f8fafc;
            margin: 0;
            padding: 40px 20px;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 80vh;
        }
        .card {
            background: #111827;
            border: 1px solid rgba(56, 189, 248, 0.25);
            border-radius: 14px;
            padding: 36px;
            max-width: 650px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
            text-align: center;
        }
        .tricolor {
            height: 4px;
            background: linear-gradient(90deg, #FF9933 33.3%, #ffffff 33.3%, #ffffff 66.6%, #138808 66.6%);
            border-radius: 4px;
            margin-bottom: 24px;
        }
        h1 { font-size: 26px; color: #ffffff; margin-bottom: 6px; font-weight: 800; }
        .subtitle { font-size: 13px; color: #38bdf8; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 14px; }
        p { font-size: 14px; color: #94a3b8; line-height: 1.6; }
        .stats-grid {
            display: flex;
            gap: 10px;
            justify-content: center;
            flex-wrap: wrap;
            margin: 20px 0;
        }
        .stat-pill {
            background: #1e293b;
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 20px;
            padding: 6px 14px;
            font-size: 12px;
            font-weight: 600;
            color: #cbd5e1;
        }
        .btn {
            display: inline-block;
            background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
            color: #ffffff !important;
            padding: 12px 26px;
            border-radius: 8px;
            font-weight: 700;
            text-decoration: none;
            margin-top: 18px;
            border: 1px solid rgba(56, 189, 248, 0.4);
            box-shadow: 0 4px 14px rgba(2, 132, 199, 0.3);
            transition: all 0.2s ease;
        }
        .btn:hover { background: #0284c7; transform: translateY(-1px); }
        .note {
            background: rgba(30, 41, 59, 0.6);
            border: 1px solid rgba(56, 189, 248, 0.2);
            border-radius: 8px;
            padding: 14px;
            font-size: 12.5px;
            color: #cbd5e1;
            margin-top: 20px;
            text-align: left;
            line-height: 1.5;
        }
    </style>
</head>
<body>
    <div class="card">
        <div class="tricolor"></div>
        <div style="font-size: 42px; margin-bottom: 10px;">🛡️</div>
        <h1>DisasterLens</h1>
        <div class="subtitle">National AI Multi-Hazard Predictive Intelligence</div>
        <p>Pan-India Real-Time Atmospheric Radar & Telemetry &bull; Predictive ML Severity &bull; Constrained Golden-Hour Evacuation &bull; Bilingual AI Disaster Sahayak</p>
        
        <div class="stats-grid">
            <div class="stat-pill">🛰️ 632 Districts Ingested</div>
            <div class="stat-pill">📡 SACHET CAP v1.2 Live</div>
            <div class="stat-pill">⚡ 10-Min Live Radar Sync</div>
        </div>

        <div class="note">
            <strong style="color: #38bdf8;">🚀 Cloud Deployment Architecture:</strong><br>
            DisasterLens leverages interactive WebSocket streaming for real-time Folium radar maps and predictive AI inferences. For 100% interactive live streaming with zero timeouts, launch directly on <strong>Streamlit Community Cloud</strong> (free) or connect via <strong>Vercel / Docker</strong>.
        </div>
        
        <a href="https://share.streamlit.io" target="_blank" class="btn">Launch DisasterLens Command Center &rarr;</a>
    </div>
</body>
</html>
"""


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(HTML_CONTENT.encode("utf-8"))
