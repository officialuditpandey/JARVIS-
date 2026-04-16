#!/usr/bin/env python3
"""
Cloud Cowork HUD Server
Modern JARVIS interface with floating HUD design
"""

import os
import sys
import json
import asyncio
import threading
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.serving import make_server

# Add JARVIS backend path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from core.ai_engine import get_hybrid_response
    AI_AVAILABLE = True
except ImportError as e:
    print(f"Legacy AI backend not available: {e}")
    AI_AVAILABLE = False

try:
    from services.brain import HybridRouter
    from services.ai_service import AIService
    HYBRID_ROUTER_AVAILABLE = True
    print("Hybrid Router available")
except ImportError as e:
    print(f"Hybrid Router not available: {e}")
    HYBRID_ROUTER_AVAILABLE = False

try:
    import cv2
    import numpy as np
    from PIL import Image
    import base64
    import io
    VISION_AVAILABLE = True
except ImportError as e:
    print(f"Vision components not available: {e}")
    VISION_AVAILABLE = False

try:
    import screen_brightness_control as sbc
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    from comtypes import CLSCTX_ALL, CoInitialize, CoUninitialize
    AUTOMATION_AVAILABLE = True
except ImportError as e:
    print(f"Automation components not available: {e}")
    AUTOMATION_AVAILABLE = False

app = Flask(__name__)

# Global state
notifications = []
system_status = {
    "volume": None,
    "brightness": None,
    "camera": False,
    "ai_engine": AI_AVAILABLE,
    "vision": VISION_AVAILABLE,
    "automation": AUTOMATION_AVAILABLE,
    "hybrid_router": HYBRID_ROUTER_AVAILABLE
}

# Initialize HybridRouter and AI service
if HYBRID_ROUTER_AVAILABLE:
    try:
        ai_service = AIService()
        hybrid_router = ai_service.hybrid_router
        print("Hybrid Router initialized successfully")
    except Exception as e:
        print(f"Hybrid Router initialization failed: {e}")
        ai_service = None
        hybrid_router = None
else:
    ai_service = None
    hybrid_router = None

def add_notification(title, message, notification_type="info"):
    """Add a new notification"""
    notification = {
        "title": title,
        "message": message,
        "type": notification_type,
        "timestamp": datetime.now().isoformat()
    }
    notifications.insert(0, notification)
    if len(notifications) > 50:
        notifications.pop()

def execute_automation_action(action, params=None):
    """Execute automation actions"""
    try:
        if action == "system_scan":
            return perform_system_scan()
        elif action == "volume_up":
            return adjust_volume("increase")
        elif action == "volume_down":
            return adjust_volume("decrease")
        elif action == "brightness_up":
            return adjust_brightness("increase")
        elif action == "brightness_down":
            return adjust_brightness("decrease")
        elif action == "whatsapp":
            return "WhatsApp integration ready"
        elif action == "vision_toggle":
            return "Vision feed toggled"
        elif action == "settings":
            return "Settings panel opened"
        else:
            return f"Unknown action: {action}"
    except Exception as e:
        return f"Error executing {action}: {e}"

def perform_system_scan():
    """Perform system scan"""
    try:
        scan_results = []
        
        # Check AI
        if AI_AVAILABLE:
            scan_results.append("AI Engine: Online")
        else:
            scan_results.append("AI Engine: Offline")
        
        # Check Vision
        if VISION_AVAILABLE:
            scan_results.append("Vision System: Available")
        else:
            scan_results.append("Vision System: Unavailable")
        
        # Check Automation
        if AUTOMATION_AVAILABLE:
            scan_results.append("Automation: Ready")
        else:
            scan_results.append("Automation: Limited")
        
        # Check system status
        volume = get_volume_level()
        if volume is not None:
            scan_results.append(f"Volume: {volume}%")
        
        brightness = get_brightness_level()
        if brightness is not None:
            scan_results.append(f"Brightness: {brightness}%")
        
        return "System scan completed: " + "; ".join(scan_results)
    except Exception as e:
        return f"System scan failed: {e}"

def adjust_volume(direction):
    """Adjust system volume"""
    try:
        if not AUTOMATION_AVAILABLE:
            return "Volume control not available"
        
        current = get_volume_level()
        if current is None:
            return "Could not get current volume level"
        
        if direction == "increase":
            new_level = min(100, current + 10)
        else:
            new_level = max(0, current - 10)
        
        set_volume(new_level)
        return f"Volume adjusted to {new_level}%"
    except Exception as e:
        return f"Volume control error: {e}"

def adjust_brightness(direction):
    """Adjust system brightness"""
    try:
        if not AUTOMATION_AVAILABLE:
            return "Brightness control not available"
        
        current = get_brightness_level()
        if current is None:
            return "Could not get current brightness level"
        
        if direction == "increase":
            new_level = min(100, current + 10)
        else:
            new_level = max(0, current - 10)
        
        sbc.set_brightness(new_level, display=0)
        return f"Brightness adjusted to {new_level}%"
    except Exception as e:
        return f"Brightness control error: {e}"

def get_volume_level():
    """Get current volume level"""
    try:
        CoInitialize()
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = interface.QueryInterface(IAudioEndpointVolume)
        level = int(volume.GetMasterVolumeLevelScalar() * 100)
        CoUninitialize()
        return level
    except Exception:
        return None

def get_brightness_level():
    """Get current brightness level"""
    try:
        brightness = sbc.get_brightness()
        return brightness[0] if brightness else None
    except Exception:
        return None

def set_volume(level):
    """Set volume level"""
    try:
        CoInitialize()
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = interface.QueryInterface(IAudioEndpointVolume)
        volume.SetMasterVolumeLevelScalar(level / 100, None)
        CoUninitialize()
    except Exception as e:
        print(f"Error setting volume: {e}")

# API Routes
@app.route('/')
def index():
    """Serve the refined HUD interface"""
    return send_from_directory('.', 'hud_refined.html')

@app.route('/api/execute_action', methods=['POST'])
def execute_action():
    """Execute automation action"""
    try:
        data = request.json
        action = data.get('action', '')
        
        if not action:
            return jsonify({'success': False, 'error': 'No action specified'})
        
        result = execute_automation_action(action)
        add_notification('Action Complete', f'{action}: {result}', 'success')
        
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        add_notification('Action Error', str(e), 'error')
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/chat_command', methods=['POST'])
def chat_command():
    """Process AI chat command with HybridRouter"""
    try:
        data = request.json
        message = data.get('message', '')
        
        if not message:
            return jsonify({'success': False, 'error': 'No message specified'})
        
        # Use HybridRouter if available
        if ai_service and ai_service.use_hybrid:
            # Process with HybridRouter
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                response, source = loop.run_until_complete(ai_service.process_command(message))
                routing_stats = ai_service.get_routing_stats()
            finally:
                loop.close()
        elif AI_AVAILABLE:
            # Fallback to legacy system
            response, source = get_hybrid_response(message, [])
            result = f"[{source.upper()}] {response}"
            routing_stats = {"total": 0, "personal": 0, "general": 0}
        else:
            response = "AI service is currently unavailable"
            source = "None"
            routing_stats = {"total": 0, "personal": 0, "general": 0}
        
        add_notification('AI Response', f'Processed: {message[:30]}...', 'ai')
        
        return jsonify({
            'success': True, 
            'response': response,
            'routing': source,
            'stats': routing_stats
        })
    except Exception as e:
        add_notification('AI Error', str(e), 'error')
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/analyze_vision', methods=['POST'])
def analyze_vision():
    """Analyze vision frame using Moondream"""
    try:
        if not VISION_AVAILABLE:
            return jsonify({'success': False, 'error': 'Vision system not available'})
        
        if 'frame' not in request.files:
            return jsonify({'success': False, 'error': 'No frame provided'})
        
        frame = request.files['frame']
        
        # Convert frame to image
        img = Image.open(frame)
        
        # Try to use Moondream for analysis
        try:
            import ollama
            import base64
            import io
            
            # Convert image to base64
            buffered = io.BytesIO()
            img.save(buffered, format="JPEG")
            b64_image = base64.b64encode(buffered.getvalue()).decode()
            
            # Send to Moondream
            response = ollama.chat(
                model="moondream",
                messages=[{
                    'role': 'user',
                    'content': 'Analyze this camera frame. Describe what you see in detail, including objects, people, and environment.',
                    'images': [b64_image]
                }]
            )
            
            analysis = response['message']['content']
            
        except Exception as vision_error:
            # Fallback to mock analysis if Moondream fails
            analysis = f"Vision analysis: Object detection and scene analysis (Moondream unavailable: {vision_error})"
        
        add_notification('Vision Analysis', analysis[:100] + '...', 'ai')
        
        return jsonify({'success': True, 'result': analysis})
    except Exception as e:
        add_notification('Vision Error', str(e), 'error')
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/get_stats')
def get_stats():
    """Get routing statistics"""
    try:
        if ai_service and ai_service.use_hybrid:
            stats = ai_service.get_routing_stats()
            return jsonify({'success': True, 'stats': stats})
        else:
            return jsonify({'success': True, 'stats': {"total": 0, "personal": 0, "general": 0}})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/get_notifications')
def get_notifications():
    """Get recent notifications"""
    return jsonify({'notifications': notifications[-20:]})

@app.route('/api/status')
def get_status():
    """Get system status"""
    return jsonify({'status': system_status})

def run_server():
    """Run the HUD server"""
    print("=== Cloud Cowork HUD Server ===")
    print("Starting modern JARVIS interface with Hybrid Router...")
    print(f"AI Engine: {'Available' if AI_AVAILABLE else 'Unavailable'}")
    print(f"Hybrid Router: {'Available' if HYBRID_ROUTER_AVAILABLE else 'Unavailable'}")
    print(f"Vision System: {'Available' if VISION_AVAILABLE else 'Unavailable'}")
    print(f"Automation: {'Available' if AUTOMATION_AVAILABLE else 'Unavailable'}")
    
    if HYBRID_ROUTER_AVAILABLE and ai_service:
        status = ai_service.get_ai_status()
        print(f"Gemini Available: {status.get('gemini_available', False)}")
        print(f"Ollama Available: {status.get('ollama_available', False)}")
        print(f"Local Model: {status.get('local_model', 'N/A')}")
    
    print("================================")
    print("HUD available at: http://localhost:3000")
    print("Press Ctrl+C to stop the server")
    
    # Add initial notification
    add_notification('System', 'Cloud Cowork HUD initialized with Hybrid Router', 'success')
    
    # Run the server
    app.run(host='0.0.0.0', port=3000, debug=False)

if __name__ == '__main__':
    run_server()
