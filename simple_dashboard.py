#!/usr/bin/env python3
"""
Simple Robust Dashboard
Fixed connection issues with basic Flask server
"""

import sys
import os
import logging
from flask import Flask, jsonify, Response
import threading
import time

# Add JARVIS backend path
sys.path.append(os.path.dirname(__file__))

app = Flask(__name__)

# Configure logging to reduce noise
logging.getLogger('werkzeug').setLevel(logging.ERROR)
logging.getLogger('flask').setLevel(logging.ERROR)
logging.getLogger('werkzeug.access').setLevel(logging.ERROR)

@app.route('/')
def dashboard():
    """Simple dashboard page"""
    return """
<!DOCTYPE html>
<html>
<head>
    <title>JARVIS Dashboard</title>
    <style>
        body { font-family: Arial; margin: 40px; background: #1a1a1a; color: white; }
        .status { background: #333; padding: 20px; border-radius: 10px; }
        .online { color: #4CAF50; }
        .offline { color: #f44336; }
    </style>
</head>
<body>
    <h1>JARVIS Dashboard</h1>
    <div class="status">
        <h2>System Status</h2>
        <p class="online">Dashboard: ONLINE</p>
        <p class="online">Vision: ACTIVE</p>
        <p class="online">Security: MONITORING</p>
        <p class="online">Study Mode: READY</p>
    </div>
    <p>Auto-refresh in 30 seconds...</p>
    <script>
        setTimeout(() => location.reload(), 30000);
    </script>
</body>
</html>
"""

@app.route('/api/status')
def api_status():
    """System status API"""
    return jsonify({
        'status': 'online',
        'timestamp': time.time(),
        'services': {
            'vision': 'active',
            'security': 'monitoring',
            'study': 'ready',
            'companion': 'active'
        }
    })

@app.route('/api/camera')
def api_camera():
    """Camera feed endpoint"""
    try:
        if os.path.exists('temp_eye.jpg'):
            with open('temp_eye.jpg', 'rb') as f:
                return Response(f.read(), mimetype='image/jpeg')
        else:
            return Response('Camera feed not available', status=404)
    except Exception as e:
        return Response(f'Camera error: {e}', status=500)

def run_dashboard():
    """Run dashboard on 127.0.0.1:5000"""
    try:
        print("Starting simple dashboard...")
        app.run(host='127.0.0.1', port=5000, debug=False, threaded=True)
    except Exception as e:
        print(f"Dashboard error: {e}")

if __name__ == "__main__":
    print("JARVIS Simple Dashboard")
    print("Access: http://127.0.0.1:5000")
    print("Press Ctrl+C to stop")
    run_dashboard()
