#!/usr/bin/env python3
"""
Cloud Cowork HUD Server - Local Only
Modern JARVIS interface using only local Ollama models
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

# Import local services only
try:
    from services.ai_service_local import LocalAIService
    LOCAL_AI_AVAILABLE = True
    print("Local AI service available")
except ImportError as e:
    print(f"Local AI service not available: {e}")
    LOCAL_AI_AVAILABLE = False

try:
    import screen_brightness_control as sbc
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    from comtypes import CLSCTX_ALL, CoInitialize, CoUninitialize
    AUTOMATION_AVAILABLE = True
except ImportError as e:
    print(f"Automation components not available: {e}")
    AUTOMATION_AVAILABLE = False

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

app = Flask(__name__)

# Global state
notifications = []
system_status = {
    "volume": None,
    "brightness": None,
    "camera": False,
    "local_ai": LOCAL_AI_AVAILABLE,
    "vision": VISION_AVAILABLE,
    "automation": AUTOMATION_AVAILABLE,
    "voice": False
}

# Initialize local AI service
if LOCAL_AI_AVAILABLE:
    try:
        ai_service = LocalAIService()
        print("Local AI service initialized successfully")
    except Exception as e:
        print(f"Local AI service initialization failed: {e}")
        ai_service = None
else:
    ai_service = None

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
        elif action == "voice_toggle":
            return toggle_voice_listening()
        elif action == "speak_test":
            return test_voice_output()
        else:
            return f"Unknown action: {action}"
    except Exception as e:
        return f"Error executing {action}: {e}"

def perform_system_scan():
    """Perform system scan"""
    try:
        scan_results = []
        
        # Check Local AI
        if ai_service and ai_service.is_available():
            scan_results.append("Local AI: Online")
        else:
            scan_results.append("Local AI: Offline")
        
        # Check Vision
        if VISION_AVAILABLE and ai_service and ai_service.vision:
            scan_results.append("Vision System: Available")
        else:
            scan_results.append("Vision System: Unavailable")
        
        # Check Voice
        if ai_service and ai_service.voice and ai_service.voice.is_available():
            scan_results.append("Voice System: Available")
        else:
            scan_results.append("Voice System: Unavailable")
        
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

def toggle_voice_listening():
    """Toggle voice listening"""
    try:
        if not ai_service or not ai_service.voice:
            return "Voice service not available"
        
        if ai_service.voice.is_listening:
            return "Voice listening already active"
        
        # Start listening in background
        def listen_background():
            result = ai_service.start_listening(timeout=5)
            if result:
                add_notification('Voice Command', f'Heard: {result}', 'info')
                # Process the voice command
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                try:
                    response, source = loop.run_until_complete(ai_service.process_command(result))
                    add_notification('AI Response', f'{source}: {response[:50]}...', 'ai')
                finally:
                    loop.close()
            else:
                add_notification('Voice', 'No speech detected', 'warning')
        
        threading.Thread(target=listen_background, daemon=True).start()
        return "Voice listening started"
        
    except Exception as e:
        return f"Voice toggle error: {e}"

def test_voice_output():
    """Test voice output"""
    try:
        if not ai_service or not ai_service.voice:
            return "Voice service not available"
        
        ai_service.speak("Voice system test complete")
        return "Voice test completed"
    except Exception as e:
        return f"Voice test error: {e}"

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
    """Process AI chat command with local Ollama"""
    try:
        data = request.json
        message = data.get('message', '')
        
        if not message:
            return jsonify({'success': False, 'error': 'No message specified'})
        
        # Use local AI service
        if ai_service and ai_service.is_available():
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                response, source = loop.run_until_complete(ai_service.process_command(message))
                stats = ai_service.get_statistics()
            finally:
                loop.close()
        else:
            response = "Local AI service is currently unavailable"
            source = "None"
            stats = {"total": 0, "local_commands": 0, "vision_commands": 0}
        
        add_notification('AI Response', f'Processed: {message[:30]}...', 'ai')
        
        return jsonify({
            'success': True, 
            'response': response,
            'routing': source,
            'stats': stats
        })
    except Exception as e:
        add_notification('AI Error', str(e), 'error')
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/analyze_vision', methods=['POST'])
def analyze_vision():
    """Analyze vision frame using local Moondream"""
    try:
        if not VISION_AVAILABLE:
            return jsonify({'success': False, 'error': 'Vision system not available'})
        
        if 'frame' not in request.files:
            return jsonify({'success': False, 'error': 'No frame provided'})
        
        frame = request.files['frame']
        
        # Convert frame to image
        img = Image.open(frame)
        
        # Use local vision service
        if ai_service and ai_service.vision:
            try:
                import base64
                import io
                
                # Convert image to base64
                buffered = io.BytesIO()
                img.save(buffered, format="JPEG")
                b64_image = base64.b64encode(buffered.getvalue()).decode()
                
                analysis = ai_service.vision.analyze_image(img, "Analyze this camera frame in detail.")
                
                add_notification('Vision Analysis', analysis[:100] + '...', 'ai')
                
                return jsonify({'success': True, 'result': analysis})
            except Exception as vision_error:
                analysis = f"Vision analysis: Local Moondream processing failed: {vision_error}"
                add_notification('Vision Error', analysis, 'error')
                return jsonify({'success': True, 'result': analysis})
        else:
            analysis = "Vision service not available"
            return jsonify({'success': False, 'error': analysis})
            
    except Exception as e:
        add_notification('Vision Error', str(e), 'error')
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/analyze_screen', methods=['POST'])
def analyze_screen():
    """Analyze screen screenshot"""
    try:
        if not ai_service or not ai_service.vision:
            return jsonify({'success': False, 'error': 'Vision service not available'})
        
        analysis = ai_service.analyze_vision("What is on my screen? Describe everything you see.")
        
        if analysis:
            add_notification('Screen Analysis', analysis[:100] + '...', 'ai')
            return jsonify({'success': True, 'result': analysis})
        else:
            return jsonify({'success': False, 'error': 'Screen analysis failed'})
            
    except Exception as e:
        add_notification('Screen Error', str(e), 'error')
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/get_stats')
def get_stats():
    """Get local AI statistics"""
    try:
        if ai_service and ai_service.is_available():
            stats = ai_service.get_statistics()
            return jsonify({'success': True, 'stats': stats})
        else:
            return jsonify({'success': True, 'stats': {"total": 0, "local_commands": 0, "vision_commands": 0}})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/get_tasks')
def get_tasks():
    """Get current tasks"""
    try:
        if ai_service:
            tasks = ai_service.get_tasks()
            return jsonify({'success': True, 'tasks': tasks})
        else:
            return jsonify({'success': True, 'tasks': []})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/add_task', methods=['POST'])
def add_task():
    """Add a new task"""
    try:
        data = request.json
        description = data.get('description', '')
        priority = data.get('priority', 'medium')
        
        if not description:
            return jsonify({'success': False, 'error': 'No task description provided'})
        
        if ai_service and ai_service.add_task(description, priority):
            add_notification('Task Added', f'{description} ({priority})', 'success')
            return jsonify({'success': True, 'message': 'Task added successfully'})
        else:
            return jsonify({'success': False, 'error': 'Failed to add task'})
            
    except Exception as e:
        add_notification('Task Error', str(e), 'error')
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/voice_command', methods=['POST'])
def voice_command():
    """Process voice command"""
    try:
        if not ai_service or not ai_service.voice:
            return jsonify({'success': False, 'error': 'Voice service not available'})
        
        result = ai_service.process_voice_command()
        if result:
            command, response = result
            add_notification('Voice Command', f'Heard: {command}', 'info')
            add_notification('AI Response', f'{response[:50]}...', 'ai')
            return jsonify({'success': True, 'command': command, 'response': response})
        else:
            return jsonify({'success': False, 'error': 'No speech detected'})
            
    except Exception as e:
        add_notification('Voice Error', str(e), 'error')
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/get_notifications')
def get_notifications():
    """Get recent notifications"""
    return jsonify({'notifications': notifications[-20:]})

@app.route('/api/status')
def get_status():
    """Get system status"""
    # Update system status
    if ai_service:
        ai_stats = ai_service.get_status()
        system_status.update({
            "ai_processing": ai_stats.get('processing', False),
            "ai_available": ai_stats.get('model_available', False),
            "local_model": ai_stats.get('model_name', 'N/A')
        })
    
    return jsonify({'status': system_status})

def run_server():
    """Run the HUD server"""
    print("=== Cloud Cowork HUD Server - Local Only ===")
    print("Starting modern JARVIS interface with local Ollama models...")
    print(f"Local AI: {'Available' if LOCAL_AI_AVAILABLE else 'Unavailable'}")
    print(f"Vision System: {'Available' if VISION_AVAILABLE else 'Unavailable'}")
    print(f"Automation: {'Available' if AUTOMATION_AVAILABLE else 'Unavailable'}")
    
    if ai_service:
        status = ai_service.get_status()
        print(f"Local Model: {status.get('model_name', 'N/A')}")
        print(f"Vision Model: {status.get('vision_model', 'N/A')}")
        print(f"Voice Available: {status.get('voice_available', False)}")
    
    print("================================")
    print("HUD available at: http://localhost:3000")
    print("Press Ctrl+C to stop the server")
    
    # Add initial notification
    add_notification('System', 'Cloud Cowork HUD initialized with local Ollama models', 'success')
    
    # Run the server
    app.run(host='0.0.0.0', port=3000, debug=False)

if __name__ == '__main__':
    run_server()
