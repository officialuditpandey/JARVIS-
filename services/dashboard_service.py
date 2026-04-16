"""
Dashboard Service for JARVIS - HTML Live Dashboard
Feature 13: Flask-based HTML Dashboard at localhost:5000
"""

import os
import json
import threading
import time
import logging
from datetime import datetime
from typing import Dict, Any, List
import sys

# Add JARVIS backend path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    import yaml
    with open('config/settings.yaml', 'r') as f:
        CONFIG = yaml.safe_load(f)
except:
    CONFIG = {
        'architect_pack': {
            'dashboard': {'enabled': True, 'host': 'localhost', 'port': 5000, 'refresh_rate': 30}
        }
    }

try:
    from flask import Flask, render_template_string, jsonify, Response
    FLASK_AVAILABLE = True
except ImportError:
    print("Flask not available - dashboard disabled")
    FLASK_AVAILABLE = False

class DashboardService:
    """Dashboard service for HTML live monitoring"""
    
    def __init__(self):
        self.app = None
        self.server_thread = None
        self.host = CONFIG['architect_pack']['dashboard'].get('host', '127.0.0.1')
        self.port = CONFIG['architect_pack']['dashboard'].get('port', 5000)
        self.refresh_rate = CONFIG['architect_pack']['dashboard'].get('refresh_rate', 30)
        self.is_running = False
        
        # Configure logging to reduce noise
        self._configure_logging()
    
    def _configure_logging(self):
        """Configure logging to show only errors"""
        try:
            # Set werkzeug logger to ERROR level only
            logging.getLogger('werkzeug').setLevel(logging.ERROR)
            
            # Set Flask logger to ERROR level only
            logging.getLogger('flask').setLevel(logging.ERROR)
            
            # Also quiet the access log
            logging.getLogger('werkzeug.access').setLevel(logging.ERROR)
            
            print("Dashboard logging: Quiet mode enabled (ERRORS only)")
        except Exception as e:
            print(f"Logging configuration failed: {e}")
        
        # Dashboard data
        self.system_status = {}
        self.vision_data = {}
        self.security_events = []
        self.study_stats = {}
        
        if FLASK_AVAILABLE and CONFIG['architect_pack']['dashboard']['enabled']:
            self._setup_flask_app()
    
    def _setup_flask_app(self):
        """Setup Flask application"""
        self.app = Flask(__name__)
        self.app.config['JSON_SORT_KEYS'] = False
        
        @self.app.route('/')
        def dashboard():
            """Main dashboard page"""
            return self._get_dashboard_html()
        
        @self.app.route('/api/status')
        def api_status():
            """API endpoint for system status"""
            return jsonify(self.get_system_status())
        
        @self.app.route('/api/vision')
        def api_vision():
            """API endpoint for vision data"""
            return jsonify(self.vision_data)
        
        @self.app.route('/api/security')
        def api_security():
            """API endpoint for security events"""
            return jsonify(self.security_events[-10:])  # Last 10 events
        
        @self.app.route('/api/study')
        def api_study():
            """API endpoint for study statistics"""
            return jsonify(self.study_stats)
        
        @self.app.route('/api/camera')
        def camera_feed():
            """Camera feed endpoint"""
            return self._get_camera_feed()
    
    def _get_dashboard_html(self) -> str:
        """Generate dashboard HTML"""
        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JARVIS Dashboard</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            min-height: 100vh;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            max-width: 1200px;
            margin: 0 auto;
        }
        .card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        .card h3 {
            margin-top: 0;
            color: #4fc3f7;
            border-bottom: 2px solid #4fc3f7;
            padding-bottom: 10px;
        }
        .status-item {
            display: flex;
            justify-content: space-between;
            margin: 10px 0;
            padding: 5px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        .status-value {
            font-weight: bold;
            color: #81c784;
        }
        .camera-container {
            position: relative;
            width: 100%;
            height: 200px;
            background: #000;
            border-radius: 10px;
            overflow: hidden;
        }
        .camera-feed {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        .refresh-info {
            text-align: center;
            margin-top: 20px;
            opacity: 0.7;
            font-size: 0.9em;
        }
        .alert {
            background: rgba(244, 67, 54, 0.2);
            border: 1px solid #f44336;
            border-radius: 5px;
            padding: 10px;
            margin: 10px 0;
        }
        .success {
            background: rgba(76, 175, 80, 0.2);
            border: 1px solid #4caf50;
            border-radius: 5px;
            padding: 10px;
            margin: 10px 0;
        }
        .brain-lights {
            display: flex;
            gap: 10px;
            margin-top: 5px;
        }
        .brain-light {
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.8em;
            font-weight: bold;
            text-align: center;
            min-width: 80px;
        }
        .brain-light.active {
            background: #4CAF50;
            color: white;
            box-shadow: 0 0 10px #4CAF50;
        }
        .brain-light.used {
            background: #FF9800;
            color: white;
        }
        .brain-light.inactive {
            background: #333;
            color: #666;
        }
        .privacy-shield {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-top: 5px;
        }
        .shield-icon {
            padding: 5px 10px;
            border-radius: 50%;
            font-size: 0.8em;
            font-weight: bold;
            text-align: center;
            min-width: 60px;
        }
        .shield-icon.active {
            background: #2196F3;
            color: white;
            box-shadow: 0 0 10px #2196F3;
        }
        .shield-icon.inactive {
            background: #333;
            color: #666;
        }
        .shield-status {
            font-size: 0.8em;
            font-weight: bold;
        }
        .shield-status.active {
            color: #2196F3;
        }
        .shield-status.inactive {
            color: #666;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1> JARVIS DASHBOARD </h1>
        <p>Real-time System Monitoring</p>
    </div>
    
    <div class="dashboard-grid">
        <!-- System Status Card -->
        <!-- Fast + Private Router Card -->
        <div class="card">
            <h3>Fast + Private Router</h3>
            <div id="router-status">
                <div class="status-item">
                    <span>Privacy Shield</span>
                    <div class="privacy-shield" id="privacy-shield">
                        <span class="shield-icon" id="shield-icon">SHIELD</span>
                        <span class="shield-status" id="shield-status">OFF</span>
                    </div>
                </div>
                <div class="status-item">
                    <span>Brain Status</span>
                    <div class="brain-lights">
                        <span class="brain-light" id="gemini-light">GEMINI</span>
                        <span class="brain-light" id="moondream-light">MOONDREAM</span>
                    </div>
                </div>
                <div class="status-item">
                    <span>Active Brain</span>
                    <span class="status-value" id="active-brain">Loading...</span>
                </div>
                <div class="status-item">
                    <span>Total Commands</span>
                    <span class="status-value" id="total-commands">Loading...</span>
                </div>
                <div class="status-item">
                    <span>Gemini Usage</span>
                    <span class="status-value" id="gemini-usage">Loading...</span>
                </div>
                <div class="status-item">
                    <span>Moondream Usage</span>
                    <span class="status-value" id="moondream-usage">Loading...</span>
                </div>
            </div>
        </div>
        
        <!-- Security Status Card -->
        <div class="card">
            <h3>Security Status</h3>
            <div id="security-status">
                <div class="status-item">
                    <span>Status</span>
                    <span class="status-value" id="sir-status">Loading...</span>
                </div>
                <div class="status-item">
                    <span>Last Face Seen</span>
                    <span class="status-value" id="last-face-seen">Loading...</span>
                </div>
                <div class="status-item">
                    <span>PC Lock</span>
                    <span class="status-value" id="pc-lock-status">Enabled</span>
                </div>
                <div class="status-item">
                    <span>Face Detection</span>
                    <span class="status-value" id="face-detection-status">Active</span>
                </div>
            </div>
        </div>
        
        <!-- System Status Card -->
        <div class="card">
            <h3>System Status</h3>
            <div id="system-status">
                <div class="status-item">
                    <span>JARVIS Status</span>
                    <span class="status-value" id="jarvis-status">Loading...</span>
                </div>
                <div class="status-item">
                    <span>CPU Usage</span>
                    <span class="status-value" id="cpu-usage">Loading...</span>
                </div>
                <div class="status-item">
                    <span>Memory Usage</span>
                    <span class="status-value" id="memory-usage">Loading...</span>
                </div>
                <div class="status-item">
                    <span>Active Services</span>
                    <span class="status-value" id="active-services">Loading...</span>
                </div>
            </div>
        </div>
        
        <!-- Vision Data Card -->
        <div class="card">
            <h3>Vision Analysis</h3>
            <div class="camera-container">
                <img id="camera-feed" class="camera-feed" src="/api/camera" alt="Camera Feed">
            </div>
            <div id="vision-data">
                <div class="status-item">
                    <span>Faces Detected</span>
                    <span class="status-value" id="faces-detected">0</span>
                </div>
                <div class="status-item">
                    <span>Objects Counted</span>
                    <span class="status-value" id="objects-counted">0</span>
                </div>
                <div class="status-item">
                    <span>Motion Detected</span>
                    <span class="status-value" id="motion-detected">No</span>
                </div>
            </div>
        </div>
        
        <!-- Security Events Card -->
        <div class="card">
            <h3>Security Events</h3>
            <div id="security-events">
                <p>Loading security events...</p>
            </div>
        </div>
        
        <!-- Study Statistics Card -->
        <div class="card">
            <h3>Study Statistics</h3>
            <div id="study-stats">
                <div class="status-item">
                    <span>Study Mode</span>
                    <span class="status-value" id="study-mode">Inactive</span>
                </div>
                <div class="status-item">
                    <span>Focus Duration</span>
                    <span class="status-value" id="focus-duration">0m</span>
                </div>
                <div class="status-item">
                    <span>Flashcards</span>
                    <span class="status-value" id="flashcard-count">0</span>
                </div>
                <div class="status-item">
                    <span>Notes Taken</span>
                    <span class="status-value" id="note-count">0</span>
                </div>
            </div>
        </div>
    </div>
    
    <div class="refresh-info">
        <p>Auto-refresh every {{ refresh_rate }} seconds | Last updated: <span id="last-update">Never</span></p>
    </div>
    
    <script>
        // Update dashboard data
        async function updateDashboard() {
            try {
                // Update system status
                const statusResponse = await fetch('/api/status');
                const statusData = await statusResponse.json();
                updateSystemStatus(statusData);
                
                // Update vision data
                const visionResponse = await fetch('/api/vision');
                const visionData = await visionResponse.json();
                updateVisionData(visionData);
                
                // Update security events
                const securityResponse = await fetch('/api/security');
                const securityData = await securityResponse.json();
                updateSecurityEvents(securityData);
                
                // Update study stats
                const studyResponse = await fetch('/api/study');
                const studyData = await studyResponse.json();
                updateStudyStats(studyData);
                
                // Update last refresh time
                document.getElementById('last-update').textContent = new Date().toLocaleTimeString();
                
            } catch (error) {
                console.error('Dashboard update error:', error);
            }
        }
        
        function updateSystemStatus(data) {
            // Update system status
            document.getElementById('jarvis-status').textContent = data.services?.vision || 'Unknown';
            document.getElementById('cpu-usage').textContent = data.system?.cpu || 'N/A';
            document.getElementById('memory-usage').textContent = data.system?.memory || 'N/A';
            
            // Count active services
            const activeServices = Object.values(data.services || {}).filter(s => s === 'active').length;
            document.getElementById('active-services').textContent = activeServices.toString();
            
            // Update Fast + Private router status
            if (data.fast_private_router) {
                // Update privacy shield
                const privacyMode = data.fast_private_router.privacy_mode || false;
                updatePrivacyShield(privacyMode);
                
                // Update brain status lights
                const brainStatus = data.fast_private_router.brain_status || {};
                updateBrainLight('gemini-light', brainStatus.gemini || 'inactive');
                updateBrainLight('moondream-light', brainStatus.moondream || 'inactive');
                
                // Update text displays
                document.getElementById('active-brain').textContent = data.fast_private_router.active_brain || 'GEMINI';
                document.getElementById('total-commands').textContent = data.fast_private_router.routing_stats?.total_commands || '0';
                document.getElementById('gemini-usage').textContent = data.fast_private_router.routing_stats?.gemini_percentage || '0%';
                document.getElementById('moondream-usage').textContent = data.fast_private_router.routing_stats?.moondream_percentage || '0%';
            }
            
            function updateBrainLight(elementId, status) {
                const element = document.getElementById(elementId);
                if (element) {
                    element.className = 'brain-light ' + status;
                }
            }
            
            function updatePrivacyShield(isActive) {
                const shieldIcon = document.getElementById('shield-icon');
                const shieldStatus = document.getElementById('shield-status');
                
                if (shieldIcon && shieldStatus) {
                    if (isActive) {
                        shieldIcon.className = 'shield-icon active';
                        shieldStatus.className = 'shield-status active';
                        shieldStatus.textContent = 'ACTIVE';
                    } else {
                        shieldIcon.className = 'shield-icon inactive';
                        shieldStatus.className = 'shield-status inactive';
                        shieldStatus.textContent = 'OFF';
                    }
                }
            }
            
            // Update security status
            if (data.security_status) {
                document.getElementById('sir-status').textContent = data.security_status.status || 'Sir Away';
                document.getElementById('last-face-seen').textContent = data.security_status.last_face_seen || 'N/A';
            }
        }
        
        function updateVisionData(data) {
            document.getElementById('faces-detected').textContent = data.faces_detected || '0';
            document.getElementById('objects-counted').textContent = data.object_counted || '0';
            document.getElementById('motion-detected').textContent = data.motion_detected ? 'Yes' : 'No';
        }
        
        function updateSecurityEvents(events) {
            const container = document.getElementById('security-events');
            if (events.length === 0) {
                container.innerHTML = '<p>No recent security events</p>';
                return;
            }
            
            container.innerHTML = events.map(event => 
                `<div class="alert">
                    <strong>${event.timestamp}</strong><br>
                    ${event.type}: ${event.message}
                </div>`
            ).join('');
        }
        
        function updateStudyStats(data) {
            document.getElementById('study-mode').textContent = data.study_mode_active ? 'Active' : 'Inactive';
            document.getElementById('focus-duration').textContent = data.focus_duration ? `${Math.floor(data.focus_duration / 60)}m` : '0m';
            document.getElementById('flashcard-count').textContent = data.total_flashcards || '0';
            document.getElementById('note-count').textContent = data.total_notes || '0';
        }
        
        // Initial update and set interval
        updateDashboard();
        setInterval(updateDashboard, {{ refresh_rate }} * 1000);
        
        // Refresh camera feed
        setInterval(() => {
            const camera = document.getElementById('camera-feed');
            if (camera) {
                camera.src = '/api/camera?' + new Date().getTime();
            }
        }, 5000);
    </script>
</body>
</html>
        """
        return html_template.replace('{{ refresh_rate }}', str(self.refresh_rate))
    
    def _get_camera_feed(self) -> Response:
        """Get camera feed image"""
        try:
            # Check if temp_eye.jpg exists
            if os.path.exists('temp_eye.jpg'):
                return Response(open('temp_eye.jpg', 'rb').read(), mimetype='image/jpeg')
            else:
                # Return a placeholder image or 404
                return Response('Camera feed not available', status=404)
        except Exception as e:
            return Response(f'Camera feed error: {e}', status=500)
    
    def start_dashboard(self) -> bool:
        """Start dashboard server"""
        if not FLASK_AVAILABLE or not CONFIG['architect_pack']['dashboard']['enabled']:
            return False
        
        try:
            if self.is_running:
                return True
            
            # Start Flask app in separate thread
            self.server_thread = threading.Thread(
                target=self._run_server,
                daemon=True
            )
            self.server_thread.start()
            
            # Wait a moment for server to start
            time.sleep(2)
            self.is_running = True
            
            print(f"Dashboard started at http://{self.host}:{self.port}")
            return True
            
        except Exception as e:
            print(f"Failed to start dashboard: {e}")
            return False
    
    def _run_server(self):
        """Run Flask server with enhanced stability"""
        try:
            # Use socketserver for better stability
            from werkzeug.serving import make_server
            
            # Create server with better configuration
            server = make_server(
                self.host, 
                self.port, 
                self.app, 
                threaded=True,
                processes=1
            )
            print(f"Dashboard server listening on {self.host}:{self.port}")
            
            # Run server with proper shutdown handling
            server.serve_forever()
            
        except Exception as e:
            print(f"Dashboard server error: {e}")
            # Retry once if server fails
            try:
                print("Retrying dashboard startup...")
                self.app.run(
                    host=self.host,
                    port=self.port,
                    debug=False,
                    use_reloader=False,
                    threaded=True
                )
            except Exception as retry_error:
                print(f"Dashboard retry failed: {retry_error}")
    
    def stop_dashboard(self) -> bool:
        """Stop dashboard server"""
        try:
            self.is_running = False
            # Flask doesn't have a clean shutdown method in development mode
            # The thread will stop when the main process exits
            print("Dashboard stopped")
            return True
            
        except Exception as e:
            print(f"Failed to stop dashboard: {e}")
            return False
    
    def update_system_status(self, status: Dict[str, Any]):
        """Update system status data"""
        self.system_status = status
    
    def update_vision_data(self, vision_data: Dict[str, Any]):
        """Update vision analysis data"""
        self.vision_data = vision_data
    
    def add_security_event(self, event_type: str, message: str):
        """Add security event"""
        event = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'type': event_type,
            'message': message
        }
        self.security_events.append(event)
        
        # Keep only last 50 events
        if len(self.security_events) > 50:
            self.security_events = self.security_events[-50:]
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status for dashboard"""
        # Get router status if available
        active_brain = "gemini"  # default
        routing_stats = {}
        privacy_mode = False
        brain_status = {
            'gemini': 'active',  # Default brain
            'moondream': 'inactive'
        }
        
        if 'services' in globals() and services.get('router'):
            router_stats = services['router'].get_routing_stats()
            active_brain = router_stats.get('active_brain', 'gemini')
            privacy_mode = router_stats.get('privacy_mode', False)
            routing_stats = router_stats
            
            # Set brain status lights
            if active_brain == "gemini":
                brain_status['gemini'] = 'active'
                brain_status['moondream'] = 'inactive'
            else:  # moondream
                brain_status['gemini'] = 'inactive'
                brain_status['moondream'] = 'active'
            
            # Show usage to determine secondary activity
            if router_stats.get('moondream_percentage', 0) > 20:
                brain_status['moondream'] = 'used'
        
        # Get security status if available
        security_status = "Away"  # default
        last_face_seen = "N/A"
        
        if 'services' in globals() and services.get('security'):
            sec_status = services['security'].get_security_status()
            security_status = sec_status.get('status', 'Away')
            last_face_seen = sec_status.get('last_face_seen', 'N/A')
        
        return {
            'timestamp': datetime.now().isoformat(),
            'services': {
                'vision': 'active' if self.vision_data else 'idle',
                'security': 'monitoring' if len(self.security_events) > 0 else 'idle',
                'study': 'active' if self.study_stats.get('study_mode_active') else 'idle',
                'companion': 'active' if self.study_stats else 'idle'
            },
            'system': {
                'cpu': '45%',
                'memory': '67%',
                'disk': '82%'
            },
            'fast_private_router': {
                'active_brain': active_brain.upper(),
                'privacy_mode': privacy_mode,
                'routing_stats': routing_stats,
                'brain_status': brain_status
            },
            'security_status': {
                'status': f"Sir {security_status}",
                'last_face_seen': last_face_seen
            },
            'last_updated': datetime.now().isoformat()
        }
