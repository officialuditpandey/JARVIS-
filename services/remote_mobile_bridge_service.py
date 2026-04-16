#!/usr/bin/env python3
"""
Remote Mobile Bridge Service for JARVIS - Feature 15
Webhook for phone-triggered desktop features (WhatsApp/Telegram)
"""

import os
import sys
import time
import threading
import json
import queue
from datetime import datetime
from typing import Dict, Any, List, Optional
import subprocess
import requests
from flask import Flask, request, jsonify
import uuid

# Add JARVIS backend path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from flask import Flask, request, jsonify
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    print("Flask not available - Installing...")
    os.system("pip install flask")
    try:
        from flask import Flask, request, jsonify
        FLASK_AVAILABLE = True
    except ImportError:
        FLASK_AVAILABLE = False

class RemoteMobileBridgeService:
    """Remote Mobile Bridge service for phone-triggered desktop features"""
    
    def __init__(self):
        self.is_active = False
        self.webhook_server = None
        self.server_thread = None
        self.command_queue = queue.Queue()
        self.active_commands = {}
        self.command_history = []
        
        # Webhook configuration
        self.webhook_port = 5000
        self.webhook_host = '0.0.0.0'  # Listen on all interfaces
        self.webhook_url = None
        self.secret_token = self._generate_secret_token()
        
        # Mobile integration
        self.supported_platforms = ['whatsapp', 'telegram', 'sms', 'webhook']
        self.mobile_commands = {
            'whatsapp': {
                'send_message': self._handle_whatsapp_message,
                'get_status': self._handle_whatsapp_status,
                'trigger_command': self._handle_whatsapp_trigger
            },
            'telegram': {
                'send_message': self._handle_telegram_message,
                'get_status': self._handle_telegram_status,
                'trigger_command': self._handle_telegram_trigger
            },
            'webhook': {
                'execute_command': self._handle_webhook_command,
                'get_status': self._handle_webhook_status,
                'trigger_feature': self._handle_webhook_trigger,
                'calendar_query': self._handle_calendar_query
            }
        }
        
        # Security
        self.allowed_senders = set()  # Whitelist of authorized senders
        self.rate_limits = {}  # Rate limiting per sender
        
        # Initialize
        self._initialize_bridge()
        
        print("Remote Mobile Bridge Service initialized")
    
    def _generate_secret_token(self) -> str:
        """Generate secret token for webhook security"""
        import secrets
        return secrets.token_urlsafe(32)
    
    def _initialize_bridge(self):
        """Initialize the mobile bridge"""
        try:
            if not FLASK_AVAILABLE:
                print("Flask not available - webhook server cannot start")
                return
            
            # Create Flask app
            self.webhook_server = Flask(__name__)
            self.webhook_server.config['SECRET_KEY'] = self.secret_token
            
            # Setup webhook endpoints
            self._setup_webhook_endpoints()
            
            # Start webhook server
            self._start_webhook_server()
            
            print("Remote Mobile Bridge initialized successfully")
            
        except Exception as e:
            print(f"Mobile bridge initialization failed: {e}")
    
    def _setup_webhook_endpoints(self):
        """Setup webhook endpoints for mobile access"""
        
        @self.webhook_server.route('/webhook', methods=['POST'])
        def handle_webhook():
            """Main webhook endpoint for mobile commands"""
            try:
                # Verify request
                if not self._verify_request(request):
                    return jsonify({'error': 'Unauthorized'}), 401
                
                # Parse request data
                data = request.get_json()
                if not data:
                    return jsonify({'error': 'No data provided'}), 400
                
                # Process command
                result = self._process_mobile_command(data)
                
                return jsonify(result)
                
            except Exception as e:
                return jsonify({'error': f'Webhook processing failed: {str(e)}'}), 500
        
        @self.webhook_server.route('/webhook/whatsapp', methods=['POST'])
        def handle_whatsapp():
            """WhatsApp webhook endpoint"""
            try:
                data = request.get_json()
                result = self._process_whatsapp_webhook(data)
                return jsonify(result)
            except Exception as e:
                return jsonify({'error': f'WhatsApp webhook failed: {str(e)}'}), 500
        
        @self.webhook_server.route('/webhook/telegram', methods=['POST'])
        def handle_telegram():
            """Telegram webhook endpoint"""
            try:
                data = request.get_json()
                result = self._process_telegram_webhook(data)
                return jsonify(result)
            except Exception as e:
                return jsonify({'error': f'Telegram webhook failed: {str(e)}'}), 500
        
        @self.webhook_server.route('/status', methods=['GET'])
        def get_status():
            """Get bridge status"""
            return jsonify(self.get_bridge_status())
        
        @self.webhook_server.route('/health', methods=['GET'])
        def health_check():
            """Health check endpoint"""
            return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})
    
    def _verify_request(self, request) -> bool:
        """Verify webhook request for security"""
        try:
            # Check for secret token in headers
            token = request.headers.get('X-Auth-Token')
            if token != self.secret_token:
                return False
            
            # Check rate limiting
            sender_ip = request.remote_addr
            current_time = time.time()
            
            if sender_ip in self.rate_limits:
                last_request = self.rate_limits[sender_ip]
                if current_time - last_request < 1:  # 1 request per second max
                    return False
            
            self.rate_limits[sender_ip] = current_time
            return True
            
        except:
            return False
    
    def _process_mobile_command(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process mobile command from webhook"""
        try:
            platform = data.get('platform', 'webhook')
            command = data.get('command', '')
            params = data.get('params', {})
            sender = data.get('sender', 'unknown')
            
            # Validate platform
            if platform not in self.supported_platforms:
                return {
                    'success': False,
                    'error': f'Unsupported platform: {platform}'
                }
            
            # Generate command ID
            command_id = str(uuid.uuid4())
            
            # Create command record
            command_record = {
                'id': command_id,
                'platform': platform,
                'command': command,
                'params': params,
                'sender': sender,
                'timestamp': datetime.now().isoformat(),
                'status': 'processing'
            }
            
            self.active_commands[command_id] = command_record
            
            # Execute command
            if platform in self.mobile_commands and command in self.mobile_commands[platform]:
                handler = self.mobile_commands[platform][command]
                result = handler(params)
                
                command_record['result'] = result
                command_record['status'] = 'completed'
                command_record['completed_at'] = datetime.now().isoformat()
                
                # Move to history
                self.command_history.append(command_record.copy())
                if len(self.command_history) > 100:
                    self.command_history = self.command_history[-100:]
                
                # Remove from active
                if command_id in self.active_commands:
                    del self.active_commands[command_id]
                
                return result
            else:
                return {
                    'success': False,
                    'error': f'Unknown command: {command} for platform: {platform}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Command processing failed: {str(e)}'
            }
    
    def _process_whatsapp_webhook(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process WhatsApp webhook data"""
        try:
            # Extract message from WhatsApp webhook format
            message = data.get('message', '')
            sender = data.get('sender', '')
            
            # Parse command from message
            if message.startswith('/'):
                command_parts = message[1:].split(' ', 1)
                command = command_parts[0]
                params = command_parts[1] if len(command_parts) > 1 else ''
                
                # Process as mobile command
                return self._process_mobile_command({
                    'platform': 'whatsapp',
                    'command': command,
                    'params': {'message': params},
                    'sender': sender
                })
            
            return {
                'success': True,
                'message': 'Message received (not a command)'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'WhatsApp webhook processing failed: {str(e)}'
            }
    
    def _process_telegram_webhook(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process Telegram webhook data"""
        try:
            # Extract message from Telegram webhook format
            message_data = data.get('message', {})
            message = message_data.get('text', '')
            sender = str(message_data.get('from', {}).get('id', ''))
            
            # Parse command from message
            if message.startswith('/'):
                command_parts = message[1:].split(' ', 1)
                command = command_parts[0]
                params = command_parts[1] if len(command_parts) > 1 else ''
                
                # Process as mobile command
                return self._process_mobile_command({
                    'platform': 'telegram',
                    'command': command,
                    'params': {'message': params},
                    'sender': sender
                })
            
            return {
                'success': True,
                'message': 'Message received (not a command)'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Telegram webhook processing failed: {str(e)}'
            }
    
    def _handle_whatsapp_message(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle WhatsApp message command"""
        try:
            message = params.get('message', '')
            recipient = params.get('recipient', '')
            
            # This would integrate with WhatsApp Business API
            # For now, simulate the operation
            print(f"WhatsApp message to {recipient}: {message}")
            
            return {
                'success': True,
                'message': 'WhatsApp message sent successfully',
                'recipient': recipient,
                'message_text': message
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'WhatsApp message failed: {str(e)}'
            }
    
    def _handle_whatsapp_status(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle WhatsApp status command"""
        try:
            return {
                'success': True,
                'status': 'WhatsApp bridge active',
                'webhook_url': self.webhook_url,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'WhatsApp status failed: {str(e)}'
            }
    
    def _handle_whatsapp_trigger(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle WhatsApp trigger command"""
        try:
            feature = params.get('feature', '')
            feature_params = params.get('params', {})
            
            # Trigger desktop feature
            result = self._trigger_desktop_feature(feature, feature_params)
            
            return {
                'success': True,
                'message': f'WhatsApp trigger for {feature} executed',
                'result': result
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'WhatsApp trigger failed: {str(e)}'
            }
    
    def _handle_telegram_message(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Telegram message command"""
        try:
            message = params.get('message', '')
            chat_id = params.get('chat_id', '')
            
            # This would integrate with Telegram Bot API
            # For now, simulate the operation
            print(f"Telegram message to {chat_id}: {message}")
            
            return {
                'success': True,
                'message': 'Telegram message sent successfully',
                'chat_id': chat_id,
                'message_text': message
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Telegram message failed: {str(e)}'
            }
    
    def _handle_telegram_status(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Telegram status command"""
        try:
            return {
                'success': True,
                'status': 'Telegram bridge active',
                'webhook_url': self.webhook_url,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Telegram status failed: {str(e)}'
            }
    
    def _handle_telegram_trigger(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Telegram trigger command"""
        try:
            feature = params.get('feature', '')
            feature_params = params.get('params', {})
            
            # Trigger desktop feature
            result = self._trigger_desktop_feature(feature, feature_params)
            
            return {
                'success': True,
                'message': f'Telegram trigger for {feature} executed',
                'result': result
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Telegram trigger failed: {str(e)}'
            }
    
    def _handle_webhook_command(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle webhook command"""
        try:
            command = params.get('command', '')
            args = params.get('args', [])
            
            # Execute command via system
            if command:
                result = subprocess.run(
                    [command] + args,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                return {
                    'success': result.returncode == 0,
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'return_code': result.returncode
                }
            else:
                return {
                    'success': False,
                    'error': 'No command provided'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Webhook command failed: {str(e)}'
            }
    
    def _handle_webhook_status(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle webhook status command"""
        try:
            return self.get_bridge_status()
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Webhook status failed: {str(e)}'
            }
    
    def _handle_webhook_trigger(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle webhook trigger command"""
        try:
            feature = params.get('feature', '')
            feature_params = params.get('params', {})
            
            # Trigger desktop feature
            result = self._trigger_desktop_feature(feature, feature_params)
            
            return {
                'success': True,
                'message': f'Webhook trigger for {feature} executed',
                'result': result
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Webhook trigger failed: {str(e)}'
            }
    
    def _handle_calendar_query(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle calendar query from mobile device"""
        try:
            # Import cloud sync service if available
            try:
                sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
                from services.cloud_sync_service import CloudSyncService
                cloud_sync = CloudSyncService()
                
                if not cloud_sync.is_active or not cloud_sync.calendar_service:
                    return {
                        'success': False,
                        'error': 'Calendar service not available',
                        'timestamp': datetime.now().isoformat()
                    }
                
                # Get calendar query parameters
                query_type = params.get('type', 'upcoming')  # upcoming, today, week
                limit = params.get('limit', 5)
                
                # Fetch calendar events
                from datetime import datetime, timedelta
                now = datetime.utcnow().isoformat() + 'Z'
                
                if query_type == 'today':
                    # Get today's events
                    start_of_day = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
                    end_of_day = start_of_day + timedelta(days=1)
                    
                    results = cloud_sync.calendar_service.events().list(
                        calendarId='primary',
                        timeMin=start_of_day.isoformat() + 'Z',
                        timeMax=end_of_day.isoformat() + 'Z',
                        maxResults=limit,
                        singleEvents=True,
                        orderBy='startTime'
                    ).execute()
                    
                elif query_type == 'upcoming':
                    # Get upcoming events
                    results = cloud_sync.calendar_service.events().list(
                        calendarId='primary',
                        timeMin=now,
                        maxResults=limit,
                        singleEvents=True,
                        orderBy='startTime'
                    ).execute()
                    
                elif query_type == 'week':
                    # Get this week's events
                    end_of_week = datetime.utcnow() + timedelta(days=7)
                    results = cloud_sync.calendar_service.events().list(
                        calendarId='primary',
                        timeMin=now,
                        timeMax=end_of_week.isoformat() + 'Z',
                        maxResults=limit,
                        singleEvents=True,
                        orderBy='startTime'
                    ).execute()
                    
                else:
                    return {
                        'success': False,
                        'error': f'Invalid query type: {query_type}',
                        'timestamp': datetime.now().isoformat()
                    }
                
                # Format events for mobile response
                events = results.get('items', [])
                formatted_events = []
                
                for event in events:
                    formatted_event = {
                        'title': event.get('summary', 'No title'),
                        'start': event.get('start', {}).get('dateTime', event.get('start', {}).get('date', 'Unknown')),
                        'end': event.get('end', {}).get('dateTime', event.get('end', {}).get('date', 'Unknown')),
                        'location': event.get('location', 'No location'),
                        'description': event.get('description', '')
                    }
                    formatted_events.append(formatted_event)
                
                return {
                    'success': True,
                    'status': f'Calendar query successful: {len(events)} events found',
                    'events': formatted_events,
                    'query_type': query_type,
                    'timestamp': datetime.now().isoformat()
                }
                
            except ImportError:
                return {
                    'success': False,
                    'error': 'Cloud sync service not available',
                    'timestamp': datetime.now().isoformat()
                }
            except Exception as e:
                return {
                    'success': False,
                    'error': f'Calendar query failed: {str(e)}',
                    'timestamp': datetime.now().isoformat()
                }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Calendar query handler failed: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    def _trigger_desktop_feature(self, feature: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger desktop feature"""
        try:
            # Import and use JARVIS services
            if 'services' in globals():
                if feature == 'camera' and 'visual_solver' in services:
                    # Trigger visual analysis
                    result = services['visual_solver'].solve_visual_problem()
                    return result
                
                elif feature == 'music' and 'native_media' in services:
                    # Control music
                    action = params.get('action', 'play')
                    if action == 'play':
                        result = services['native_media'].play_media('default')
                    elif action == 'stop':
                        result = services['native_media'].stop_media()
                    elif action == 'pause':
                        result = services['native_media'].pause_media()
                    else:
                        result = {'success': False, 'error': f'Unknown action: {action}'}
                    return result
                
                elif feature == 'system' and 'god_mode' in services:
                    # System control
                    command = params.get('command', '')
                    if command:
                        result = services['god_mode'].execute_terminal_command(command)
                        return result
                
                elif feature == 'status':
                    # Get system status
                    if 'god_mode' in services:
                        return services['god_mode'].get_system_status()
            
            return {
                'success': False,
                'error': f'Feature {feature} not available or no services found'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Feature trigger failed: {str(e)}'
            }
    
    def _start_webhook_server(self):
        """Start webhook server in background thread"""
        try:
            self.server_thread = threading.Thread(
                target=self._run_webhook_server,
                daemon=True
            )
            self.server_thread.start()
            
            # Wait for server to start
            time.sleep(2)
            
            # Set webhook URL
            self.webhook_url = f"http://{self.webhook_host}:{self.webhook_port}/webhook"
            
            print(f"Webhook server started at {self.webhook_url}")
            print(f"Secret token: {self.secret_token}")
            
        except Exception as e:
            print(f"Failed to start webhook server: {e}")
    
    def _run_webhook_server(self):
        """Run webhook server"""
        try:
            self.is_active = True
            self.webhook_server.run(
                host=self.webhook_host,
                port=self.webhook_port,
                debug=False,
                use_reloader=False
            )
        except Exception as e:
            print(f"Webhook server error: {e}")
        finally:
            self.is_active = False
    
    def add_allowed_sender(self, sender: str):
        """Add sender to whitelist"""
        self.allowed_senders.add(sender)
        print(f"Added sender to whitelist: {sender}")
    
    def remove_allowed_sender(self, sender: str):
        """Remove sender from whitelist"""
        self.allowed_senders.discard(sender)
        print(f"Removed sender from whitelist: {sender}")
    
    def get_webhook_url(self) -> str:
        """Get webhook URL for configuration"""
        return self.webhook_url
    
    def get_secret_token(self) -> str:
        """Get secret token for authentication"""
        return self.secret_token
    
    def get_bridge_status(self) -> Dict[str, Any]:
        """Get bridge status"""
        return {
            'is_active': self.is_active,
            'webhook_url': self.webhook_url,
            'webhook_port': self.webhook_port,
            'supported_platforms': self.supported_platforms,
            'active_commands': len(self.active_commands),
            'command_history_count': len(self.command_history),
            'allowed_senders': len(self.allowed_senders),
            'last_updated': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get service status"""
        return {
            'is_active': self.is_active,
            'webhook_server_running': self.webhook_server is not None,
            'webhook_url': self.webhook_url,
            'supported_platforms': self.supported_platforms,
            'active_commands': len(self.active_commands),
            'command_history_count': len(self.command_history),
            'last_updated': datetime.now().isoformat()
        }

    def process_mobile_command(self, data):
        return {'success': True, 'command': data.get('command', '')}
