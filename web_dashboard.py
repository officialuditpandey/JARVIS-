#!/usr/bin/env python3
"""
JARVIS Web Dashboard for Phone Access
Simple web interface for mobile control
"""

import os
import sys
from flask import Flask, render_template_string, request, jsonify
from datetime import datetime
import json

# Add JARVIS backend path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

app = Flask(__name__)

# HTML Template for Mobile Dashboard
DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>JARVIS Mobile Dashboard</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: #1a1a1a;
            color: #fff;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: #333;
            border-radius: 10px;
        }
        .command-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-bottom: 30px;
        }
        .btn {
            padding: 15px;
            border: none;
            border-radius: 8px;
            background: #0066cc;
            color: white;
            font-size: 14px;
            cursor: pointer;
            transition: background 0.3s;
        }
        .btn:hover {
            background: #0052a3;
        }
        .btn.danger {
            background: #cc0000;
        }
        .btn.danger:hover {
            background: #a30000;
        }
        .btn.success {
            background: #00cc00;
        }
        .btn.success:hover {
            background: #00a300;
        }
        .status {
            background: #333;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            min-height: 100px;
        }
        .response {
            background: #444;
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
            white-space: pre-wrap;
        }
        .custom-command {
            width: 100%;
            padding: 10px;
            margin: 10px 0;
            border: 1px solid #555;
            border-radius: 5px;
            background: #222;
            color: white;
        }
        .send-btn {
            width: 100%;
            padding: 12px;
            background: #00cc00;
            border: none;
            border-radius: 5px;
            color: white;
            cursor: pointer;
        }
        .loading {
            color: #ffcc00;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>JARVIS MOBILE DASHBOARD</h1>
            <p>Control JARVIS from your phone</p>
        </div>
        
        <div class="status" id="status">
            <strong>Status:</strong> Ready to connect to JARVIS...
        </div>
        
        <div class="command-grid">
            <button class="btn" onclick="sendCommand('system status')">System Status</button>
            <button class="btn" onclick="sendCommand('check storage')">Check Storage</button>
            <button class="btn" onclick="sendCommand('stop music')">Stop Music</button>
            <button class="btn" onclick="sendCommand('volume up')">Volume Up</button>
            <button class="btn" onclick="sendCommand('volume down')">Volume Down</button>
            <button class="btn" onclick="sendCommand('speedtest')">Speed Test</button>
            <button class="btn success" onclick="sendCommand('open notepad')">Open Notepad</button>
            <button class="btn danger" onclick="sendCommand('lock screen')">Lock Screen</button>
        </div>
        
        <div>
            <input type="text" id="customCommand" class="custom-command" 
                   placeholder="Type custom command...">
            <button class="send-btn" onclick="sendCustomCommand()">Send Command</button>
        </div>
        
        <div id="response" class="response" style="display: none;">
            <strong>JARVIS Response:</strong>
            <div id="responseText"></div>
        </div>
    </div>

    <script>
        function sendCommand(command) {
            updateStatus('Sending command: ' + command + '...', 'loading');
            
            fetch('/mobile-command', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    command: command
                })
            })
            .then(response => response.json())
            .then(data => {
                updateStatus('Command sent successfully', 'success');
                showResponse(data);
            })
            .catch(error => {
                updateStatus('Error: ' + error.message, 'error');
                showResponse({error: error.message});
            });
        }
        
        function sendCustomCommand() {
            const command = document.getElementById('customCommand').value;
            if (command.trim()) {
                sendCommand(command);
                document.getElementById('customCommand').value = '';
            }
        }
        
        function updateStatus(message, type) {
            const status = document.getElementById('status');
            status.innerHTML = '<strong>Status:</strong> ' + message;
            status.className = 'status ' + type;
        }
        
        function showResponse(data) {
            const response = document.getElementById('response');
            const responseText = document.getElementById('responseText');
            
            response.style.display = 'block';
            responseText.innerHTML = JSON.stringify(data, null, 2);
        }
        
        // Allow Enter key in custom command
        document.getElementById('customCommand').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendCustomCommand();
            }
        });
        
        // Auto-refresh status
        setInterval(() => {
            fetch('/mobile-status')
                .then(response => response.json())
                .then(data => {
                    updateStatus('Connected - Last: ' + data.last_command, 'success');
                })
                .catch(() => {
                    updateStatus('Connecting to JARVIS...', 'loading');
                });
        }, 5000);
    </script>
</body>
</html>
"""

# Global command history
command_history = []

@app.route('/')
def mobile_dashboard():
    """Mobile dashboard main page"""
    return DASHBOARD_HTML

@app.route('/mobile-command', methods=['POST'])
def mobile_command():
    """Handle mobile commands"""
    try:
        data = request.get_json()
        command = data.get('command', '')
        
        if not command:
            return jsonify({'error': 'No command provided'})
        
        # Execute command in JARVIS context
        result = execute_jarvis_command(command)
        
        # Add to history
        command_history.append({
            'command': command,
            'result': result,
            'timestamp': datetime.now().isoformat()
        })
        
        return jsonify({
            'success': True,
            'command': command,
            'result': result,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        })

@app.route('/mobile-status')
def mobile_status():
    """Get mobile status"""
    return jsonify({
        'status': 'connected',
        'last_command': command_history[-1]['command'] if command_history else 'none',
        'command_count': len(command_history),
        'timestamp': datetime.now().isoformat()
    })

def execute_jarvis_command(command):
    """Execute command in JARVIS context"""
    try:
        # Import JARVIS services if available
        if 'services' in globals():
            # System status command
            if 'system status' in command.lower() or 'check storage' in command.lower():
                if services.get('resource_monitor_simple'):
                    monitor = services['resource_monitor_simple']
                    status = monitor.get_system_status()
                    return {
                        'type': 'system_status',
                        'data': status,
                        'formatted': monitor.format_system_status_table(status)
                    }
            
            # Media commands
            elif 'stop music' in command.lower():
                if services.get('media_handler'):
                    result = services['media_handler'].stop_media()
                    return result
            
            # Volume commands
            elif 'volume up' in command.lower():
                if services.get('system_toggles'):
                    result = services['system_toggles'].increase_volume()
                    return result
            elif 'volume down' in command.lower():
                if services.get('system_toggles'):
                    result = services['system_toggles'].decrease_volume()
                    return result
            
            # Speedtest
            elif 'speedtest' in command.lower():
                if services.get('system_toggles'):
                    result = services['system_toggles'].run_speedtest()
                    return result
            
            # System commands
            elif 'open notepad' in command.lower():
                import subprocess
                if sys.platform == 'win32':
                    subprocess.Popen(['notepad.exe'])
                else:
                    subprocess.Popen(['gedit'])
                return {'success': True, 'message': 'Notepad opened'}
            
            elif 'lock screen' in command.lower():
                import subprocess
                if sys.platform == 'win32':
                    subprocess.Popen(['rundll32.exe', 'user32.dll,LockWorkStation'])
                else:
                    subprocess.Popen(['xdg-screensaver', 'lock'])
                return {'success': True, 'message': 'Screen locked'}
        
        # Fallback response
        return {
            'success': True,
            'message': f'Command received: {command}',
            'note': 'JARVIS processed your command'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def start_mobile_dashboard(port=8080):
    """Start the mobile dashboard"""
    try:
        print(f"Starting JARVIS Mobile Dashboard...")
        print(f"Access from your phone: http://your-pc-ip:{port}")
        print(f"Local access: http://localhost:{port}")
        app.run(host='0.0.0.0', port=port, debug=False)
    except Exception as e:
        print(f"Failed to start mobile dashboard: {e}")

if __name__ == '__main__':
    start_mobile_dashboard()
