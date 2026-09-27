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
    <title>DisasterLens | National Disaster Portal</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: #f8fafc;
            color: #0f172a;
            margin: 0;
            padding: 40px 20px;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 80vh;
        }
        .card {
            background: white;
            border: 1px solid #cbd5e1;
            border-radius: 12px;
            padding: 32px;
            max-width: 650px;
            box-shadow: 0 4px 16px rgba(15, 23, 42, 0.08);
            text-align: center;
        }
        .tricolor {
            height: 6px;
            background: linear-gradient(90deg, #FF9933 33.3%, #ffffff 33.3%, #ffffff 66.6%, #138808 66.6%);
            border-radius: 4px;
            margin-bottom: 20px;
        }
        h1 { font-size: 24px; color: #1e40af; margin-bottom: 8px; }
        p { font-size: 15px; color: #475569; line-height: 1.6; }
        .btn {
            display: inline-block;
            background-color: #1e40af;
            color: white !important;
            padding: 12px 24px;
            border-radius: 8px;
            font-weight: 700;
            text-decoration: none;
            margin-top: 16px;
            transition: background 0.2s;
        }
        .btn:hover { background-color: #1d4ed8; }
        .note {
            background-color: #eff6ff;
            border: 1px solid #bfdbfe;
            border-radius: 8px;
            padding: 12px;
            font-size: 13px;
            color: #1e40af;
            margin-top: 20px;
            text-align: left;
        }
    </style>
</head>
<body>
    <div class="card">
        <div class="tricolor"></div>
        <div style="font-size: 40px;">🏛️</div>
        <h1>DisasterLens: National Decision Support Portal</h1>
        <p><strong>Government of India / NDMA Decision-Support Engine</strong></p>
        <p>105 Real Disaster Locations in India &bull; Live Telemetry &bull; Predictive ML Severity &bull; Constrained Resource Optimization &bull; AI Disaster Sahayak Chatbot</p>
        
        <div class="note">
            <strong>🚀 Live Deployment Notice:</strong><br>
            Streamlit requires active WebSocket streaming for live interactive maps and AI chats. For optimal performance with 0 timeouts, DisasterLens is deployed on <strong>Streamlit Community Cloud</strong> or containerized via <strong>Docker / Cloud Run</strong>.
        </div>
        
        <a href="https://share.streamlit.io" target="_blank" class="btn">Open DisasterLens on Streamlit Cloud &rarr;</a>
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
